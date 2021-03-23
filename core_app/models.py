from django.db import models
from django.contrib.auth.models import User


class ForgotPasswordLinkModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    activation_key = models.CharField(max_length=255, default="", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.get_full_name()}'


class TaskSchedulesModel(models.Model):
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="assigned_by")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_to')
    description = models.CharField(max_length=255, default="", null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    is_delete = models.BooleanField(null=True, blank=True, default=False)

    def __str__(self):
        return self.description
