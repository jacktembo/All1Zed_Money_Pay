from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/auth/', include('authentication.urls')),
    path('', include('all1zed_api.urls'))
]
