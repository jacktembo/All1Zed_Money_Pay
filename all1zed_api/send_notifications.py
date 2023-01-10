from rest_framework.response import Response
from all1zed_api.momo_pay import generate_pin
import requests
import os

headers = {
    'Content-Type': 'application/json'
}

def send_notification(phone_number, msg):
    phone_number_format = f"26{phone_number}"
    payload = {
        "username": os.environ.get('PROBASE_USERNAME'),
        "password": os.environ.get('PROBASE_PASSWORD'),
        "recipient": [phone_number_format],
        "senderid": os.environ.get('PROBASE_SENDER_ID'),
        "message": f'{msg}',
        "source": os.environ.get('PROBASE_SOURCE'),
        "msg_ref": f'{generate_pin(2)}',
    }

    try:   
        response = requests.post(f"{os.environ.get('PROBASE_URL')}", json=payload, headers=headers)
        results = response.text 
    except Exception as e:
        return Response({'Error': 'An error occured while sending the message'})
    return results
