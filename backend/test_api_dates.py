
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User = get_user_model()
c = APIClient()

u_demo = User.objects.get(username='demo')
c.force_authenticate(user=u_demo)
res = c.get('/api/v1/purchase/po/', {'start_date': '2026-05-31', 'end_date': '2026-06-29', 'po_type': '', 'document_status': '', 'approval_status': ''}, HTTP_HOST='localhost')
print('DEMO STATUS:', res.status_code)
print('DEMO DATA:', res.data)

