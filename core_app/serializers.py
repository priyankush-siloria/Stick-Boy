from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from rest_framework.validators import UniqueValidator
from core_app.models import TaskSchedulesModel, ForgotPasswordLinkModel
from django.db.models import Q


class UserModelSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password']
    
    def validate_email(self, email):
        if User.objects.filter(email=email, is_active=True).exists() is False:
            raise serializers.ValidationError('Email not exists.')
        else:
            return email


class AdminEmployeeModelSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def save(self):
        is_employee = self.context.get('is_employee')
        email = self.validated_data.get('email')
        password = self.validated_data.get('password')
        first_name = self.validated_data.get('first_name')
        last_name = self.validated_data.get('last_name')
        if is_employee:
            is_staff = False
            is_superuser = False
        else:
            is_staff = True
            is_superuser = True
        user_obj = User.objects.create(username=email, email=email, first_name=first_name, last_name=last_name, is_staff=is_staff, is_superuser=is_superuser, is_active=True)
        user_obj.set_password(password)
        user_obj.save()
        return user_obj


class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])
    confirm_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])

    class Meta:
        model = User
    
    def validate_email(self, email):
        if User.objects.filter(email=email, is_active=True).exists() is False:
            raise serializers.ValidationError('Email not exists.')
        else:
            return email
    
    def validate_confirm_password(self, confirm_password):
        new_pass = self.initial_data.get('new_password')
        if new_pass != confirm_password:
            raise serializers.ValidationError('New Password and Confirm Password are not equal.')
        return confirm_password
    
    def save(self):
        email = self.validated_data.get('email')
        new_pass = self.validated_data.get('new_password')
        user_obj = User.objects.get(email=email, is_active=True)
        user_obj.set_password(new_pass)
        user_obj.save()
        return user_obj


class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])
    new_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])
    confirm_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])

    class Meta:
        model = User
    
    def validate_current_password(self, current_password):
        pk = self.context.get('pk')
        user_obj = User.objects.get(pk=pk, is_active=True)
        if user_obj.check_password(current_password) is False:
            raise serializers.ValidationError('Invalid current password.')
        return current_password
    
    def validate_confirm_password(self, confirm_password):
        new_pass = self.initial_data.get('new_password')
        if new_pass != confirm_password:
            raise serializers.ValidationError('New Password and Confirm Password are not equal.')
        return confirm_password
    
    def save(self):
        pk = self.context.get('pk')
        new_pass = self.validated_data.get('new_password')
        user_obj = User.objects.get(pk=pk, is_active=True)
        user_obj.set_password(new_pass)
        user_obj.save()
        return user_obj


class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']
    
    def get_role(self, obj):
        role: str = ""
        if obj.is_superuser or obj.is_staff:
            role = "Admin"
        else:
            role = "Employee"
        return role


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])
    confirm_password = serializers.CharField(required=True, validators=[MinLengthValidator(limit_value=10)])

    def validate_token(self, token):
        if ForgotPasswordLinkModel.objects.filter(activation_key=token).exists() is False:
            raise serializers.ValidationError('Invalid token.')
        else:
            return token
    
    def validate_confirm_password(self, confirm_password):
        new_pass = self.initial_data.get('new_password')
        if new_pass != confirm_password:
            raise serializers.ValidationError('New Password and Confirm Password are not equal.')
        return confirm_password
    
    def save(self):
        token = self.validated_data.get('token')
        new_pass = self.validated_data.get('new_password')
        forgot_password_obj = ForgotPasswordLinkModel.objects.get(activation_key=token)            
        user = User.objects.get(pk=forgot_password_obj.user.pk, is_active=True)
        user.set_password(new_pass)
        user.save()
        forgot_password_obj.delete()
        return user


class SchedulesTaskSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField(required=True)
    description = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    start_time = serializers.TimeField(required=True, format='%I:%M %p')
    end_time = serializers.TimeField(required=True)

    class Meta:
        model = TaskSchedulesModel
        fields = ('id', 'assigned_by', 'assigned_to', 'description',
                    'date', 'start_time', 'end_time',)
    
    def validate_employee_id(self, employee_id):
        if User.objects.filter(Q(is_staff=False) | Q(is_superuser=False), pk=employee_id, is_active=True).exists() is False:
            raise serializers.ValidationError('Invalid employee ID.')
        else:
            return employee_id
    
    def save(self):
        assigned_by = self.context.get('assigned_by')
        assigned_to = self.validated_data.get('employee_id')
        description = self.validated_data.get('description')
        date = self.context.get('date')
        start_time = self.context.get('start_time')
        end_time = self.context.get('end_time')
        schedule_object = TaskSchedulesModel.objects.create(
            assigned_by_id=assigned_by, assigned_to_id=assigned_to, description=description, 
            date=date, start_time=start_time, end_time=end_time
        )
        return schedule_object


class AssignToAnotherSchedulesTaskSerializer(serializers.Serializer):
    task_schedule_id = serializers.IntegerField(required=True)
    employee_id = serializers.IntegerField(required=True)

    class Meta:
        model = TaskSchedulesModel
    
    def validate_task_schedule_id(self, task_schedule_id):
        if TaskSchedulesModel.objects.filter(pk=task_schedule_id, is_delete=True).exists() is False:
            raise serializers.ValidationError('This task already assigned to another employee.')
        else:
            return task_schedule_id

    def validate_employee_id(self, employee_id):
        if User.objects.filter(Q(is_staff=False) | Q(is_superuser=False), pk=employee_id, is_active=True).exists() is False:
            raise serializers.ValidationError('Invalid employee ID.')
        else:
            return employee_id


class ViewScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSchedulesModel
        fields = ['id', 'assigned_by', 'assigned_to', 'description', 'date', 'start_time', 'end_time']

    def get_assigned_by(self, obj):
        return obj.assigned_by.get_full_name()
    
    def get_assigned_to(self, obj):
        return obj.assigned_to.get_full_name()
