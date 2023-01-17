from rest_framework.views import APIView
from rest_framework import status, permissions
from authentication.serializers import BusinessProfileSerializer, OrganizationProfileSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from all1zed_api.models import Transaction, BusinessTransaction
from all1zed_api.serializers import (
    BalanceSerializer, BusinessAccountSerializer,
    BusinessProfileListSerializer, TransactionHistorySerializer,
    CardsListSerializer, CardPaymentSerializer, BusinessTxnHistorySerializer,
) 
from authentication.models import BusinessProfile
from all1zed_api.momo_pay import generate_pin, login
from .models import CardAccount, BusinessAccount
from all1zed_api.momo_pay import generate_pin, login
from all1zed_api.nfs_cashin import (
    nfs_zanaco_cashin, nfs_zanaco_cashin_confirm,
    nfs_momo_cashin_confirm, nfs_airtel_cashin, 
    nfs_airtel_cashin_confirm, nfs_zamtel_cashin,
    nfs_zamtel_cashin_confirm,
)
from all1zed_api.send_notifications import send_notification


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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CardPaymentSerializer

    def post(self, request, format=None):
        serializer = CardPaymentSerializer(data=request.data)

        if serializer.is_valid():
            card_number = request.data.get('card_number', None)
            amount = float(request.data.get('txn_amount', None))
            
            try:
                card_account = CardAccount.objects.get(card_number=card_number)
            except CardAccount.DoesNotExist:
                return Response({'Error': 'Card account not found'})

            try:
                merchant_account = BusinessAccount.objects.get(user=request.user)
            except BusinessAccount.DoesNotExist:
                return Response({'Error': 'Merchant account not found'})

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
                        print(f'Zanaco-CONFIRM {confirm_response}')

                        Transaction.objects.create(
                            card_number=card_number,
                            txn_type='pay',
                            txn_amount=amount,                      
                            update_amount=card_account.card_balance,             
                            reference_id=txn_id,
                            message=f'Payment of {amount} to {merchant_account.merchant_code} is successful',
                            status= True
                        )  

                        BusinessTransaction.objects.create(
                            user=request.user.username,
                            branch_name=merchant_account.branch_name,
                            txn_type='pay',
                            txn_amount=amount,             
                            txn_commission=commission,          
                            update_amount=merchant_account.balance,             
                            reference_id=txn_id,
                            message=f'{card_number} has successfully paid {amount} to your account',
                            status= True
                        )  
                     
                        notification_msg = f'You have successfully paid ZMW{amount} to {merchant_account.business_name} - {merchant_account.merchant_code}. Your balance is now {card_account.card_balance} Transaction ID: {txn_id}'
                        send_notification(card_account.phone_number, notification_msg)
                        
                        return Response({'Success': 'OK', 'Details': serializer.data})

                    return Response({'Error': True})
                except (KeyError, TypeError) as e:
                    pass
                
            return Response({"Error": 'Unknown account type'})
        return Response({'Error': serializer.errors})


class BusinessAcountListView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessProfileSerializer

    def get(self, request):
        business_accounts = BusinessProfile.objects.all()
        total_business_accounts = business_accounts.count()
        serializer = BusinessProfileSerializer(business_accounts, many=True)

        return Response({'Business_Accounts': serializer.data, 'Total_business_accounts': total_business_accounts})


class ListCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CardsListSerializer
    
    def get(self, request, *args, **kwargs):
        all_cards = CardAccount.objects.all()
        serializer = CardsListSerializer(all_cards, many=True)

        return Response({'All_Cards': serializer.data})


class PersonalTxnHistoryView(RetrieveAPIView):
    serializer_class = TransactionHistorySerializer

    def get(self, request, *args, **kwargs):
        txn_date = request.data.get('txn_date', None)
        from_date = request.data.get('start_date', None)
        to_date = request.data.get('end_date', None)
        card_number = request.data.get('card_number', None)

        try:
            card_account = CardAccount.objects.get(card_number=card_number)
        except CardAccount.DoesNotExist:
            return Response({'Error': 'Card account not found'})

        if card_number == card_account.card_number:
            transactions = Transaction.objects.filter(card_number=card_number).order_by('-created_on')
            
            if card_account.is_active == True:
                if txn_date:
                    txn_list = transactions.filter(created_on=txn_date)
                    serializer = TransactionHistorySerializer(txn_list, many=True)
                    return Response({'Personal_Transaction_list': serializer.data}, status=status.HTTP_200_OK)

                elif from_date and to_date:
                    txn_list = transactions.filter(created_on__range=['from_date', 'to_date'])
                    serializer = TransactionHistorySerializer(txn_list, many=True)
                    return Response({'Personal_Transaction_list': serializer.data}, status=status.HTTP_200_OK)

                else:
                    serializer = TransactionHistorySerializer(transactions, many=True)
                    return Response({'Personal_Transaction_list': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'Error': 'Card account not found'})
        else:
            return Response({'Error': 'Invalid card number'})


class BusinessTxnHistory(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessTxnHistorySerializer

    def get(self, request, *args, **kwargs):
        queryset = BusinessTransaction.objects.all().order_by('created_on')
        transactions = queryset.filter(user=request.user)
        txn_type = request.query_params.get('txn_class')
        txn_date = request.query_params.get('txn_date')
        from_date = request.query_params.get('start_date')
        to_date = request.query_params.get('end_date')
        business_name = self.request.query_params.get('business_name', None)

        try:
            business_account = BusinessAccount.objects.filter(user=request.user)
        except BusinessAccount.DoesNotExist:
            return Response({'Error': 'Business account not found'})

        if business_name == business_account.business_name:
            if txn_date:
                txn_list = transactions.filter(created_on=txn_date, business_name=business_name)
                serializer = BusinessTxnHistorySerializer(txn_list, many=True)
                return Response({'Business_Transaction_list': serializer.data}, status=status.HTTP_200_OK)

            elif from_date and to_date:
                txn_list = transactions.filter(created_on_range=['from_date', 'to_date'])
                serializer = BusinessTxnHistorySerializer(txn_list, many=True)
                return Response({'Business_Transaction_list': serializer.dat}, status=status.HTTP_200_OK)

            else:
                serializer = BusinessTxnHistorySerializer(transactions, many=True)
                return Response({'Business_Transaction_list': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Invalid business name'})





