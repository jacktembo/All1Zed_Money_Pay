from django.conf import settings
from django.contrib import auth
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response 
from .models import BusinessProfile, OrganizationProfile, LimitedCompanyProfile
from .serializers import (
    UserSerializer, LoginSerializer, 
    BusinessProfileSerializer, BlockCardSerializer, 
    OrganizationProfileSerializer, CreateBusinessSerializer,
)
from authentication.serializers import CardAccountSerializer
from .helper_functions import id_generator
from all1zed_api.models import CardAccount, MerchantCode, BusinessAccount
from all1zed_api.momo_pay import generate_pin
from all1zed_api.send_notifications import send_notification
import jwt 


class RegisterView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        user = auth.authenticate(username=username, password=password)

        if user:
            auth_token = jwt.encode({'username': user.username}, settings.JWT_SECRET_KEY)
            serializer = LoginSerializer(user)
            data = {
                'user': serializer.data,
                'token': auth_token
            }

            return Response({'Data': data}, status=status.HTTP_200_OK)
        return Response({'Error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class OrganizationProfileView(APIView):
    """
    This the code for creating an organisation profile after they have registered on All1Zed platform.
    This is the second step after first user account creation and it is required by every user to 
    start using the All1Zed app. (Emmanuel Simasiku)
    """
    serializer_class = OrganizationProfileSerializer

    def get(self, request, format=None):
        account = None
        try:
            organization = OrganizationProfile.objects.get(user=request.user)
        except OrganizationProfile.DoesNotExist:
            return Response({"profile": "Profile not found"})
        try:
            account = BusinessAccount.objects.get(user=request.user, account_type="organization")
        except BusinessAccount.DoesNotExist:
            return Response({"profile": "Profile not found"})

        serializer = OrganizationProfileSerializer(organization, context={'request': request})
        return Response({"profile": serializer.data, "balance": account.balance, "businessAccountID": account.id})

    def post(self, request, format='json'):
        serializer = OrganizationProfileSerializer(data=request.data)
        merchant_code = f'{generate_pin(5)}'

        if serializer.is_valid():
            MerchantCode.objects.create(
                user=request.user,
                merchant_code=merchant_code,
                business_name=request.data.get('business_name')
            )
            BusinessAccount.objects.create(
                user=request.user,
                merchant_code=merchant_code,
                phone_number=request.user.username
            )
            serializer.save(user=request.user, merchant_code=merchant_code)
            return Response({"success": "ok"})
        return Response({"error": serializer.errors})



class BusinessProfileView(APIView):
    '''
    This code section creates a business profile after they have reqiestered on All1Zed platform.
    This is the second step after creating the first account required to start using the the All1Zed app.
    '''
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = BusinessProfileSerializer

    def get(self, request, formate='json'):
        try:
            business = BusinessProfile.objects.get(user=request.user)
            print(f'BUSINESS PROFILE {business}')
        except BusinessProfile.DoesNotExist:
            return Response({'Profile': 'Profile not found'})

        try:
            acc_details = BusinessAccount.objects.get(user=request.user)
            print(f'BUSINESS-ACC PROFILE {acc_details}')
        except BusinessAccount.DoesNotExist:
            return Response({'Profile': 'Profile not found'})

        serializer = BusinessProfileSerializer(business, context={'request': request})
        return Response(
            {
                'Profile': serializer.data, 
                'Balance': acc_details.balance, 
                'BusinessAccountID': acc_details.id
            }
        )

    def post(self, request, formate='json'):
        business_name = request.data.get('business_name')
        merchant_code = f'{generate_pin(5)}'
        serializer = CreateBusinessSerializer(data=request.data)

        if serializer.is_valid():
            MerchantCode.objects.create(
                user=request.user,
                business_name=business_name,
                merchant_code=merchant_code
            )
            business_account = BusinessAccount(
                user=request.user,
                merchant_code=merchant_code,
                phone_number=request.user.username
            )

            business_account.save()
            serializer.save(user=request.user, merchant_code=merchant_code)
            return Response({'Sucess': 'OK'})
        return Response({'Error': serializer.errors})


class RegisterCardView(APIView):
    serializer_class = CardAccountSerializer

    def post(self, request, *args, **kwargs):
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        phone_number = request.data.get('phone_number', None)
        card_number = request.data.get('card_number', None)
        card_id = id_generator()
        
        serializer = CardAccountSerializer(data=request.data)
    
        if serializer.is_valid():
            serializer.save()
            notification_msg  = f'Dear {first_name} {last_name}, your card account with card number: {card_number} has been created successfully. Dial *772# to top up your card and start transacting.'       
            probase_response = send_notification(phone_number, notification_msg)
            print(notification_msg)
            print(f'PROBASE {probase_response}')
            return Response({'Success': 'Created', 'Card_Account_Data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'Error': serializer.errors})
        
   
class BlockCardView(APIView):
    serializer_class = BlockCardSerializer

    def put(self, request, *args, **kwargs):
        try:
            card_number = request.data.get('card_number', None)
            card_account = CardAccount.objects.get(card_number=card_number)

            if card_account.is_active == True:
                card_account.is_active == False
                card_account.save()
                
                return Response({'Info': 'Card blocked successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'Error': 'Card is already blocked'}, status=status.HTTP_400_BAD_REQUEST)
        except CardAccount.DoesNotExist:
            return Response({'Error': 'Card does not exist'}, status=status.HTTP_400_BAD_REQUEST)








