from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from btr.bookings.models import Booking


@admin.action(description=_('Confirm selected bookings'))
def make_confirm(modeladmin, request, queryset):
    queryset.update(status=_('confirmed'))


@admin.action(description=_('Cancel selected bookings'))
def make_cancel(modeladmin, request, queryset):
    queryset.update(status=_('canceled'))


class RiderAdminFilter(admin.SimpleListFilter):
    title = _('Outer booking')
    parameter_name = 'rider'

    def lookups(self, request, model_admin):
        return (
            ('admin', _('Yes')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'admin':
            return queryset.filter(rider__username='admin')


class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'link_to_user',
        'status',
        'booking_date',
        'start_time',
        'end_time',
        'bike_count',
        'foreign_number',
    )

    def link_to_user(self, obj):
        url = reverse(
            'admin:users_siteuser_change',
            args=[obj.rider.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.rider.username
        )

    link_to_user.short_description = _('User')

    search_fields = ('id', 'status', 'booking_date')
    list_filter = (RiderAdminFilter, 'status')
    actions = [make_confirm, make_cancel]


admin.site.register(Booking, BookingAdmin)
admin.site.site_title = _('Booking Management')
admin.site.site_header = _('Admin Panel')
