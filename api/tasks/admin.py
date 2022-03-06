from django.contrib import admin

from tasks import models


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.TaskType, list_display=["id", "name"], list_display_links=["id", "name"])

admin.site.register(
    models.Task,
    admin_class=ReadOnlyAdmin,
    list_select_related=["task_type"],
    list_display=["created", "task_id", "processing_time", "status", "task_type"],
    list_filter=["status", "task_type"],
    search_fields=["task_id", "task_type__name"],
)
