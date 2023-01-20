from django.urls import path
from all1zed_api import views, momo_views
from all1zed_api.cashin import CardDetails, CashinView
from authentication.views import OrganizationProfileView

urlpatterns = [
    path('api/payments/mtnPayment/', momo_views.MtnDebitView.as_view(), name='mtn-pay'),
    path('api/payments/cardPayment/', views.CardPaymentView.as_view(), name='card-payment'),
    path('api/payments/airtelPayment/', momo_views.AirtelPayView.as_view(), name='airtel-pay'),
    path('api/payments/zamtelPayment/', momo_views.ZamtelPayView.as_view(), name='airtel-pay-confirm'),
    path('api/payments/mtnPaymentConfirm/', momo_views.MtnDebitConfirm.as_view(), name='mtn-pay-confirm'),
    path('api/payments/airtelPaymentConfirm/', momo_views.AirtelPayConfirmView.as_view(), name='airtel-pay-confirm'),
    path('api/payments/zamtelPaymentConfirm/', momo_views.AirtelPayConfirmView.as_view(), name='zamtel-pay-confirm'),
    path('api/accounts/cards/list/', views.ListCardsView.as_view(), name='cards_list'),
    path('api/accounts/businesses/list/', views.BusinessAcountListView.as_view(), name='business_accounts_list'),
    path('api/accounts/create/organization/', OrganizationProfileView.as_view(), name='create_organization_account'),
    path('api/accounts/card/details/', CardDetails.as_view(), name='card_details'),
    path('api/accounts/transfer/', CashinView.as_view(), name='money_transfers'),
    path('api/accounts/transactions/business/', views.BusinessTxnHistory.as_view(), name='business_transaction_history'),
    path('api/accounts/transactions/personal/', views.PersonalTxnHistoryView.as_view(), name='personal_transaction_history'),
]
