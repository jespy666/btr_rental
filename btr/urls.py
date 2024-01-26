from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import VKCommentsView
from .views import IndexView, BriefingView, ContactsView, GalleryView

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('briefing/', BriefingView.as_view(), name='briefing'),
    path('auth/', include('btr.auth.urls')),
    path('users/', include('btr.users.urls')),
    path('bookings/', include('btr.bookings.urls')),
    path('reviews/', VKCommentsView.as_view(), name='reviews'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
