from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('auth_registration.urls')),
    path('profile/', include('profile_user.urls')),
]
