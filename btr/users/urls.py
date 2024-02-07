from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (UserRegistrationView, UserView, UserUpdateView,
                    UserDeleteView, UserUpdateImageView,
                    UserChangePasswordView)

urlpatterns = [
    path(
        'registration/',
        UserRegistrationView.as_view(),
        name='registration'
    ),

    path(
        '<int:pk>/profile/',
        UserView.as_view(),
        name='profile'
    ),

    path(
        '<int:pk>/profile/edit/',
        UserUpdateView.as_view(),
        name='user_edit'
    ),

    path(
        '<int:pk>/profile/delete/',
        UserDeleteView.as_view(),
        name='user_delete'
    ),

    path(
        '<int:pk>/profile/change-image/',
        UserUpdateImageView.as_view(),
        name='change_image'
    ),

    path(
        '<int:pk>/profile/change-password/',
        UserChangePasswordView.as_view(),
        name='change_password'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
