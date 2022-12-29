from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from all1zed_api.momo_pay import (
    login, airtel_pay, zamtel_pay_confirm,
    airtel_pay_confirm, airtel_pay_query,
    airtel_pay_query_confirm, zamtel_pay, 
    mtn_momo_pay, mtn_momo_pay_approval, 
    mtn_momo_pay_confirm, generate_pin,
  )
from all1zed_api.models import Transaction, CardAccount
from all1zed_api.serializers import BalanceSerializer


login_session = login()

class AirtelPayView(APIView):
    '''
    First request to prompt a user for approving a transaction
    '''
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        txn_amount = float(request.data.get('txn_amount'))

        all1zed_charge = (2/100) * float(txn_amount)
        total_bill = int(txn_amount) + int(all1zed_charge)
        
        try:
            response_body = airtel_pay(phone_number, f'{total_bill}', login_session)
            print(f"AIRTEL - airtel_pay {response_body}")
        except (KeyError, TypeError) as e:
            pass
        
        try:
            if "Please confirm" in response_body.get('confirmation_message', ''):
                confirm = airtel_pay_confirm(phone_number, response_body.get('confirmation_number', None), login_session)
                print(f"AIRTEL - airtel_pay_confirm {confirm}")
                wallet_msisdn = confirm.get('wallet_msisdn', None)
                airtel_reference = confirm.get('request_reference', None)
        except (KeyError, TypeError) as e:
            pass
    
        return Response({"success": "OK", "wallet_msisdn": f"{wallet_msisdn}", "airtel_reference": f"{airtel_reference}"})


class AirtelPayConfirmView(APIView):

    def post(self, request, *args, **kwargs):
        session_uuid = request.data.get('session_uuid')
        wallet_msisdn = request.data.get('wallet_msisdn')
        txn_amount = request.data.get('txn_amount')
        card_number = request.data.get('card_number', None)
        airtel_reference = request.data.get('airtel_reference', None)

        # Check if card is registered
        try: 
            card_account = CardAccount.objects.get(card_number=card_number)
            print(card_account)
        except CardAccount.DoesNotExist:
            return Response({'Error': 'Card not found'})
        
        try:
            if card_account.is_active == True:
                # Update card account balance 
                all1zed_charge = (2/100) * float(txn_amount)
                credit_amount = float(txn_amount) - float(all1zed_charge)
                card_account.card_balance = card_account.card_balance + float(credit_amount)

                airtel_query = airtel_pay_query(f'{txn_amount}', wallet_msisdn, airtel_reference, login_session)
                print(f'AIRTEL - airtel_query {airtel_query}')
            else:               
                return Response({'Error': 'The card you are trying to access is blocked.'}, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, TypeError) as e:
            pass
    
        try:
            if 'Please confirm' in airtel_query.get('confirmation_message'):
                resp_body = airtel_pay_query_confirm(airtel_query.get('confirmation_number', None), login_session)
                print(f'AIRTEL - resp_body {resp_body}')
        except (KeyError, TypeError) as e:
            pass

        try:
            if 'Payment Successful' in resp_body.get('response_message', None):
                card_account.save()
                return Response({"Success": "OK"})
        except (KeyError, TypeError) as e:
            pass 
       

class ZamtelPayView(APIView):

    def post(self, request, *args, **kwargs):
        session_uuid = request.data.get('session_uuid')
        msisdn = request.data.get('msisdn', '')
        txn_amount = request.data.get('txn_amount', '')
        card_number = request.data.get('card_number', None)
        
        all1zed_charge = (2/100) * float(txn_amount)
        total_bill = int(txn_amount) + int(all1zed_charge)

        try:
            zamtel_pay_response = zamtel_pay(f'{total_bill}', msisdn, session_uuid)
            print(f'ZAMTEL-zamtel_pay_response {zamtel_pay_response}')
        except (KeyError, TypeError) as e:
            pass
        
        try:
            card_account = CardAccount.objects.get(card_number=card_number)
            print(f'CARD_ACCOUNT {card_account}')
        except CardAccount.DoesNotExist:
            return Response({'Error': 'Card does not exist'})
            
        try:
             
            if card_account.is_active == True:
                # Update card account balance 
                txn_charge = (2/100) * float(txn_amount)
                actual_amount = float(txn_amount) - float(txn_charge)
                card_account.card_balance = card_account.card_balance + float(actual_amount)
           
                if "Please confirm" in zamtel_pay_response.get('confirmation_message', ''):
                    zamtel_confirm = zamtel_pay_confirm(zamtel_pay_response.get('confirmation_number', ''), session_uuid)
                    print(f'ZAMTEL-CONFIRM {zamtel_confirm }')
        except (KeyError, TypeError) as e:
            pass
        if 'Payment Successful' in zamtel_confirm.get('response_message'):
            card_account.save()

            return Response({'Success': 'OK'})
        return Response({'Msg': 'Error'})

    
