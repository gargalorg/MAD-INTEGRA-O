# app.py
import os
from flask import Flask, request, jsonify
from config import Config
from models import db, User
from asaas_client import create_customer, create_payment
from roles import ROLES
from werkzeug.exceptions import BadRequest

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/register", methods=["POST"])
    def register():
        """
        Body expected:
        {
          "name": "...",
          "email": "...",
          "password": "...",
          "role": "Parceiro",
          "cpfCnpj": "..."
        }
        """
        data = request.get_json()
        if not data:
            raise BadRequest("JSON body required")

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "Start")
        cpf = data.get("cpfCnpj", None)

        if not all([name, email, password]):
            return jsonify({"error": "name, email e password são obrigatórios"}), 400

        if role not in ROLES:
            return jsonify({"error": f"role inválida. Roles válidas: {list(ROLES.keys())}"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email já cadastrado"}), 400

        user = User(name=name, email=email, role=role)
        user.set_password(password)

        # cria customer no Asaas
        try:
            cust_payload = {"name": name, "email": email}
            if cpf:
                cust_payload["cpfCnpj"] = cpf
            cust_resp = create_customer(cust_payload)
            user.asaas_customer_id = cust_resp.get("id")
        except Exception as e:
            # opcional: log
            return jsonify({"error": "Erro ao criar customer no Asaas", "detail": str(e)}), 500

        # persiste usuário antes de gerar cobrança
        db.session.add(user)
        db.session.commit()

        # cria cobrança de assinatura se value > 0 (conforme roles)
        role_meta = ROLES[role]
        plan_value = role_meta.get("value", 0)
        commission = role_meta.get("commission", 0.0)

        payment_resp = None
        try:
            if plan_value and plan_value > 0:
                # monta split: comissão para parceiro, resto para wallet system (sua conta)
                # pega wallet ids do env (roles.py tem a chave wallet_key)
                partner_wallet_env_key = role_meta.get("wallet_key")
                partner_wallet = os.getenv(partner_wallet_env_key) if partner_wallet_env_key else None
                system_wallet = os.getenv("WALLET_SYSTEM")

                splits = []
                if commission and partner_wallet:
                    splits.append({
                        "walletId": partner_wallet,
                        "percentualValue": commission
                    })
                # (opcional) você pode adicionar split para sistema se quiser explícito
                # criar payload
                payment_payload = {
                    "customer": user.asaas_customer_id,
                    "value": float(plan_value),
                    "dueDate": "2099-12-31",   # para teste, ou gere data dinâmica
                    "description": f"Plano {role}",
                    "billingType": "PIX"
                }
                if splits:
                    payment_payload["split"] = splits

                payment_resp = create_payment(payment_payload)
        except Exception as e:
            # Não removemos o usuário; apenas reportamos erro na cobrança
            return jsonify({
                "user": {"id": user.id, "email": user.email},
                "error": "Erro ao criar cobrança no Asaas",
                "detail": str(e)
            }), 500

        return jsonify({
            "user": {"id": user.id, "email": user.email, "role": user.role},
            "asaas_customer_id": user.asaas_customer_id,
            "payment": payment_resp
        }), 201

    @app.route("/create_charge", methods=["POST"])
    def create_charge_endpoint():
        """
        Endpoint genérico para criar cobrança:
        Body:
        {
          "customer_id": "...",  # ou "email" + payer info
          "value": 150.00,
          "dueDate": "2025-10-10",
          "description": "Venda X",
          "splits": [ { "walletId": "...", "fixedValue": 30.0 } ]
        }
        """
        data = request.get_json()
        if not data:
            raise BadRequest("JSON body required")

        try:
            payload = {
                "customer": data.get("customer_id") or data.get("customer"),
                "value": float(data["value"]),
                "dueDate": data["dueDate"],
                "description": data.get("description", ""),
                "billingType": data.get("billingType", "PIX")
            }
        except Exception:
            return jsonify({"error": "body inválido"}), 400

        if data.get("splits"):
            payload["split"] = data.get("splits")

        try:
            resp = create_payment(payload)
            return jsonify(resp), 201
        except Exception as e:
            return jsonify({"error": "Erro ao criar pagamento", "detail": str(e)}), 500

    @app.route("/webhook", methods=["POST"])
    def webhook():
        """
        Recebe eventos do Asaas. Apenas grava o body/raw para processar.
        Você deve validar IP / assinaturas se precisar de segurança.
        """
        body = request.get_json(silent=True)
        # exemplo: {"event": "PAYMENT_RECEIVED", "payment": {...}}
        # Aqui você atualizaria registros no DB conforme necessário.
        # Para demo, apenas logamos e retornamos 200.
        print("Webhook recebido:", body)
        return jsonify({"ok": True}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
