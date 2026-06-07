from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User for BFS ERP.
    Authorization is handled by RBAC (AuthorizationGroup), not Django's built-in groups.
    """
    username        = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(unique=True)
    full_name       = models.CharField(max_length=150, blank=True)
    employee_id     = models.CharField(max_length=30, blank=True, null=True, unique=True)
    profile_photo   = models.ImageField(upload_to='users/photos/', blank=True, null=True)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)   # Django admin access

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table    = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering    = ['username']

    def __str__(self):
        return f"{self.username} ({self.full_name})"

    @property
    def authorization_groups(self):
        """Return all active RBAC groups this user belongs to."""
        return self.user_auth_groups.filter(
            authorization_group__status=True
        ).select_related('authorization_group')
