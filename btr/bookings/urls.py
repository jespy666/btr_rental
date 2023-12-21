from django.urls import path
from .views import BookingCreateView, BookingEditView, BookingDeleteView, \
    BookingIndexView

urlpatterns = [
    path('', BookingIndexView.as_view(), name='bookings'),
    path('create/', BookingCreateView.as_view(), name='book_create'),
    path('<int:pk>/edit/', BookingEditView.as_view(), name='book_edit'),
    path('<int:pk>/delete/', BookingDeleteView.as_view(), name='book_delete'),
]
