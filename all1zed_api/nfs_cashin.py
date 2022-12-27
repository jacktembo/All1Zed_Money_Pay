from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
import string
import random
import requests
import json
import secrets
import os
from all1zed_api.momo_pay import generate_pin

current_date = datetime.now()
time_stamp = current_date
digits = string.digits
req_ref = "".join(secrets.choice(digits) for i in range(6))

headers = {
    'Content-Type': 'application/json'
    }


def nfs_airtel_cashin(amount, reference, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": "5308",
        "reference": f"{reference}",
        "amount": amount,
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/nfsCashIn", json=payload, headers=headers)
#    print(response.json())
#    return response.json()
    results = json.loads(response.text)
    print(f"NFS_AIRTEL_DEBIT {results}")
    return results


def nfs_airtel_cashin_confirm(confirmation_number, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": "5308",
        "confirmation_number": f"{confirmation_number}"
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/nfsCashinConfirm", json=payload, headers=headers)
    results = json.loads(response.text)
    print(f"DEBIT_CONFIRM {results}")
    return results


def nfs_momo_cashin(amount, reference, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": 5360,
        "reference": f"{reference}",
        "amount": amount,
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/nfsCashIn", json=payload, headers=headers)
#    print(response.json())
#    return response.json()
    results = json.loads(response.text)
    print(f"NFS_DEBIT {results}")
    print(response)
    return results


def nfs_momo_cashin_confirm(confirmation_number, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": 5360,
        "confirmation_number": f"{confirmation_number}"
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/nfsCashInConfirm", json=payload, headers=headers)
    results = json.loads(response.text)
    print(f"DEBIT_CONFIRM {results}")
    return results



def nfs_zamtel_cashin(amount, reference, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": "5305",
        "reference": f"{reference}",
        "amount": amount,
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/nfsCashIn", json=payload, headers=headers)
#    print(response.json())
#    return response.json()
    results = json.loads(response.text)
    print(f"NFS_DEBIT {results}")
    return results


def nfs_zamtel_cashin_confirm(confirmation_number, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": "5305",
        "confirmation_number": f"{confirmation_number}"
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/nfsCashInConfirm", json=payload, headers=headers)
    results = json.loads(response.text)
    print(f"DEBIT_CONFIRM {results}")
    return results


def nfs_zanaco_cashin(amount, reference, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": "5586",
        "reference": f"{reference}",
        "amount": amount,
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/nfsCashIn", json=payload, headers=headers)
#    print(response.json())
#    return response.json()
    print(f'{22}00')
    results = json.loads(response.text)
    print(f"NFS_DEBIT {results}")
    return results


def nfs_zanaco_cashin_confirm(confirmation_number, login_session):
    payload = {
        "session_uuid": f"{login_session}",
        "request_reference": f'{generate_pin(8)}',
        "product_id": "5586",
        "confirmation_number": f"{confirmation_number}"
    }
    
    response = requests.post(f"{os.environ.get('KAZANG_BASE_URL')}/nfsCashInConfirm", json=payload, headers=headers)
    results = json.loads(response.text)
    print(f"DEBIT_CONFIRM {results}")
    return results

