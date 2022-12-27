from ekamo_api.mtnmomo import collection, disbursement
import pyqrcode
import png
import string
import random
import os

client = collection.Collection({
    "COLLECTION_USER_ID": os.environ.get("COLLECTION_USER_ID"),
    "COLLECTION_API_SECRET": os.environ.get("COLLECTION_API_SECRET"),
    "COLLECTION_PRIMARY_KEY": os.environ.get("COLLECTION_PRIMARY_KEY"),
    })

def pin_generator(size=6, chars=string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def qrcode_gen(refference_id):
    ref = pyqrcode.create(refference_id)
    img = f"{refference_id}-ekamoeticket-qr-code.png"
    return ref.png(img, scale= 10)


def request_topay(mobile_number,amount):
    external_id = pin_generator(12)
    return client.requestToPay(mobile=mobile_number, amount=amount, external_id=external_id, payee_note="Testing Ekamo API", payer_message="Ekamo Wallet", currency="ZMW")

def get_status(transaction_id):
    return client.getTransactionStatus(str(transaction_id))

disbursement_client = disbursement.Disbursement({
    "DISBURSEMENT_USER_ID": os.environ.get("DISBURSEMENT_USER_ID"),
    "DISBURSEMENT_API_SECRET": os.environ.get("DISBURSEMENT_API_SECRET"),
    "DISBURSEMENT_PRIMARY_KEY": os.environ.get("DISBURSEMENT_PRIMARY_KEY"),
})

def request_transfer(mobile_number,amount):
    external_id = pin_generator(12)
    return disbursement_client.transfer(mobile=mobile_number, amount=amount, external_id=external_id, payee_note="Testing Ekamo API", payer_message="Ekamo Wallet", currency="ZMW")

def disbursment_get_status(transaction_id):
    return disbursement_client.getTransactionStatus(str(transaction_id))
    