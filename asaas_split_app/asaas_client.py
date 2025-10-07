# asaas_client.py
import requests
from flask import current_app
import os

def _headers():
    api_key = current_app.config.get("ASAAS_API_KEY")
    return {
        "Content-Type": "application/json",
        "access_token": api_key
    }

def create_customer(payload):
    """
    payload example:
    {
      "name": "Fulano",
      "email": "fulano@ex.com",
      "cpfCnpj": "00000000000",
      "phone": "11999999999"
    }
    """
    base = current_app.config.get("ASAAS_BASE_URL", "https://www.asaas.com/api/v3")
    url = f"{base}/customers"
    r = requests.post(url, json=payload, headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.json()

def create_payment(payload):
    """
    payload example:
    {
      "customer": "cus_123..",
      "value": 200.00,
      "dueDate": "2025-10-15",
      "description": "Plano X",
      "billingType": "PIX",
      "split": [ { "walletId": "...", "percentualValue": 10.0 } ]
    }
    """
    base = current_app.config.get("ASAAS_BASE_URL", "https://www.asaas.com/api/v3")
    url = f"{base}/payments"
    r = requests.post(url, json=payload, headers=_headers(), timeout=20)
    r.raise_for_status()
    return r.json()
