from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from core_app import serializers
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from core_app.models import ForgotPasswordLinkModel, TaskSchedulesModel
from core_app.misc_files import send_forgot_password_link
from datetime import datetime
from django.db.models import Q
from core_app.pagination import BasicPagination, PaginationHandlerMixin


class LoginAPIView(ObtainAuthToken):
    def post(self, request):
        context: dict = dict()
        try:
            user_serializer = serializers.UserModelSerializer(data=request.data)
            if user_serializer.is_valid():
                email = user_serializer.data.get('email')
                password = user_serializer.data.get('password')
                user_obj = User.objects.get(email=email, is_active=True)
                user = authenticate(username=user_obj.username, password=password)
                if user:
                    token, created = Token.objects.get_or_create(user=user)
                    context['status'] = True
                    context['data'] = {
                        'first_name': user_obj.first_name,
                        'last_name': user_obj.last_name,
                        'email': user_obj.email,
                        'token': token.key
                    }
                    context['message'] = 'Login Successfully.'
                else:
                    context['status'] = False
                    context['error'] = {'password': ['Invalid password.']}
                    context['data'] = []
            else:
                context['status'] = False
                context['error'] = user_serializer.errors
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class LogoutAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            request.user.auth_token.delete()
            context['status'] = True
            context['data'] = []
            context['message'] = 'User Logout.'
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class CreateAdminUserAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                admin_serializer = serializers.AdminEmployeeModelSerializer(data=request.data)
                if admin_serializer.is_valid():
                    admin_serializer.save()
                    context['status'] = True
                    context['data'] = admin_serializer.data
                    context['message'] = 'Admin User Created.'    
                else:
                    context['status'] = False
                    context['error'] = admin_serializer.errors
                    context['data'] = []
            else:
                context['status'] = False
                context['error'] = "You do not have permission to create an administrator."
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class CreateEmployeeUserAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                employee_serializer = serializers.AdminEmployeeModelSerializer(data=request.data, context={'is_employee': True})
                if employee_serializer.is_valid():
                    employee_serializer.save()
                    context['status'] = True
                    context['data'] = employee_serializer.data
                    context['message'] = 'Employee User Created.'
                else:
                    context['status'] = False
                    context['error'] = employee_serializer.errors
                    context['data'] = []
            else:
                context['status'] = False
                context['error'] = "You do not have permission to create an administrator."
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class ChangeEmployeePasswordAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                set_password_serializer = serializers.SetNewPasswordSerializer(data=request.data)
                if set_password_serializer.is_valid():
                    email = set_password_serializer.data.get('email')
                    if email != request.user.email:
                        set_password_serializer.save()
                        context['status'] = True
                        context['data'] = []
                        context['message'] = 'Password Updated.'  
                    else:
                        context['status'] = False
                        context['error'] = {'invalid_access': ['You can not change your password from here.']}
                        context['data'] = []           
                else:
                    context['status'] = False
                    context['error'] = set_password_serializer.errors
                    context['data'] = []
            else:
                context['status'] = False
                context['error'] = "You do not have permission to change the password."
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class UpdatePasswordAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            update_password_serializer = serializers.UpdatePasswordSerializer(data=request.data, context={'pk': request.user.pk})
            if update_password_serializer.is_valid():
                update_password_serializer.save()
                context['status'] = True
                context['data'] = []
                context['message'] = 'Password Updated.' 
            else:
                context['status'] = False
                context['error'] = update_password_serializer.errors
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class AllUserListAPIView(APIView, PaginationHandlerMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserListSerializer
    pagination_class = BasicPagination

    def get(self, request):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                get_role = request.GET.get('role')
                if get_role:
                    if get_role.lower() == 'employee':
                        all_users = User.objects.filter(Q(is_superuser=False) | Q(is_staff=False), is_active=True).order_by('-date_joined')
                    else:
                        all_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True), is_active=True).order_by('-date_joined')
                else:
                    all_users = User.objects.filter(is_active=True).order_by('-date_joined')

                page = self.paginate_queryset(all_users)
                if page is not None:
                    serializer_data = self.get_paginated_response(self.serializer_class(page, many=True).data)
                else:
                    serializer_data = self.serializer_class(all_users, many=True)
                context['status'] = True
                context['data'] = serializer_data.data
                context['message'] = 'User List.'
            else:
                context['status'] = False
                context['error'] = "You do not have permission."
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class SearchUserListAPIView(APIView, PaginationHandlerMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.UserListSerializer
    pagination_class = BasicPagination

    def get(self, request):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                get_search = request.GET.get('search')
                if get_search:
                    all_users = User.objects.filter(Q(first_name__icontains=get_search) | Q(last_name__icontains=get_search) | Q(email__icontains=get_search), is_active=True).order_by('-date_joined')
                else:
                    all_users = User.objects.filter(is_active=True).order_by('-date_joined')

                page = self.paginate_queryset(all_users)
                if page is not None:
                    serializer_data = self.get_paginated_response(self.serializer_class(page, many=True).data)
                else:
                    serializer_data = self.serializer_class(all_users, many=True)
                context['status'] = True
                context['data'] = serializer_data.data
                context['message'] = 'User List.'
            else:
                context['status'] = False
                context['error'] = "You do not have permission."
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
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
                        context['data'] = []
                    else:
                        context['status'] = False
                        context['message'] = 'Something went wrong, please check your network connection or contact to admin.'
                        context['data'] = []
                else:
                    context['status'] = False
                    context['error'] = 'Email not exists.'
                    context['data'] = []        
            else:
                context['status'] = False
                context['error'] = forgot_password_serializer.errors
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class ResetPasswordAPIView(APIView):
    def post(self, request):
        context: dict = dict()
        try:
            reset_password_serializer = serializers.ResetPasswordSerializer(data=request.data)
            if reset_password_serializer.is_valid():
                new_password = reset_password_serializer.data.get('new_password')
                confirm_password = reset_password_serializer.data.get('confirm_password')
                reset_password_serializer.save()
                context['status'] = True
                context['message'] = 'Password updated successfully.'
                context['data']  = []            
            else:
                context['status'] = False
                context['error'] = reset_password_serializer.errors
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
        return Response(context)


class ScheduleTasksAPIView(APIView, PaginationHandlerMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ViewScheduleSerializer
    pagination_class = BasicPagination

    def get(self, request):
        context: dict = dict()
        title = request.GET.get('title')
        if title:
            all_tasks = TaskSchedulesModel.objects.filter(title__icontains=title, is_delete=False).order_by('date')
        else:
            all_tasks = TaskSchedulesModel.objects.filter(is_delete=False).order_by('date')
        page = self.paginate_queryset(all_tasks)
        if page is not None:
            all_tasks_serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            all_tasks_serializer = self.serializer_class(all_tasks, many=True)
        context['status'] = True
        context['data'] = all_tasks_serializer.data
        return Response(context)

    def post(self, request):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                employee_id = request.data.get('employee_id')
                description = request.data.get('description')
                date = request.data.get('date')
                start_time = request.data.get('start_time')
                end_time = request.data.get('end_time')
                date = datetime.strptime(date, "%Y-%m-%d").date()
                start_time = datetime.strptime(start_time, "%I:%M %p").time()
                end_time = datetime.strptime(end_time, "%I:%M %p").time()
                context_data = {
                    'assigned_by': request.user.pk,
                    'date': date,
                    'start_time': start_time,
                    'end_time': end_time,
                }
                schedule_task_serializer = serializers.SchedulesTaskSerializer(data=request.data, context=context_data)
                if schedule_task_serializer.is_valid():   
                    if TaskSchedulesModel.objects.filter(assigned_to_id=employee_id, date=date, end_time__gt=start_time, is_delete=False).exists() is False:
                        schedule_task_serializer.save()
                        context['status'] = True
                        context['data'] = schedule_task_serializer.data
                        context['message'] = 'Schedule Assigned.'
                    else:
                        context['status'] = False
                        context['error'] = "This time slot already occupied in this date. Please choose different time slot on this date."
                        context['data'] = []
                else:
                    context['status'] = False
                    context['error'] = schedule_task_serializer.errors
                    context['data'] = []
            else:
                context['status'] = False
                context['error'] = "You do not have permission to assign the schedule."
                context['data'] = []    
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)
    
    def delete(self, request, pk):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                task_obj = TaskSchedulesModel.objects.get(pk=pk, is_delete=False)
                task_obj.is_delete = True
                task_obj.save()
                context['status'] = True
                context['message'] = 'Task Schedule Removed.'
                context['data'] = []
            else:
                context['status'] = False
                context['error'] = "You do not have permission to assign the schedule."
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class AssignTaskScheduleToAnotherEmployee(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context: dict = dict()
        try:
            if request.user.is_superuser:
                task_schedule_id = request.data.get('task_schedule_id')
                employee_id = request.data.get('employee_id')
                serializer_data = serializers.AssignToAnotherSchedulesTaskSerializer(data=request.data)
                if serializer_data.is_valid():
                    schedule_data = TaskSchedulesModel.objects.get(pk=task_schedule_id, is_delete=True)
                    schedule_data.assigned_by_id = request.user.pk
                    schedule_data.assigned_to_id = employee_id
                    schedule_data.is_delete = False
                    schedule_data.save()
                    context['status'] = True
                    context['data'] = {
                        'id': schedule_data.pk,
                        'assigned_by': schedule_data.assigned_by.get_full_name(),
                        'assigned_to': schedule_data.assigned_to.get_full_name(),
                        'description': schedule_data.description,
                        'date': schedule_data.date,
                        'start_time': schedule_data.start_time,
                        'end_time': schedule_data.end_time,
                    }
                    context['message'] = 'Schedule Assigned.'
                else:
                    context['status'] = False
                    context['error'] = serializer_data.errors
                    context['data'] = []
            else:
                context['status'] = False
                context['error'] = "You do not have permission to assign the schedule."
                context['data'] = []
        except Exception as e:
            context['status'] = False
            context['error'] = str(e)
            context['data'] = []
        return Response(context)


class EmployeeTaskScheduleAPIView(APIView, PaginationHandlerMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ViewScheduleSerializer
    pagination_class = BasicPagination

    def get(self, request):
        context: dict = dict()
        try:
            start_datetime = request.GET.get('start_datetime')
            end_datetime = request.GET.get('end_datetime')
            sort_by_start_date = request.GET.get('sort_by_start_date')
            if sort_by_start_date:
                if sort_by_start_date == '1' or sort_by_start_date == 1:
                    sort_by_start_date = True
                else:
                    sort_by_start_date = False     
            if start_datetime and end_datetime:
                start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %I:%M %p")
                end_datetime = datetime.strptime(end_datetime, "%Y-%m-%d %I:%M %p")
                all_schedule = TaskSchedulesModel.objects.filter(assigned_to=request.user, date=start_datetime.date(), start_time__gte=start_datetime.time(), end_time__lte=end_datetime.time(), is_delete=False).order_by('-date')
            elif sort_by_start_date:
                all_schedule = TaskSchedulesModel.objects.filter(assigned_to=request.user, is_delete=False).order_by('-date')
            else:    
                all_schedule = TaskSchedulesModel.objects.filter(assigned_to=request.user, is_delete=False).order_by('-date')
            page = self.paginate_queryset(all_schedule)
            if page is not None:
                data_serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
            else:
                data_serializer = self.serializer_class(all_schedule, many=True)
            context['status'] = True
            context['data'] = data_serializer.data
        except Exception as e:
            context['status'] = True
            context['error'] = str(e)
        return Response(context)

# class TaskSchedulesAPIView(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def post(self, request):
#         context: dict = dict()
#         try:
#             schedule_serializer = serializers.SchedulesSerializer(data=request.data)
#             if schedule_serializer.is_valid():
#                 admin_id = request.user.pk
#                 employee_id = schedule_serializer.data.get('employee_id')
#                 task_id = schedule_serializer.data.get('task_id')
#                 if User.objects.filter(pk=admin_id, is_active=True).exists() is True:
#                     admin_obj = User.objects.get(pk=admin_id, is_active=True)
#                     if admin_obj.is_superuser:
#                         if User.objects.filter(pk=employee_id, is_active=True).exists() is True:
#                             employee_obj = User.objects.get(pk=employee_id, is_active=True)
#                             if employee_obj.is_superuser is False and employee_obj.is_staff is False:
#                                 if TasksModel.objects.filter(pk=task_id, is_delete=False).exists() is True:
#                                     task_obj = TasksModel.objects.get(pk=task_id, is_delete=False)
#                                     if TaskSchedulesModel.objects.filter(assigned_to=employee_obj, date=task_obj.start_date.date(), start_time=task_obj.start_date.time(), end_end=task_obj.end_date.time(), is_delete=False).exists() is False:
#                                         schedule_obj = TaskSchedulesModel.objects.create(
#                                             assigned_by=admin_obj,
#                                             assigned_to=employee_obj,
#                                             task=task_obj,
#                                             date=task_obj.start_date.date(),
#                                             start_time=task_obj.start_date.time(),
#                                             end_time=task_obj.end_date.time()
#                                         )
#                                         schedule_obj.save()
#                                         context['status'] = True
#                                         context['data'] = {
#                                             'id': schedule_obj.pk,
#                                             'assigned_by': schedule_obj.assigned_by.get_full_name(),
#                                             'assigned_to': schedule_obj.assigned_to.get_full_name(),
#                                             'task_title': schedule_obj.task.title,
#                                             'date': schedule_obj.date,
#                                             'start_time': schedule_obj.start_time,
#                                             'end_time': schedule_obj.end_time
#                                         }    
#                                     else:
#                                         context['status'] = False
#                                         context['error'] = "Already assigned task in this slot."
#                                 else:
#                                     context['status'] = False
#                                     context['error'] = "Task not exists."
#                             else:
#                                 context['status'] = False
#                                 context['error'] = "You are not an employee."        
#                         else:
#                             context['status'] = False
#                             context['error'] = "Employee not exists."
#                     else:
#                         context['status'] = False
#                         context['error'] = "You are not an admin."
#                 else:
#                     context['status'] = False
#                     context['error'] = "Admin not exists."
#             else:
#                 context['status'] = False
#                 context['error'] = schedule_serializer.errors
#         except Exception as e:
#             context['status'] = True
#             context['error'] = str(e)
#         return Response(context)

#     def delete(self, request, pk):
#         context: dict = dict()
#         try:
#             if request.user.is_superuser:
#                 schedule_obj = TaskSchedulesModel.objects.get(pk=pk, is_delete=False)
#                 schedule_obj.is_delete = True
#                 schedule_obj.save()
#                 context['status'] = True
#                 context['message'] = 'Schedule Deleted.'
#             else:
#                 context['status'] = False
#                 context['message'] = "You don't have to permission to delete it."
#         except Exception as e:
#             context['status'] = False
#             context['error'] = str(e)
#         return Response(context)





# class AdminViewAllScheduleAPIView(APIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         context: dict = dict()
#         try:
#             all_schedule = TaskSchedulesModel.objects.filter(assigned_by=request.user, is_delete=False).order_by('-date')
#             data_serializer = serializers.ViewScheduleSerializer(all_schedule, many=True)
#             context['status'] = True
#             context['data'] = data_serializer.data
#         except Exception as e:
#             context['status'] = True
#             context['error'] = str(e)
#         return Response(context)
