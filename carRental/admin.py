from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Car, VisitLog


# Register your models here.

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    fields = ("automaker", "model", "year", "type", "price", "is_available")  # Hidden created_by

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user.id
        obj.from_admin_site = True
        obj.save()

    def delete_model(self, request, obj):
        obj.from_admin_site = True
        obj.delete()

    def save_formset(self, request, form, formset, change):
        if formset.model == Car:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.save()
        else:
            formset.save()


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True  # Change to false so logs can't be deleted

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return mark_safe(link)

    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"


@admin.register(VisitLog)
class VisitorLogAdmin(admin.ModelAdmin):

    list_display = ("timestamp", "user", "ip_address", "agent")
    list_filter = ("timestamp",)
    search_fields = (
        "user",
        "agent",
    )
    readonly_fields = (
        "user",
        "hash",
        "timestamp",
        "session_key",
        "ip_address",
        "agent",
        "created_at",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
