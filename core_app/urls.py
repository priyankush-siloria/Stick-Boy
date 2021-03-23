from django.urls import path
from core_app import views

urlpatterns = [
    path('login/', views.LoginAPIView.as_view()),
    path('logout/', views.LogoutAPIView.as_view()),
    path('create_admin/', views.CreateAdminUserAPIView.as_view()),
    path('create_employee/', views.CreateEmployeeUserAPIView.as_view()),
    path('set_password_by_admin/', views.ChangeEmployeePasswordAPIView.as_view()),
    path('update_password/', views.UpdatePasswordAPIView.as_view()),
    path('all_user_list/', views.AllUserListAPIView.as_view()),
    path('search_user/', views.SearchUserListAPIView.as_view()),
    path('forgot_password/', views.ForgotPasswordAPIView.as_view()),
    path('create_new_password', views.ResetPasswordAPIView.as_view()),
    path('assign_schedule_task/', views.ScheduleTasksAPIView.as_view()),
    path('remove_task_schedule/<int:pk>/', views.ScheduleTasksAPIView.as_view()),
    path('assign_task_schedule_to_another/', views.AssignTaskScheduleToAnotherEmployee.as_view()),
    path('view_all_schedule/', views.ScheduleTasksAPIView.as_view()),
    path('employee_all_schedule/', views.EmployeeTaskScheduleAPIView.as_view()),
    # path('admin_all_schedule/', views.AdminViewAllScheduleAPIView.as_view()),
    # path('remove_schedule/<int:pk>', views.TaskSchedulesAPIView.as_view()),
]