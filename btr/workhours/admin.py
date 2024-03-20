from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from .models import WorkHours


class WorkHoursAdmin(admin.ModelAdmin):

    list_display = ('day', 'open', 'close')

    def save_model(self, request, obj, form, change):
        if WorkHours.objects.count() >= 2 and not obj.pk:
            messages.error(
                request,
                _('Only two records are allowed here!'),
            )
            return
        super().save_model(request, obj, form, change)


admin.site.register(WorkHours, WorkHoursAdmin)
admin.site.site_title = _('Opening hours operation')
