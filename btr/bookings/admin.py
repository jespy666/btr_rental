from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from btr.bookings.models import Booking
from btr.tasks.admin import send_vk_notify
from btr.tasks.bookings import (send_confirm_message, send_cancel_message,
                                send_edit_booking_message)
from ..orm_utils import AsyncTools


@admin.action(description=_('Confirm selected bookings'))
def make_confirm(modeladmin, request, queryset) -> None:
    """
    Custom admin action to confirm selected bookings.

    Args:
        modeladmin: The admin class instance.
        request: The HTTP request object.
        queryset: Queryset containing selected bookings.

    Returns:
        None

    Example:
        Select bookings in the Django admin interface and choose the
         'Confirm selected bookings' action.
        This will mark the selected bookings as 'confirmed' and trigger
         notifications to the client.
    """
    for booking in queryset:
        booking.status = _('confirmed')
        booking.save()
        f_phone = booking.foreign_number
        # check if foreign booking
        phone = f_phone if f_phone else booking.rider.phone_number
        date = booking.booking_date.strftime('%Y-%B-%d')
        via = _('Admin panel')
        data = {
            'pk': booking.pk,
            'client': booking.rider.username,
            'date': AsyncTools().get_friendly_date(date),
            'start': booking.start_time.strftime('%H:%M'),
            'end': booking.end_time.strftime('%H:%M'),
            'bikes': booking.bike_count,
            'phone': str(phone),
            'status': booking.status,
            'email': booking.rider.email,
        }
        # send message to admin
        send_vk_notify.delay(via, False, data, is_admin=True)
        # send confirm message to user email
        send_confirm_message.delay(**data)


@admin.action(description=_('Cancel selected bookings'))
def make_cancel(modeladmin, request, queryset) -> None:
    """
    Custom admin action to cancel selected bookings.

    Args:
        modeladmin: The admin class instance.
        request: The HTTP request object.
        queryset: Queryset containing selected bookings.

    Returns:
        None

    Example:
        Select bookings in the Django admin interface and choose
         the 'Cancel selected bookings' action.
        This will mark the selected bookings as 'canceled' and trigger
         notifications to the client.
    """
    for booking in queryset:
        booking.status = _('canceled')
        booking.save()
        f_phone = booking.foreign_number
        date = booking.booking_date.strftime('%Y-%B-%d')
        via = _('Admin panel')
        data = {
            'pk': booking.pk,
            'client': booking.rider.username,
            'email': booking.rider.email,
            'date': AsyncTools().get_friendly_date(date),
            'start': booking.start_time.strftime('%H:%M'),
            'end': booking.end_time.strftime('%H:%M'),
            'bikes': booking.bike_count,
            'phone': str(f_phone if f_phone else booking.rider.phone_number),
            'status': booking.status,
        }
        send_vk_notify.delay(via, False, data, is_admin=True)
        send_cancel_message.delay(**data)


class RiderAdminFilter(admin.SimpleListFilter):
    """
    Custom admin filter for outer bookings.

    Args:
        admin.SimpleListFilter: Base class for creating custom filters.

    Attributes:
        title (str): The display name for the filter.
        parameter_name (str): The parameter name used in the query string.

    Example:
        In the Django admin interface, use the 'Outer booking' filter
         to display bookings associated with the 'admin' user.
    """
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
    """
    Custom admin configuration for managing bookings.

    Attributes:
        list_display (tuple): Fields to display in the admin list view.

    Example:
        In the Django admin interface, manage bookings with additional
         functionality provided by this custom configuration.
    """
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
        """
        Create a link to the user's profile page.

        Args:
            obj: The booking instance.

        Returns:
            str: HTML link to the user's profile page.

        Example:
            Displays the user's username as a clickable link.
        """
        url = reverse(
            'admin:users_siteuser_change',
            args=[obj.rider.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.rider.username
        )

    def save_model(self, request, obj, form, change):
        """
        Custom method to handle saving booking changes.

        Args:
            request: The HTTP request object.
            obj: The booking instance being saved.
            form: The form containing the booking data.
            change (bool): Indicates whether the booking is being edited.

        Returns:
            None

        Example:
            When a booking is saved, this method triggers notifications
             and handles status changes.
        """
        client = obj.rider.username
        f_phone = obj.foreign_number
        # check if outer booking
        phone = f_phone if f_phone else obj.rider.phone_number
        booking_date = obj.booking_date.strftime('%Y-%B-%d')
        date = AsyncTools().get_friendly_date(booking_date)
        start = obj.start_time.strftime('%H:%M')
        end = obj.end_time.strftime('%H:%M')
        bikes = obj.bike_count
        via = _('Admin panel')
        # check if not new object
        if change:
            changed_fields = form.changed_data
            data = {
                'pk': obj.pk,
                'client': client,
                'email': obj.rider.email,
                'date': date,
                'start': start,
                'end': end,
                'bikes': bikes,
                'phone': str(phone),
            }
            # check if only status field has changed
            if len(changed_fields) == 1 and 'status' in changed_fields:
                status = form.cleaned_data.get('status')
                data['status'] = status
                send_vk_notify.delay(via, False, data, is_admin=True)
                if status == _('confirmed'):
                    send_confirm_message.delay(**data)
                elif status == _('canceled'):
                    send_cancel_message.delay(**data)
            # if other fields changed too
            else:
                data['status'] = _('pending')
                send_vk_notify.delay(via, False, data, is_admin=True)
                send_edit_booking_message.delay(**data)
        # if new object
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

    search_fields = ('id', 'booking_date', 'rider__username')
    list_filter = (RiderAdminFilter, 'status')
    actions = [make_confirm, make_cancel]


admin.site.register(Booking, BookingAdmin)
admin.site.site_title = _('Booking Management')
admin.site.site_header = _('Admin Panel')
