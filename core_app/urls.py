from django.urls import path
from core_app import views

urlpatterns = [
    path('login/', views.LoginAPIView.as_view()),
    path('logout/', views.LogoutAPIView.as_view()),
    path('create_admin/', views.CreateAdminUserAPIView.as_view()),
    path('create_employee/', views.CreateEmployeeUserAPIView.as_view()),
    path('set_password_by_admin/', views.ChangeEmployeePasswordAPIView.as_view()),
    path('update_password/', views.UpdatePasswordAPIView.as_view()),
    path('forgot_password/', views.ForgotPasswordAPIView.as_view()),
    path('create_new_password', views.ResetPasswordAPIView.as_view()),
    #   Endpoints for Tasks
    path('add_task/', views.TasksAPIView.as_view()),
    path('remove_task/<int:pk>', views.TasksAPIView.as_view()),
    path('all_tasks/', views.TasksAPIView.as_view()),
    #   Endpoints for Schedule
    path('assign_task/', views.TaskSchedulesAPIView.as_view()),
    path('view_all_schedule/', views.ViewScheduleAPIView.as_view()),
    path('admin_all_schedule/', views.AdminViewAllScheduleAPIView.as_view()),
    path('remove_schedule/<int:pk>', views.TaskSchedulesAPIView.as_view()),
]