class MtnDebitView(APIView):

    def post(self, request, *args, **kwargs):
        session_uuid = request.data.get('session_uuid', None)
        wallet_msisdn = request.data.get('wallet_msisdn', None)
        txn_amount = float(request.data.get('txn_amount'))

        all1zed_charge = (2/100) * float(txn_amount)
        total_bill = int(txn_amount) + int(all1zed_charge)
     
        try:
            resp_body = mtn_momo_pay(f'{total_bill}00', wallet_msisdn, session_uuid)
            txn_id = resp_body.get('supplier_transaction_id', None)
            phone_number = resp_body.get('wallet_msisdn', None)
            print(f"AIRTEL - airtel_pay {resp_body}")
        except (KeyError, TypeError) as e:
            pass

        return Response({"Message": "Success", "supplier_transaction_id": txn_id, "wallet_msisdn": phone_number})
        

class MtnDebitConfirm(APIView):
    '''
    All1Zed user can load funds from their MTN MOMO account into their All1Zed card account
    '''

    def post(self, request, *args, **kwargs):
        session_uuid = request.data.get('session_uuid', None)
        wallet_msisdn = request.data.get('wallet_msisdn', '')
        supplier_transaction_id = request.data.get('supplier_transaction_id', '')
        card_number = request.data.get('card_number', '')
        txn_amount = request.data.get('txn_amount', None)

        # Check if card is registered
        try: 
            card_account = CardAccount.objects.get(card_number=card_number)
            print(card_account)
        except CardAccount.DoesNotExist:
            return Response({'Error': 'Account not found'})

        try:
            if card_account.is_active == True:
                # Update card account balance 
                txn_charge = (2/100) * float(txn_amount)
                actual_amount = float(txn_amount) - float(txn_charge)
                card_account.card_balance = card_account.card_balance + float(actual_amount)

                mtn_approval = mtn_momo_pay_approval(f'{txn_amount}', wallet_msisdn, supplier_transaction_id, session_uuid)
                print(f'MTN-APPROVAL {mtn_approval}')
            else:
                return Response({'Error': 'The card you are trying to access is blocked.'}, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, TypeError) as e:        
             return Response({'Error': e})
        
        try:
            if mtn_approval.get("response_code") == '0':
                print(f'MTN-APPROVAL-REPRINT {mtn_approval.get("response_code")}')
                confirmation_number = mtn_approval.get('confirmation_number')
                print(confirmation_number)
                approval_response = mtn_momo_pay_confirm(confirmation_number, session_uuid)
                card_account.save()
                print(f'APPROVAL-CONFIRM {approval_response}')
                return Response({'Message': 'Success'})
            return Response({'Error': True})
        except (KeyError, TypeError) as e:
            pass



#{
#  "txn_amount": "100",
#   "wallet_msisdn": "976637416",
#    "airtel_reference": "3663813458",
#  "session_uuid": "7d4fb09e-37ae-4328-a456-314cdca08a62",
# "card_number": "0022"
#}


#
#{
#  "wallet_msisdn": "0963533399",
#  "txn_amount": "100",
#  "supplier_transaction_id": "3614814347",
#  "session_uuid": "dfc9560f-2b6e-48e0-a186-307f0d554088",
# "card_number": "0022"
#}
