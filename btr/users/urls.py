from django.urls import path
from .views import UserRegistrationView, UserView, UserUpdateView

urlpatterns = [
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('<int:pk>/profile/', UserView.as_view(), name='profile'),
    path('<int:pk>/profile/edit/', UserUpdateView.as_view(), name='user_edit'),
]