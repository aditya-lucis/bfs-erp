
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User = get_user_model()
c = APIClient()

u_aditya = User.objects.get(username='adityalucis')
c.force_authenticate(user=u_aditya)
res = c.get('/api/v1/organization/departments/', HTTP_HOST='localhost')
print('ADITYA STATUS:', res.status_code)
print('ADITYA DATA:', res.data)

