from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import UserRegistrationView, UserView, UserUpdateView

urlpatterns = [
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('<int:pk>/profile/', UserView.as_view(), name='profile'),
    path('<int:pk>/profile/edit/', UserUpdateView.as_view(), name='user_edit'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)