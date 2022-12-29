from datetime import datetime, timedelta, date
from django.utils import timezone
from django.http import response
from rest_framework import status
#from rest_framework.generics import RetrieveAPIView, get_object_or_404, CreateAPIView, UpdateAPIView, ListAPIVIew
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.serializers import BusinessProfileSerializer
from authentication.serializers import UserSerializer, CardAccountSerializer
from all1zed_api.models import (
    CardAccount,
    BusinessAccount,
    Transaction, 
)
from authentication.models import (
    User, BusinessProfile, OrganizationProfile,
    LimitedCompanyProfile,
)
from all1zed_api.serializers import (
    BalanceSerializer,
    TransactionSerializer, BusinessAccountSerializer,
    BusinessProfileListSerializer,
)
from all1zed_api.momo_pay import generate_pin, login
from all1zed_api.nfs_cashin import (
    nfs_momo_cashin, 
    nfs_momo_cashin_confirm, nfs_airtel_cashin, 
    nfs_airtel_cashin_confirm, nfs_zamtel_cashin,
    nfs_zamtel_cashin_confirm,
)


login_session = login()

class CardDetails(APIView):
    '''
    Get card details before submitting a cashin request
    '''

    serializer_class = CardAccountSerializer

    def get(self, request, card_number, format=None):
        try:
            card_account = CardAccount.objects.get(card_number=card_number)
        except CardAccount.DoesNotExist:
            return Response({'Error': 'Invalid card number'})

        if card_account.is_active == True:
            response = CardAccountSerializer(card_account)
            return Response({'message': 'OK', 'Results': response.data}, status=status.HTTP_200_OK)


class CashinView(APIView):
    '''
    All1zed card user can tranfer money from their card a/c to another card or momo a/c
    '''
    serializer_class = CardAccountSerializer

    def get(self, request, format=None):
        serializer = CardAccountSerializer(data=request.data)

        if serializer.is_valid():
            card_number = request.data.get('card_card')
            
            try:
                card_account = CardAccount.objects.get(card_number=card_number)
            except CardAccount.DoesNotExist:
                return Response({'Error': 'No card account found'})
        return Response({'Error': serializer.errors})

    def post(self, request, format=None):
        serializer = BalanceSerializer(data=request.data)

        if serializer.is_valid():
            card_number = request.data.get('card_number', None)
            phone_number = request.data.get('phone_number', None)
            reference = request.data.get('reference', None)
            amount = request.data.get('amount', None)
            account_type = request.data.get('account_type', None).lower()
        
            try:
                sender = CardAccount.objects.get(card_number=card_number)
            except CardAccount.DoesNotExist:
                return Response({'Error': 'Card account not found'})

            if sender.phone_number == phone_number:
                if account_type == 'card':
                    receiver_card_number = request.data.get('receiver_card_number', None)
                    try:
                        receiver = CardAccount.objects.get(receiver_card_number=receiver_card_number)
                    except CardAccount.DoesNotExist:
                        return Response({'Error': 'Card account not found'})

                    if sender.card_balance < float(amount):
                        return Response({'Error': f'You have insufficient balance to make this tranfer of {amount}'})

                    sender.card_balance -= float(amount)
                    receiver.card_balance += float(amount)
                    sender.save()
                    receiver.save()

                    if sender and receiver:
                        txn_id = generate_pin()
                        Transaction.objects.create(
                            phone_number=phone_number,
                            card_number=card_number,
                            status=True,
                            reference_id=txn_id
                        )

                        verification_msg  = f'You have sent ZMW{amount} to {receiver.first_name} {receiver.first_name} card account number {receiver_card_number}. Your card balance is now ZMW{sender.card_balance}. Txn ID: {txn_id}'
                        notification_msg = f'You have received ZMW{amount} from {sender.first_name} {sender.first_name} {sender.phone_number}. Your card balance is now ZMW{receiver.card_balance}'

                        # send_message(receiver.phone_number, notification_msg)
                        # send_message(sender.phone_number, verification_msg)
                        return Response({'Success': 'OK'})
                    return Response({"Error": serializer.errors})

                elif account_type == 'mtn':
                    momo_status = nfs_momo_cashin(amount, reference, login_session)
                    try:
                        if momo_status.get("response_code") == '0':
                            print(f'MTN-APPROVAL-REPRINT {momo_status.get("response_code")}')
                            confirmation_number = momo_status.get('confirmation_number')
                            print(confirmation_number)
                            confirm_response = nfs_momo_cashin_confirm(confirmation_number, login_session)
                            sender.card_balance -= float(amount)
                            sender.save()
                            verification_msg  = f'You have transfered ZMW{amount} to {reference}. Your card balance is now ZMW{sender.card_balance}. Txn ID: {txn_id}'
                            # send_message(sender.phone_number, verification_msg)
                            print(f'APPROVAL-CONFIRM {confirm_response}')
                            return Response({'Success':'OK', 'Data': serializer.data})
                        return Response({'Error': True})
                    except (KeyError, TypeError) as e:
                        pass

                elif account_type == 'airtel':
                    momo_status = nfs_airtel_cashin(amount, reference, login_session)
                    try:
                        if momo_status.get("response_code") == '0':
                            print(f'MTN-APPROVAL-REPRINT {momo_status.get("response_code")}')
                            confirmation_number = momo_status.get('confirmation_number')
                            print(confirmation_number)
                            confirm_response = nfs_airtel_cashin_confirm(confirmation_number, login_session)
                            sender.card_balance -= float(amount)
                            sender.save()
                            verification_msg  = f'You have transfered ZMW{amount} to {reference}. Your card balance is now ZMW{sender.card_balance}. Txn ID: {txn_id}'
                            # send_message(sender.phone_number, verification_msg)
                            print(f'Airtel-CONFIRM {confirm_response}')
                            return Response({"Success": serializer.data, "Message": "Transfer successful."})

                        return Response({'Error': True})
                    except (KeyError, TypeError) as e:
                        pass
                
                elif account_type == 'zamtel':
                    momo_status = nfs_zamtel_cashin(amount, reference, login_session)
                    try:
                        if momo_status.get("response_code") == '0':
                            print(f'MTN-APPROVAL-REPRINT {momo_status.get("response_code")}')
                            confirmation_number = momo_status.get('confirmation_number')
                            print(confirmation_number)
                            confirm_response = nfs_zamtel_cashin_confirm(confirmation_number, login_session)
                            sender.card_balance -= float(amount)
                            sender.save()
                            verification_msg  = f'You have transfered ZMW{amount} to {reference}. Your card balance is now ZMW{sender.card_balance}. Txn ID: {txn_id}'
                            # send_message(sender.phone_number, verification_msg)
                            print(f'Airtel-CONFIRM {confirm_response}')
                            return Response({"Success": serializer.data, "Message": "Transfer successful."})

                        return Response({'Error': True})
                    except (KeyError, TypeError) as e:
                        pass
                    
                return Response({"Error": 'Unknown account type'})
    
        return Response({'Error': serializer.errors})




#{
#  "amount": "100",
#   "phone_number": "0976637416",
#   "account_reference": "0963533399",
#  "account_type": "mtn",
#   "session_uuid": "a529f7c9-9806-4533-86b3-53a68dbdb49c",
#   "card_number": "0022"
#}








