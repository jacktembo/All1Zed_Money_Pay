from django.contrib import admin
from django.urls import path
from .views import (
    RegisterView, LoginView, 
    RegisterCardView, BusinessProfileViewSet,
)


urlpatterns = [
    path('acounts/register/', RegisterView.as_view(), name = 'register_user'),
    path('accounts/login/', LoginView.as_view(), name = 'login'),
    path('accounts/register/card/', RegisterCardView.as_view(), name='register_card'),
    path('accounts/register/business/', BusinessProfileViewSet.as_view({'get': 'list'}), name='register_business')
]

admin.site.site_header  =  "All1ZedPOS" 
admin.site.index_title  =  "All1ZedPOS Admin Dashboard"  
admin.site.site_title   =  "All1ZedPOS Admin Site"
