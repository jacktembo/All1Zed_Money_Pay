from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import string
import random
import requests
import json
import secrets
import os


current_date = datetime.now()
time_stamp = current_date
digits = string.digits
req_ref = "".join(secrets.choice(digits) for i in range(6))

headers = {
    'Content-Type': 'application/json'
    }

def generate_pin(size=6, char=string.digits):
    return ''.join(random.choice(char) for x in range(size))
 

def login():
    auth_data = {
        'username': os.environ.get('PROD_USERNAME'),
        'password': os.environ.get('PROD_PASSWORD'),
        'channel': os.environ.get('CHANNEL')
    }

    params = {
        'username': os.environ.get('PROD_USERNAME'),
        'password': os.environ.get('PROD_PASSWORD'),
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/authClient", params=params, json=auth_data, headers=headers)
    results = json.loads(response.text)
    print(results.get('session_uuid', None))
    return results.get('session_uuid', None)


def get_product_list(login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f"{generate_pin(8)}",
    }
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/productList", json=payload, headers=headers)
    results = json.loads(response.text)
    print(results)
    return results


def airtel_pay(phone_number,amount,login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f"{generate_pin(8)}",
        "product_id": "5392",
        "amount":  f"{amount}",
        "wallet_msisdn": f"{phone_number}"
    }

    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/airtelPayPayment", json=payload, headers=headers)
    results = json.loads(response.text)
    print(response.text)
    return results


def airtel_pay_confirm(phone_number, confirmation_number, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f"{generate_pin(8)}",
        "wallet_msisdn":f"{phone_number}",
        "product_id": "5392",
        "confirmation_number": f"{confirmation_number}"
    }

    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/airtelPayPaymentConfirm", json=payload, headers=headers)
    results = json.loads(response.text)
    print(results)
    return results


def airtel_pay_query(amount, phone_number, airtel_reference, login_session):
    payload = {
       "session_uuid": f"{login_session}",
       "request_reference": f"{generate_pin(8)}",
       "product_id": "5393",
       "amount":  amount,
       "wallet_msisdn": f"{phone_number}",
       "airtel_reference": f"{airtel_reference}"
    }

    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/airtelPayQuery", json=payload, headers=headers)
    results = json.loads(response.text)
    print(results)
    return results


def airtel_pay_query_confirm(confirmation_number, login_session):
    payload = {
       "session_uuid": f"{login_session}",
       "request_reference": f"{generate_pin(8)}",
       "product_id": "5393",
       "confirmation_number": f"{confirmation_number}"
    }

    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/airtelPayQueryConfirm", json=payload, headers=headers)
    results = json.loads(response.text)
    print(results)
    return results


def zamtel_pay(amount, msisdn, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "product_id": 5440,
        "msisdn": f"{msisdn}",
        "amount": amount,
    }

    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/zamtelMoneyPay", json=payload, headers=headers)
    results = json.loads(response.text)
    print(results)
    return results


def zamtel_pay_confirm(confirmation_number, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "product_id": 5440,
        "confirmation_number": f"{confirmation_number}"
    }

    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/zamtelMoneyPayConfirm", json=payload, headers=headers)
    results = json.loads(response.text)
    print(results)
    return results


def mtn_momo_pay(amount, wallet_msisdn, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": 5120,
        "wallet_msisdn": f"{wallet_msisdn}",
        "amount": amount,
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/mtnDebit", json=payload, headers=headers)
#    print(response.json())
#    return response.json()
    results = json.loads(response.text)
    print(f"MTN_DEBIT {results}")
    return results


def mtn_momo_pay_approval(amount, phone_number, supplier_transaction_id, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "product_id": "5121",
        "request_reference": f'{generate_pin(8)}',
        "amount":  amount,
        "wallet_msisdn": f"{phone_number}",
        "supplier_transaction_id": f"{supplier_transaction_id}"
    }

    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/mtnDebitApproval", json=payload, headers=headers)
    results = json.loads(response.text)
    print(f"MTN-APPROVAL {results}")
    return results


def mtn_momo_pay_confirm(confirmation_number, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": "5121",
        "confirmation_number": f"{confirmation_number}"
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/mtnDebitApprovalConfirm", json=payload, headers=headers)
    results = json.loads(response.text)
    print(f"MTN_DEBIT_CONFIRM {results}")
    return results
