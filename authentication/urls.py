from django.urls import path
from .views import (
    RegisterView, LoginView, 
    RegisterCardView, BusinessProfileView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name = 'register_user'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('card/register/', RegisterCardView.as_view(), name='register_card'),
    path('register/business', BusinessProfileView.as_view(), name='register_business')
]
