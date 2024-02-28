from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import VKCommentsView, health
from .views import IndexView, BriefingView, ContactsView, GalleryView, BlogView

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('briefing/', BriefingView.as_view(), name='briefing'),
    path('auth/', include('btr.auth.urls')),
    path('users/', include('btr.users.urls')),
    path('bookings/', include('btr.bookings.urls')),
    path('reviews/', VKCommentsView.as_view(), name='reviews'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
    path('admin/', admin.site.urls),
    path('health-check/', health, name='is_health'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
