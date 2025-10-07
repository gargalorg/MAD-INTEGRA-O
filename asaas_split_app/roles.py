# roles.py
ROLES = {
    "Admin": {"commission": 0.0, "value": 0, "wallet_key": "WALLET_SYSTEM"},
    "Parceiro": {"commission": 20.0, "value": 0, "wallet_key": "WALLET_PARCEIRO"},
    "Agência Premium": {"commission": 12.0, "value": 3000, "wallet_key": "WALLET_AGENCIA"},
    "Autoridade": {"commission": 8.0, "value": 2000, "wallet_key": "WALLET_AUTORIDADE"},
    "Impacto": {"commission": 8.0, "value": 850, "wallet_key": "WALLET_IMPACTO"},
    "Premium": {"commission": 5.0, "value": 1000, "wallet_key": "WALLET_PREMIUM"},
    "Jornalista": {"commission": 5.0, "value": 500, "wallet_key": "WALLET_JORNALISTA"},
    "Start": {"commission": 2.0, "value": 0, "wallet_key": "WALLET_START"},
}
