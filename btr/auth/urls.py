from django.urls import path

from .views import (AuthLoginView, AuthLogoutView, AuthResetView,
                    ConfirmCodeView)

urlpatterns = [
    path('login/', AuthLoginView.as_view(), name='login'),
    path('logout/', AuthLogoutView.as_view(), name='logout'),
    path('reset_password/', AuthResetView.as_view(), name='auth-reset'),
    path('confirm_code/', ConfirmCodeView.as_view(), name='confirm')
]
