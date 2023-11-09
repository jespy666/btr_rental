from django.urls import path
from .views import BookingCreateView, BookingEditView, BookingDeleteView


urlpatterns = [
    path('<int:pk>/create/', BookingCreateView.as_view(), name='book_create'),
    path('<int:pk>/edit/', BookingEditView.as_view(), name='book_edit'),
    path('<int:pk>/delete/', BookingDeleteView.as_view(), name='book_delete'),
]
