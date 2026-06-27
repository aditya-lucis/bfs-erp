
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.first()
c = APIClient()
c.force_authenticate(user=u)
res = c.get('/api/v1/purchase/po/', HTTP_HOST='localhost')
print('DATA:', res.data)

