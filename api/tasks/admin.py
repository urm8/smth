from django.contrib import admin

from tasks import models

admin.site.register(models.TaskType, list_display=["id", "name"], list_display_links=["id", "name"])
admin.site.register(models.Task)
