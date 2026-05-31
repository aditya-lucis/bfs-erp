from django.contrib import admin
from .models import Module, Function, AuthorizationGroup, GroupFunction, UserAuthorizationGroup


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['order']


class FunctionInline(admin.TabularInline):
    model = Function
    extra = 0
    fields = ['code', 'name', 'url_path', 'order', 'is_active']


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'module', 'order', 'is_active']
    list_filter = ['module', 'is_active']
    search_fields = ['code', 'name']


class GroupFunctionInline(admin.TabularInline):
    model = GroupFunction
    extra = 0
    fields = [
        'function',
        'can_create', 'can_read', 'can_update', 'can_delete',
        'can_approve', 'can_print', 'can_export',
    ]


class UserAuthGroupInline(admin.TabularInline):
    model = UserAuthorizationGroup
    extra = 0
    fields = ['user', 'assigned_at', 'assigned_by']
    readonly_fields = ['assigned_at']


@admin.register(AuthorizationGroup)
class AuthorizationGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'group_name', 'description', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['group_name', 'description']
    inlines = [GroupFunctionInline, UserAuthGroupInline]


@admin.register(UserAuthorizationGroup)
class UserAuthorizationGroupAdmin(admin.ModelAdmin):
    list_display = ['user', 'authorization_group', 'assigned_at', 'assigned_by']
    list_filter = ['authorization_group']
    search_fields = ['user__username', 'authorization_group__group_name']
