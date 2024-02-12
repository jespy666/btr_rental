from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from btr.bookings.models import Booking
from btr.tasks.admin import send_vk_notify
from btr.tasks.bookings import send_confirm_message, send_cancel_message


@admin.action(description=_('Confirm selected bookings'))
def make_confirm(modeladmin, request, queryset):
    for booking in queryset:
        booking.status = _('confirmed')
        booking.save()
        email = booking.rider.email
        pk = booking.pk
        client = booking.rider.username
        f_phone = booking.foreign_number
        phone = f_phone if f_phone else booking.rider.phone_number
        date = booking.booking_date
        start = booking.start_time.strftime('%H:%M')
        end = booking.end_time.strftime('%H:%M')
        bikes = booking.bike_count
        via = _('Admin panel')
        data = {
            'pk': pk,
            'client': client,
            'date': date,
            'start': start,
            'end': end,
            'bikes': bikes,
            'phone': str(phone),
            'status': booking.status,
        }
        send_vk_notify.delay(via, False, data, is_admin=True)
        send_confirm_message.delay(email, pk, bikes, date, start, end)


@admin.action(description=_('Cancel selected bookings'))
def make_cancel(modeladmin, request, queryset):
    for booking in queryset:
        booking.status = _('canceled')
        booking.save()
        email = booking.rider.email
        pk = booking.pk
        client = booking.rider.username
        f_phone = booking.foreign_number
        phone = f_phone if f_phone else booking.rider.phone_number
        date = booking.booking_date
        start = booking.start_time.strftime('%H:%M')
        end = booking.end_time.strftime('%H:%M')
        bikes = booking.bike_count
        via = _('Admin panel')
        data = {
            'pk': pk,
            'client': client,
            'date': date,
            'start': start,
            'end': end,
            'bikes': bikes,
            'phone': str(phone),
            'status': booking.status,
        }
        send_vk_notify.delay(via, False, data, is_admin=True)
        send_cancel_message.delay(email, pk, date, start, end)


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

    def save_model(self, request, obj, form, change):
        client = obj.rider.username
        f_phone = obj.foreign_number
        phone = f_phone if f_phone else obj.rider.phone_number
        date = obj.booking_date
        start = obj.start_time.strftime('%H:%M')
        end = obj.end_time.strftime('%H:%M')
        bikes = obj.bike_count
        via = _('Admin panel')
        if change:
            changed_fields = form.changed_data
            if 'status' in changed_fields:
                status = form.cleaned_data.get('status')
                email = obj.rider.email
                data = {
                    'pk': obj.pk,
                    'client': client,
                    'date': date,
                    'start': start,
                    'end': end,
                    'bikes': bikes,
                    'phone': str(phone),
                    'status': status,
                }
                send_vk_notify.delay(via, False, data, is_admin=True)
                if status == _('confirmed'):
                    send_confirm_message.delay(email, obj.pk, bikes,
                                               date, start, end)
                elif status == _('canceled'):
                    send_cancel_message.delay(email, obj.pk, date, start, end)
        else:
            last_booking = Booking.objects.latest('created_at')
            data = {
                'pk': last_booking.pk + 1,
                'client': client,
                'date': date,
                'start': start,
                'end': end,
                'bikes': bikes,
                'phone': str(phone),
                'status': _('Confirmed'),
            }
            send_vk_notify.delay(via, True, data, is_admin=True)
        super().save_model(request, obj, form, change)

    link_to_user.short_description = _('User')

    search_fields = ('id', 'status', 'booking_date')
    list_filter = (RiderAdminFilter, 'status')
    actions = [make_confirm, make_cancel]


admin.site.register(Booking, BookingAdmin)
admin.site.site_title = _('Booking Management')
admin.site.site_header = _('Admin Panel')
