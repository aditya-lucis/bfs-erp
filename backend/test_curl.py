
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
u = User.objects.get(username='adityalucis')
refresh = RefreshToken.for_user(u)
access_token = str(refresh.access_token)

import subprocess
cmd = [
    'curl', '-s', '-H', f'Authorization: Bearer {access_token}', 
    'http://localhost:8000/api/v1/purchase/po/?search=&po_type=&document_status=&approval_status=&start_date=2026-05-31&end_date=2026-06-29'
]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)

