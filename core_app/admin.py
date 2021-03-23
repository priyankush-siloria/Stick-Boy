from django.contrib import admin
from core_app.models import ForgotPasswordLinkModel, TaskSchedulesModel

admin.site.register(ForgotPasswordLinkModel)


@admin.register(TaskSchedulesModel)
class TaskSchedulesAdmin(admin.ModelAdmin):
    list_display = ['id', 'assigned_by', 'assigned_to', 'description', 'date', 'start_time', 'end_time', 'is_delete']