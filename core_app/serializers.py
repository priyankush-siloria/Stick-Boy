from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from rest_framework.validators import UniqueValidator
from core_app.models import TasksModel, TaskSchedulesModel


class UserModelSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password']


class AdminEmployeeModelSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']


class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])
    confirm_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])


class UpdatePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    current_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])
    new_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])
    confirm_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])
    confirm_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])


class TasksSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)

    class Meta:
        model = TasksModel
        fields = '__all__'


class SchedulesSerializer(serializers.Serializer):
    admin_id = serializers.IntegerField(required=True)
    employee_id = serializers.IntegerField(required=True)
    task_id = serializers.IntegerField(required=True)


class ViewScheduleSerializer(serializers.ModelSerializer):
    assigned_by = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()

    class Meta:
        model = TaskSchedulesModel
        fields = ['id', 'assigned_by', 'assigned_to', 'task', 'date', 'start_time', 'end_time']

    def get_assigned_by(self, obj):
        return obj.assigned_by.get_full_name()
    
    def get_assigned_to(self, obj):
        return obj.assigned_to.get_full_name()
    
    def get_task(self, obj):
        return obj.task.title