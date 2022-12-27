from rest_framework.views import APIView
from all1zed_api.serializers import (
    BalanceSerializer, BusinessAccountSerializer,
    BusinessProfileListSerializer,
    CardsListSerializer, CardPaymentSerializer,
) 
from authentication.serializers import BusinessProfileSerializer, OrganizationProfileSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from all1zed_api.momo_pay import generate_pin, login
from .models import CardAccount, BusinessAccount
from all1zed_api.momo_pay import generate_pin, login
from all1zed_api.nfs_cashin import (
    nfs_zanaco_cashin, nfs_zanaco_cashin_confirm,
    nfs_momo_cashin_confirm, nfs_airtel_cashin, 
    nfs_airtel_cashin_confirm, nfs_zamtel_cashin,
    nfs_zamtel_cashin_confirm,
)

login_session = login()

class BalanceView(APIView):
    serializer_class = BalanceSerializer

    def get_object(self, pk):
        try:
            return CardAccount.objects.get(phone_number=pk)
        except CardAccount.DoesNotExist:
            return Response({'Error': 'Account not found'})

    def get(self, pk, format=None):
        balance = self.get_object(pk)
        serializer = BalanceSerializer(balance)
        return Response(serializer.data)


class CardPaymentView(APIView):
    '''
    An All1Zed user can pay for a service.
    - A user credits the service provider.
    - A percent from the amount is creditted to All1Zed.
    - User account is debited 
    '''
    serializer_class = CardPaymentSerializer

    def post(self, request, format=None):
        serializer = CardPaymentSerializer(data=request.data)

        if serializer.is_valid():
            merchant_code = request.data.get('merchant_code', '')
            card_number = request.data.get('card_number', None)
            amount = float(request.data.get('txn_amount', None))
            
            # Find customer account on All1Zed platform
            try:
                card_account = CardAccount.objects.get(card_number=card_number)
            except CardAccount.DoesNotExist:
                return Response({'Error': 'Account not found'})

            # Find Merchant account on All1Zed platform
            try:
                merchant_account = BusinessAccount.objects.get(merchant_code=merchant_code)
            except BusinessAccount.DoesNotExist:
                return Response({'Error': 'Account not found'})

            if card_account.card_balance < float(amount):
                return Response({'Error': 'Insufficient balance'})

            card_account.card_balance = card_account.card_balance - float(amount)
            commision_amount = float(merchant_account.commission)
            commission = amount - commision_amount/100 * float(amount)

            if merchant_account.account_type == 'zanaco':
                reference = merchant_account.bank_account_number
                disbursment = nfs_zanaco_cashin(f'{amount}00', reference, login_session)
                try:
                    if disbursment.get("response_code") == '0':
                        print(f'Zanaco-APPROVAL-REPRINT {disbursment.get("response_code")}')
                        confirmation_number = disbursment.get('confirmation_number')
                        print(confirmation_number)
                        confirm_response = nfs_zanaco_cashin_confirm(confirmation_number, login_session)
                        merchant_account.balance = float(merchant_account.balance) + commission
                        merchant_account.save()
                        card_account.save()
                        txn_id = generate_pin(12)
                        # send_message(sender.phone_number, verification_msg)
                        print(f'Zanaco-CONFIRM {confirm_response}')

#                        Transaction.objects.create(
#                            user=request.user,
#                            txn_type='pay',
#                            txn_amount=amount,             
#                            txn_charge=all1zed_charge,          
#                            update_amount=customer_acc.balance,             
#                            reference_id=txn_id,
#                            message=f'Payment of {amount} to {merchant_code} is successful',
#                            status= True
#                        )  
#
#                        Transaction.objects.create(
#                            user=request.user,
#                            txn_type='pay',
#                            txn_amount=amount,             
#                            txn_charge=all1zed_charge,          
#                            update_amount=merchant_acc.balance,             
#                            reference_id=txn_id,
#                            message=f'{request.user.username} has successfully paid {amount} to you account',
#                            status= True
#                        )  
#                        
                        message = f'You have successfully paid ZMW{amount} to {merchant_account.business_name} - {merchant_code}. Your balance is now {card_account.card_balance} Transaction ID: {txn_id}'
       
                        return Response({'Success': 'OK', 'Details': serializer.data})

                    return Response({'Error': True})
                except (KeyError, TypeError) as e:
                    pass
                
            return Response({"Error": 'Unknown account type'})
        return Response({'Error': serializer.errors})


class BusinessAcountListView(RetrieveAPIView):
    serializer_class = BusinessProfileSerializer

    def get(self, request):
        business_accounts = BusinessProfile.objects.all()
        total_business_accounts = business_accounts.count()
        serializer = BusinessProfileSerializer(business_accounts, many=True)

        return Response({'Business_Accounts': serializer.data, 'Total_business_accounts': total_business_accounts})


class ListCardsView(APIView):
    serializer_class = CardsListSerializer
    
    def get(self, request, *args, **kwargs):
        all_cards = CardAccount.objects.all()
        serializer = CardsListSerializer(all_cards, many=True)

        return Response({'All_Cards': serializer.data})




















            
