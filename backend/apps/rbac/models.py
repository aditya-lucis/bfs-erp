"""
BFS ERP — RBAC Models

Hierarchy:
    Module (e.g. "General Ledger")
        └── Function (e.g. "GL > Journal Entry")
                └── FunctionAction (CREATE, READ, UPDATE, DELETE, APPROVE, PRINT, EXPORT)

    AuthorizationGroup  (e.g. "ACC-ACCMGR" / "Accounting Manager")
        └── GroupFunction  (which Functions + allowed Actions the group has)

    User  ──M2M──  AuthorizationGroup  (via UserAuthorizationGroup)
"""
from django.conf import settings
from django.db import models


class Module(models.Model):
    """Top-level ERP module visible in the Function List (screenshot: Commercial, General Ledger, etc.)"""
    code        = models.CharField(max_length=30, unique=True)
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order       = models.PositiveSmallIntegerField(default=0, help_text='Display order')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rbac_module'
        ordering = ['order', 'name']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'

    def __str__(self):
        return f"[{self.code}] {self.name}"


class Function(models.Model):
    """
    A single screen / operation inside a Module.
    e.g.  Module=General Ledger  →  Function=Journal Entry
    """
    module      = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='functions')
    parent      = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='children',
    )
    code        = models.CharField(max_length=50, unique=True)
    name        = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    url_path    = models.CharField(max_length=200, blank=True, help_text='Frontend route, e.g. /gl/journal-entry')
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rbac_function'
        ordering = ['module__order', 'order', 'name']

    def __str__(self):
        return f"{self.module.code} > {self.name}"
    
    @property
    def is_parent(self):
        return self.children.exists()


class ActionType(models.TextChoices):
    CREATE  = 'CREATE',  'Create'
    READ    = 'READ',    'Read / View'
    UPDATE  = 'UPDATE',  'Update'
    DELETE  = 'DELETE',  'Delete'
    APPROVE = 'APPROVE', 'Approve'
    PRINT   = 'PRINT',   'Print'
    EXPORT  = 'EXPORT',  'Export'


class AuthorizationGroup(models.Model):
    """
    Maps to a 'User Authorization Group' row in the screenshot.
    e.g.  group_name='ACC-ACCMGR'  description='ACCOUNTING MANAGER'
    """
    group_name  = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    status      = models.BooleanField(default=True, help_text='Active / Inactive')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='created_groups',
    )

    class Meta:
        db_table = 'rbac_authorization_group'
        ordering = ['group_name']
        verbose_name = 'Authorization Group'
        verbose_name_plural = 'Authorization Groups'

    def __str__(self):
        return f"{self.group_name} — {self.description}"


class GroupFunction(models.Model):
    """
    Junction: which Function an AuthorizationGroup can access,
    and which specific actions are allowed.
    Mirrors the checkbox list in screenshot 3.
    """
    authorization_group = models.ForeignKey(
        AuthorizationGroup,
        on_delete=models.CASCADE,
        related_name='group_functions',
    )
    function = models.ForeignKey(
        Function,
        on_delete=models.CASCADE,
        related_name='group_functions',
    )
    # Fine-grained action flags
    can_create  = models.BooleanField(default=False)
    can_read    = models.BooleanField(default=True)
    can_update  = models.BooleanField(default=False)
    can_delete  = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    can_print   = models.BooleanField(default=False)
    can_export  = models.BooleanField(default=False)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rbac_group_function'
        unique_together = ('authorization_group', 'function')
        verbose_name = 'Group Function'
        verbose_name_plural = 'Group Functions'

    def __str__(self):
        return f"{self.authorization_group.group_name} → {self.function.code}"


class UserAuthorizationGroup(models.Model):
    """
    M2M: User  ←→  AuthorizationGroup
    A user can belong to multiple groups (e.g. ENG-ENGSTF + DIR-DIR).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_auth_groups',
    )
    authorization_group = models.ForeignKey(
        AuthorizationGroup,
        on_delete=models.CASCADE,
        related_name='user_auth_groups',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_user_groups',
    )

    class Meta:
        db_table = 'rbac_user_authorization_group'
        unique_together = ('user', 'authorization_group')
        verbose_name = 'User Authorization Group'
        verbose_name_plural = 'User Authorization Groups'

    def __str__(self):
        return f"{self.user.username} → {self.authorization_group.group_name}"
