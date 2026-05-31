# config/settings_test.py
from .settings import *

# Override ke SQLite in-memory supaya test gak butuh PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   ':memory:',
    }
}

# Hash password lebih cepat waktu test
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Matiin debug pas test
DEBUG = False