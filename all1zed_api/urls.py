from django.urls import path
from all1zed_api import views, momo_views
from all1zed_api.cashin import CardDetails, CashinView
from authentication.views import OrganizationProfileView,BusinessProfileView

urlpatterns = [
    path('api/mtnPayment/', momo_views.MtnDebitView.as_view(), name='mtn-pay'),
    path('api/cardPayment/', views.CardPaymentView.as_view(), name='card-payment'),
    path('api/airtelPayment/', momo_views.AirtelPayView.as_view(), name='airtel-pay'),
    path('api/zamtelPayment/', momo_views.ZamtelPayView.as_view(), name='airtel-pay-confirm'),
    path('api/mtnPaymentConfirm/', momo_views.MtnDebitConfirm.as_view(), name='mtn-pay-confirm'),
    path('api/airtelPaymentConfirm/', momo_views.AirtelPayConfirmView.as_view(), name='airtel-pay-confirm'),
    path('api/zamtelPaymentConfirm/', momo_views.AirtelPayConfirmView.as_view(), name='zamtel-pay-confirm'),
    path('api/accounts/cards/list/', views.ListCardsView.as_view(), name='cards_list'),
    path('api/accounts/businesses/list/', views.BusinessAcountListView.as_view(), name='business_accounts_list'),
    path('api/accounts/oragnization/create/', OrganizationProfileView.as_view(), name='create_organization_account'),
    path('api/accounts/businesses/create/', BusinessProfileView.as_view(), name='create_business_account'),
    path('api/card/details/', CardDetails.as_view(), name='card_details'),
    path('api/accounts/cashin/', CashinView.as_view(), name='cashin'),
]
