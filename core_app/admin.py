from django.contrib import admin
from core_app.models import ForgotPasswordLinkModel, TasksModel, TaskSchedulesModel

admin.site.register(ForgotPasswordLinkModel)
admin.site.register(TasksModel)
admin.site.register(TaskSchedulesModel)
