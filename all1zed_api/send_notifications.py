from rest_framework import Response
import requests
import os

headers = {
    'Content-Type': 'application/json'
}

def send_notification(phone_number, msg):
    phone_number_format = f"26{phone_number}"
    payload = {
        "username": os.environ.get('PROBASE_USERNAME'),
        "username": os.environ.get('PROBASE_PASSWORD'),
        "recipient": [phone_number_format],
        "senderid": os.environ.get('PROBASE_SENDER_ID'),
        "message": f'{msg}',
        "source": os.environ.get('PROBASE_SOURCE'),
        "msg_ref": os.environ.get('PROBASE_MSG_REF'),
    }

    try:
        response = requests.post(f"{os.environ.get('PROBASE_URL')}", json=payload, headers=headers)
    except Exception as e:
        return Response({'Error': 'An error occured while sending the message'})
    return response
