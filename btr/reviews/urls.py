from django.urls import path
from .views import VKCommentsView


urlpatterns = [
    path('', VKCommentsView.as_view(), name='reviews')
    ]
