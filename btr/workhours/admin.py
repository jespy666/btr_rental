from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import WorkHours, DayControl


class WorkHoursAdmin(admin.ModelAdmin):
    """
    Admin configuration for the WorkHours model.

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
    """

    list_display = ('day', 'open', 'close')

    def save_model(self, request, obj, form, change):
        if WorkHours.objects.count() >= 2 and not obj.pk:
            messages.error(
                request,
                _('Only two records are allowed here!'),
            )
            return
        super().save_model(request, obj, form, change)


class PastDateFilter(SimpleListFilter):
    title = _('Outdated entries')
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        return (
            ('past', _('Yes')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'past':
            return queryset.filter(date__lte=timezone.now().date())


class DayControlAdmin(admin.ModelAdmin):

    list_display = ('date', 'open', 'close', 'is_closed')
    list_filter = ('is_closed', PastDateFilter)


admin.site.register(WorkHours, WorkHoursAdmin)
admin.site.register(DayControl, DayControlAdmin)
admin.site.site_title = _('Opening hours operation')
