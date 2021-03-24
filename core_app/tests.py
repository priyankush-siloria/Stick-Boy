from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from core_app import serializers
from core_app.models import TaskSchedulesModel
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework import status


class AdminAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin@mail.com", password="password@12")
        self.token, self.created = Token.objects.get_or_create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
    
    def test_create_admin(self):
        data = {'email': "test@test.com", 'password': "password@12", 'first_name': "test admin", 'last_name': "first"}
        response = self.client.post('/create_admin/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_employee(self):
        data = {'email': "employee@employee.com", 'password': "password@12", 'first_name': "test employee", 'last_name': "first"}
        response = self.client.post('/create_employee/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_change_employee_password(self):
        data = {'email': "employee@employee.com", 'new_password': "password@12", 'confirm_password': "password@12"}
        response = self.client.post('/set_password_by_admin/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_all_employee_list(self):
        response = self.client.get('/all_user_list/?role=employee')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_all_admin_list(self):
        response = self.client.get('/all_user_list/?role=admin')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_all_user_list(self):
        response = self.client.get('/all_user_list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_search_user_list(self):
        response = self.client.get('/search_user/?search=emp')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BasicAPITestCase(APITestCase):
    def test_login(self):
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
