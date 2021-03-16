from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from core_app import serializers
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from core_app.models import ForgotPasswordLinkModel, TasksModel, TaskSchedulesModel
from core_app.misc_files import send_forgot_password_link
from datetime import datetime


class LoginAPIView(ObtainAuthToken):
    def post(self, request):
        context: dict = dict()
        try:
            user_serializer = serializers.UserModelSerializer(data=request.data)
            if user_serializer.is_valid():
                email = user_serializer.data.get('email')
                password = user_serializer.data.get('password')
                if User.objects.filter(email=email, is_active=True).exists():
                    user_obj = User.objects.get(email=email, is_active=True)
                    user = authenticate(username=user_obj.username, password=password)
                    if user:
                        token, created = Token.objects.get_or_create(user=user)
                        context['status'] = True
                        context['data'] = {
                            'First Name': user_obj.first_name,
                            'last Name': user_obj.last_name,
                            'email': user_obj.email,
                            'token': token.key
                        }
                        context['message'] = 'Login Successfully.'
                    else:
                        context['status'] = False
                        context['error'] = {'password': ['Invalid password.']}    
                else:
                    context['status'] = False
                    context['error'] = {'email': ['Email not exists.']}
            else:
                context['status'] = False
                context['error'] = user_serializer.errors
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class LogoutAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            request.user.auth_token.delete()
            context['status'] = True
            context['message'] = 'User Logout.'
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class CreateAdminUserAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            admin_serializer = serializers.AdminEmployeeModelSerializer(data=request.data)
            if admin_serializer.is_valid():
                email = admin_serializer.data.get('email')
                password = admin_serializer.data.get('password')
                first_name = admin_serializer.data.get('first_name')
                last_name = admin_serializer.data.get('last_name')
                user_obj = User.objects.create(username=get_random_string(), email=email, first_name=first_name, last_name=last_name, is_staff=True, is_superuser=True, is_active=True)
                user_obj.set_password(password)
                user_obj.save()
                context['status'] = True
                context['data'] = {
                    'Id': user_obj.pk,
                    'First Name': user_obj.first_name,
                    'Last Name': user_obj.last_name,
                    'Email': user_obj.email,
                }
                context['message'] = 'Admin User Created.'    
            else:
                context['status'] = False
                context['error'] = admin_serializer.errors
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class CreateEmployeeUserAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            employee_serializer = serializers.AdminEmployeeModelSerializer(data=request.data)
            if employee_serializer.is_valid():
                email = employee_serializer.data.get('email')
                password = employee_serializer.data.get('password')
                first_name = employee_serializer.data.get('first_name')
                last_name = employee_serializer.data.get('last_name')
                user_obj = User.objects.create(username=get_random_string(), email=email, first_name=first_name, last_name=last_name, is_staff=False, is_superuser=False, is_active=True)
                user_obj.set_password(password)
                user_obj.save()
                context['status'] = True
                context['data'] = {
                    'Id': user_obj.pk,
                    'First Name': user_obj.first_name,
                    'Last Name': user_obj.last_name,
                    'Email': user_obj.email,
                }
                context['message'] = 'Employee User Created.'    
            else:
                context['status'] = False
                context['error'] = employee_serializer.errors
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class ChangeEmployeePasswordAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            set_password_serializer = serializers.SetNewPasswordSerializer(data=request.data)
            if set_password_serializer.is_valid():
                email = set_password_serializer.data.get('email')
                new_password = set_password_serializer.data.get('new_password')
                confirm_password = set_password_serializer.data.get('confirm_password')
                if User.objects.filter(email=email, is_active=True).exists():
                    user_obj = User.objects.get(email=email, is_active=True)
                    if user_obj.email != request.user.email:
                        if new_password == confirm_password:
                            user_obj.set_password(new_password)
                            user_obj.save()
                            context['status'] = True
                            context['data'] = {
                                'Id': user_obj.pk,
                                'First Name': user_obj.first_name,
                                'Last Name': user_obj.last_name,
                                'Email': user_obj.email,
                            }
                            context['message'] = 'Password Updated.'
                        else:
                            context['status'] = False
                            context['error'] = {'password_not_match': ['New password and confirm password not match.']}    
                    else:
                        context['status'] = False
                        context['error'] = {'invalid_access': ['You can not change your password from here.']}        
                else:
                    context['status'] = False
                    context['error'] = {'email': ['Email not exists.']}    
            else:
                context['status'] = False
                context['error'] = set_password_serializer.errors
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class UpdatePasswordAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            update_password_serializer = serializers.UpdatePasswordSerializer(data=request.data)
            if update_password_serializer.is_valid():
                email = update_password_serializer.data.get('email')
                current_password = update_password_serializer.data.get('current_password')
                new_password = update_password_serializer.data.get('new_password')
                confirm_password = update_password_serializer.data.get('confirm_password')
                if User.objects.filter(email=email, is_active=True).exists():
                    user_obj = User.objects.get(email=email, is_active=True)
                    if user_obj.email == request.user.email:
                        if check_password(current_password, user_obj.password):
                            if new_password == confirm_password:
                                user_obj.set_password(new_password)
                                user_obj.save()
                                context['status'] = True
                                context['data'] = {
                                    'Id': user_obj.pk,
                                    'First Name': user_obj.first_name,
                                    'Last Name': user_obj.last_name,
                                    'Email': user_obj.email,
                                }
                                context['message'] = 'Password Updated.'
                            else:
                                context['status'] = False
                                context['error'] = {'password_not_match': ['New password and confirm password not match.']}
                        else:
                            context['status'] = False
                            context['error'] = {'invalid_password': ['Invalid current password.']}    
                    else:
                        context['status'] = False
                        context['error'] = {'invalid_access': ['You can change only your own password.']}        
                else:
                    context['status'] = False
                    context['error'] = {'email': ['Email not exists.']}    
            else:
                context['status'] = False
                context['error'] = update_password_serializer.errors
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class ForgotPasswordAPIView(APIView):
    def post(self, request):
        context: dict = dict()
        try:
            forgot_password_serializer = serializers.ForgotPasswordSerializer(data=request.data)
            if forgot_password_serializer.is_valid():
                email = forgot_password_serializer.data.get('email')
                if User.objects.filter(email=email, is_active=True).exists():
                    user = User.objects.get(email=email, is_active=True)
                    activation_key = get_random_string(20)
                    obj, created = ForgotPasswordLinkModel.objects.update_or_create(
                        user=user,
                        activation_key=activation_key,
                    )
                    obj.save()
                    status = send_forgot_password_link(
                        username=user.get_full_name(),
                        token=activation_key,
                        to=user.email
                    )
                    if status:
                        context['status'] = True
                        context['message'] = 'Forgot password link is sent on your email.'
                    else:
                        context['status'] = False
                        context['message'] = 'Something went wrong, please check your network connection or contact to admin.'
                else:
                    context['status'] = False
                    context['error'] = 'Email not exists.'        
            else:
                context['status'] = False
                context['error'] = forgot_password_serializer.errors
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class ResetPasswordAPIView(APIView):
    def post(self, request):
        context: dict = dict()
        try:
            reset_password_serializer = serializers.ResetPasswordSerializer(data=request.data)
            if reset_password_serializer.is_valid():
                token = reset_password_serializer.data.get('token')
                new_password = reset_password_serializer.data.get('new_password')
                confirm_password = reset_password_serializer.data.get('confirm_password')
                if ForgotPasswordLinkModel.objects.filter(activation_key=token).exists():
                    forgot_password_obj = ForgotPasswordLinkModel.objects.get(activation_key=token)
                    if new_password == confirm_password:
                        user = User.objects.get(pk=forgot_password_obj.user.pk, is_active=True)
                        user.set_password(new_password)
                        user.save()
                        forgot_password_obj.delete()
                        context['status'] = False
                        context['message'] = 'Password updated successfully.'
                    else:
                        context['status'] = False
                        context['message'] = 'New password and confirm password not match.'
                else:
                    context['status'] = False
                    context['error'] = 'Invalid Token.'        
            else:
                context['status'] = False
                context['error'] = reset_password_serializer.errors
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class TasksAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        context: dict = dict()
        title = request.GET.get('title')
        if title:
            all_tasks = TasksModel.objects.filter(title__icontains=title, is_delete=False).order_by('start_date')
        else:
            all_tasks = TasksModel.objects.filter(is_delete=False).order_by('start_date')
        all_tasks_serializer = serializers.TasksSerializer(all_tasks, many=True)
        context['status'] = True
        context['data'] = all_tasks_serializer.data
        return Response(context)

    def post(self, request):
        context: dict = dict()
        try:
            print(request.data)
            task_serializer = serializers.TasksSerializer(data=request.data)
            if task_serializer.is_valid():
                title = task_serializer.data.get('title')
                start_date = datetime.strptime(task_serializer.data.get('start_date'), "%Y-%m-%dT%I:%M:%SZ")
                end_date = datetime.strptime(task_serializer.data.get('end_date'), "%Y-%m-%dT%I:%M:%SZ")
                task_obj = TasksModel.objects.create(
                    created_by=request.user,
                    title=title,
                    start_date=start_date,
                    end_date=end_date
                )
                task_obj.save()
                context['status'] = True
                context['message'] = 'Task Created.'
                context['data'] = {
                    'id': task_obj.pk,
                    'title': task_obj.title,
                    'start_date': task_obj.start_date,
                    'end_date': task_obj.end_date,
                    'created_by': task_obj.created_by.get_full_name()
                }
            else:
                context['status'] = False
                context['error'] = task_serializer.errors    
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)
    
    def delete(self, request, pk):
        context: dict = dict()
        try:
            task_obj = TasksModel.objects.get(pk=pk, is_delete=False)
            if TaskSchedulesModel.objects.filter(task=task_obj, is_delete=False).exists() is False:
                task_obj.is_delete = True
                task_obj.save()
                context['status'] = True
                context['message'] = 'Task Deleted.'
            else:
                context['status'] = False
                context['message'] = 'This Task is assigned to employee, please remove first from employee.'
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class TaskSchedulesAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            schedule_serializer = serializers.SchedulesSerializer(data=request.data)
            if schedule_serializer.is_valid():
                admin_id = request.user.pk
                employee_id = schedule_serializer.data.get('employee_id')
                task_id = schedule_serializer.data.get('task_id')
                if User.objects.filter(pk=admin_id, is_active=True).exists() is True:
                    admin_obj = User.objects.get(pk=admin_id, is_active=True)
                    if admin_obj.is_superuser:
                        if User.objects.filter(pk=employee_id, is_active=True).exists() is True:
                            employee_obj = User.objects.get(pk=employee_id, is_active=True)
                            if employee_obj.is_superuser is False and employee_obj.is_staff is False:
                                if TasksModel.objects.filter(pk=task_id, is_delete=False).exists() is True:
                                    task_obj = TasksModel.objects.get(pk=task_id, is_delete=False)
                                    if TaskSchedulesModel.objects.filter(assigned_to=employee_obj, date=task_obj.start_date.date(), start_time=task_obj.start_date.time(), end_end=task_obj.end_date.time(), is_delete=False).exists() is False:
                                        schedule_obj = TaskSchedulesModel.objects.create(
                                            assigned_by=admin_obj,
                                            assigned_to=employee_obj,
                                            task=task_obj,
                                            date=task_obj.start_date.date(),
                                            start_time=task_obj.start_date.time(),
                                            end_time=task_obj.end_date.time()
                                        )
                                        schedule_obj.save()
                                        context['status'] = True
                                        context['data'] = {
                                            'id': schedule_obj.pk,
                                            'assigned_by': schedule_obj.assigned_by.get_full_name(),
                                            'assigned_to': schedule_obj.assigned_to.get_full_name(),
                                            'task_title': schedule_obj.task.title,
                                            'date': schedule_obj.date,
                                            'start_time': schedule_obj.start_time,
                                            'end_time': schedule_obj.end_time
                                        }    
                                    else:
                                        context['status'] = False
                                        context['error'] = "Already assigned task in this slot."
                                else:
                                    context['status'] = False
                                    context['error'] = "Task not exists."
                            else:
                                context['status'] = False
                                context['error'] = "You are not an employee."        
                        else:
                            context['status'] = False
                            context['error'] = "Employee not exists."
                    else:
                        context['status'] = False
                        context['error'] = "You are not an admin."
                else:
                    context['status'] = False
                    context['error'] = "Admin not exists."
            else:
                context['status'] = False
                context['error'] = schedule_serializer.errors
        except Exception as e:
            context['status'] = True
            context['error'] = str(e)
        return Response(context)

    def delete(self, request, pk):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                schedule_obj = TaskSchedulesModel.objects.get(pk=pk, is_delete=False)
                schedule_obj.is_delete = True
                schedule_obj.save()
                context['status'] = True
                context['message'] = 'Schedule Deleted.'
            else:
                context['status'] = False
                context['message'] = "You don't have to permission to delete it."
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class ViewScheduleAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        context: dict = dict()
        try:
            all_schedule = TaskSchedulesModel.objects.filter(assigned_to=request.user, is_delete=False).order_by('-date')
            data_serializer = serializers.ViewScheduleSerializer(all_schedule, many=True)
            context['status'] = True
            context['data'] = data_serializer.data
        except Exception as e:
            context['status'] = True
            context['error'] = str(e)
        return Response(context)


class AdminViewAllScheduleAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        context: dict = dict()
        try:
            all_schedule = TaskSchedulesModel.objects.filter(assigned_by=request.user, is_delete=False).order_by('-date')
            data_serializer = serializers.ViewScheduleSerializer(all_schedule, many=True)
            context['status'] = True
            context['data'] = data_serializer.data
        except Exception as e:
            context['status'] = True
            context['error'] = str(e)
        return Response(context)
