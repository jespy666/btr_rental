from django.urls import path
from .views import (BookingCreateView, BookingEditView, BookingCancelView,
                    BookingIndexView, BookingDetailView)

urlpatterns = [
    path('', BookingIndexView.as_view(), name='bookings'),
    path('create/', BookingCreateView.as_view(), name='book_create'),
    path('<int:pk>/show/', BookingDetailView.as_view(), name='book_show'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='book_cancel'),
    path('<int:pk>/edit/', BookingEditView.as_view(), name='book_edit'),
]
