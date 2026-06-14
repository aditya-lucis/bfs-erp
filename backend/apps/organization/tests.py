from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.authentication.models import User
from apps.organization.models import Company, Department, Position, Employee

class EmployeePermissionsTestCase(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            company_code='TST',
            company_name='Test Company'
        )
        self.department = Department.objects.create(
            company=self.company,
            code='DEPT-A',
            name='Department A'
        )
        self.position = Position.objects.create(
            department=self.department,
            code='POS-A',
            name='Position A'
        )
        self.user = User.objects.create_user(
            username='regularuser',
            password='testpassword123',
            email='user@test.com'
        )
        self.employee = Employee.objects.create(
            user=self.user,
            position=self.position,
            employee_id='EMP001',
            full_name='Regular User',
            email='user@test.com',
            status='active'
        )

    def test_regular_user_can_list_employees(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_create_employee(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('employee-list')
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'full_name': 'New User',
            'password': 'password123',
            'position': self.position.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
