
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.first()
c = APIClient()
c.force_authenticate(user=u)

endpoints = [
  '/api/v1/auth/users/',
  '/api/v1/purchase/vendors/',
  '/api/v1/projects/projects/',
  '/api/v1/projects/raps/',
  '/api/v1/organization/departments/'
]
for ep in endpoints:
    res = c.get(ep, HTTP_HOST='localhost')
    print(ep, res.status_code)

