from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import SiteUser


class UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the User model.

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        list_filter (tuple): Fields to use for filtering in the
         admin list view.
        search_fields (tuple): Fields to use for searching in the
         admin list view.
    """
    list_display = (
        'id',
        'username',
        'first_name',
        'phone_number',
        'email',
        'status',
    )

    list_filter = ('status',)
    search_fields = ('id', 'phone_number', 'username')


admin.site.register(SiteUser, UserAdmin)
admin.site.site_title = _('Users Management')
admin.site.site_header = _('Admin Panel')
