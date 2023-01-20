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
    nfs_zamtel_cashin_confirm, nfs_zanaco_cashin,
    nfs_zanaco_cashin_confirm,
)
from all1zed_api.send_notifications import send_notification



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
                        receiver = CardAccount.objects.get(card_number=receiver_card_number)
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
#                            card_number=sender.card_number,
#                            txn_type='transfer',
                            account_type=account_type,
                            txn_amount=amount,                      
                            update_amount=sender.card_balance,             
                            reference_id=txn_id,
                            message=f'Transfer of {amount} to {receiver.card_number} successful',
                            status= True
                        ) 

                        Transaction.objects.create(
#                            card_number=card_number,
#                            txn_type='transfer',
                            account_type=account_type,
                            txn_amount=amount,                      
                            update_amount=receiver.card_balance,             
                            reference_id=txn_id,
                            message=f'You received {amount} from {sender.card_number}.',
                            status= True
                        ) 

                        verification_msg  = f'Dear customer, you have sent ZMW{amount} to {receiver.first_name} {receiver.first_name} card account number {receiver_card_number}. Your card balance is now ZMW{sender.card_balance}. Txn ID: {txn_id}'
                        notification_msg = f'Dear customer, you have received ZMW{amount} from {sender.first_name} {sender.first_name} {sender.phone_number}. Your card balance is now ZMW{receiver.card_balance}'

                        send_notification(receiver.phone_number, notification_msg)
                        send_notification(sender.phone_number, verification_msg)
                        return Response({'Success': 'OK'})
                    return Response({"Error": serializer.errors})

                elif account_type == 'mobile_money':
                    institution_name = request.data.get('institution_name', None)
                    
                    if institution_name == 'mtn':
                        momo_status = nfs_momo_cashin(amount, reference, login_session)
                        try:
                            if momo_status.get("response_code") == '0':
                                print(f'MTN-APPROVAL-REPRINT {momo_status.get("response_code")}')
                                confirmation_number = momo_status.get('confirmation_number')
                                print(confirmation_number)
                                confirm_response = nfs_momo_cashin_confirm(confirmation_number, login_session)
                                sender.card_balance -= float(amount)
                                sender.save()

                                Transaction.objects.create(
#                                    card_number=card_number,
#                                    txn_type='cashin',
                                    account_type=account_type,
                                    institution_name=institution_name,
                                    txn_amount=amount,                      
                                    update_amount=sender.card_balance,             
#                                    reference_id=txn_id,
                                    message=f'Transfer of {amount} to {reference} successful',
                                    status= True
                                ) 
                                verification_msg  = f'Dear customer, you have transfered ZMW{amount} to {reference}. Your card balance is now ZMW{sender.card_balance}.'       
                                send_notification(sender.phone_number, verification_msg)
                                print(f'APPROVAL-CONFIRM {confirm_response}')

                                return Response({'Success':'OK', 'Data': serializer.data})
                            return Response({'Error': True})
                        except (KeyError, TypeError) as e:
                            pass

                    elif institution_name == 'airtel':
                        momo_status = nfs_airtel_cashin(amount, reference, login_session)
                        try:
                            if momo_status.get("response_code") == '0':
                                print(f'MTN-APPROVAL-REPRINT {momo_status.get("response_code")}')
                                confirmation_number = momo_status.get('confirmation_number')
                                print(confirmation_number)
                                confirm_response = nfs_airtel_cashin_confirm(confirmation_number, login_session)
                                sender.card_balance -= float(amount)
                                sender.save()
                                
                                Transaction.objects.create(
                                    card_number=card_number,
                                    txn_type='cashin',
                                    account_type=account_type,
                                    institution_name=institution_name,
                                    txn_amount=amount,                      
                                    update_amount=sender.card_balance,             
                                    reference_id=txn_id,
                                    message=f'Transfer of {amount} to {reference} successful',
                                    status= True
                                ) 
                                verification_msg  = f'Dear customer, you have transfered ZMW{amount} to {reference}. Your card balance is now ZMW{sender.card_balance}. Txn ID: {txn_id}'
                                send_notification(sender.phone_number, verification_msg)
                                print(f'Airtel-CONFIRM {confirm_response}')

                                return Response({"Success": serializer.data, "Message": "Transfer successful."})
                            return Response({'Error': True})
                        except (KeyError, TypeError) as e:
                            pass
                    
                    elif institution_name == 'zamtel':
                        momo_status = nfs_zamtel_cashin(amount, reference, login_session)
                        try:
                            if momo_status.get("response_code") == '0':
                                print(f'MTN-APPROVAL-REPRINT {momo_status.get("response_code")}')
                                confirmation_number = momo_status.get('confirmation_number')
                                print(confirmation_number)
                                confirm_response = nfs_zamtel_cashin_confirm(confirmation_number, login_session)
                                sender.card_balance -= float(amount)
                                sender.save()

                                Transaction.objects.create(
                                    card_number=card_number,
                                    txn_type='cashin',
                                    account_type=account_type,
                                    institution_name=institution_name,
                                    txn_amount=amount,                      
                                    update_amount=sender.card_balance,             
                                    reference_id=txn_id,
                                    message=f'Transfer of {amount} to {reference} successful',
                                    status= True
                                ) 
                                verification_msg  = f'Dear customer, you have transfered ZMW{amount} to {reference}. Your card balance is now ZMW{sender.card_balance}. Txn ID: {txn_id}'
                                send_notification(sender.phone_number, verification_msg)
                                print(f'Airtel-CONFIRM {confirm_response}')

                                return Response({"Success": serializer.data, "Message": "Transfer successful."})
                            return Response({'Error': True})
                        except (KeyError, TypeError) as e:
                            pass
                    else:
                        return Response({'Error': 'Please enter a valid institution name'})

                elif account_type == 'bank':
                    bank_name = request.data.get('bank_name', None).lower()

                    if bank_name == 'zanaco':
                        account_number = request.data.get('account_number', None).lower()
                        reference = account_number
                        
                        try:
                            disbursment = nfs_zanaco_cashin(f'{amount}', reference, login_session)
                            if disbursment.get("response_code") == '0':
                                confirmation_number = disbursment.get('confirmation_number')
                                confirm_response = nfs_zanaco_cashin_confirm(confirmation_number, login_session)
                                sender.card_balance -= float(amount)
                                sender.save()
                                txn_id = generate_pin(12)
                                print(f'Zanaco-CONFIRM {confirm_response}')

                                Transaction.objects.create(
#                                    card_number=card_number,
#                                    txn_type='cashin',
                                    account_type=account_type,
                                    institution_name=bank_name,
                                    txn_amount=amount,                      
                                    update_amount=sender.card_balance,             
                                    reference_id=txn_id,
                                    message=f'Transfer of {amount} to {reference} - {bank_name} successful',
                                    status= True
                                )   
                            
                                notification_msg = f'Dear customer, you have successfully transfered ZMW{amount} to {reference}. Your balance is now {sender.card_balance} Transaction ID: {txn_id}.'
                                send_notification(sender.phone_number, notification_msg)
                                
                                return Response({'Success': 'OK', 'Details': serializer.data})
                            return Response({'Error': True})
                        except (KeyError, TypeError) as e:
                            pass
                        
                    return Response({"Error": 'Please enter a valid bank name.'})
                return Response({"Error": 'Unknown account type'})
            return Response({'Error': 'Unknown phone number'})
        return Response({'Error': serializer.errors})
