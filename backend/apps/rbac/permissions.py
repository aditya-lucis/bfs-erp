"""
Custom DRF Permission classes for BFS ERP RBAC.

Usage in a ViewSet:
    from apps.rbac.permissions import HasFunctionPermission

    class JournalEntryViewSet(ModelViewSet):
        permission_classes = [IsAuthenticated, HasFunctionPermission]
        rbac_function_code = 'GL-JOURNAL-ENTRY'

    # The class will automatically map HTTP method → action flag:
    #   GET    → can_read
    #   POST   → can_create
    #   PUT/PATCH → can_update
    #   DELETE → can_delete
"""
from rest_framework.permissions import BasePermission

# Maps HTTP method → GroupFunction field
METHOD_ACTION_MAP = {
    'GET':    'can_read',
    'HEAD':   'can_read',
    'OPTIONS':'can_read',
    'POST':   'can_create',
    'PUT':    'can_update',
    'PATCH':  'can_update',
    'DELETE': 'can_delete',
}


def get_user_permissions(user):

    if not user or not user.is_authenticated:
        return {}

    if hasattr(user, '_rbac_permissions_cache'):
        return user._rbac_permissions_cache
    
     # ── Superuser: beri akses penuh ke semua function aktif ──────────────────
    if user.is_superuser:
        from apps.rbac.models import Function
        all_actions = {
            'can_create':  True,
            'can_read':    True,
            'can_update':  True,
            'can_delete':  True,
            'can_approve': True,
            'can_print':   True,
            'can_export':  True,
        }
        perms = {
            fn.code: all_actions
            for fn in Function.objects.filter(is_active=True).only('code')
        }
        user._rbac_permissions_cache = perms
        return perms
    
    # ── Regular user: OR-merge dari semua group ───────────────────────────────
    from apps.rbac.models import GroupFunction

    # Get all GroupFunction rows for groups this user belongs to
    gf_qs = GroupFunction.objects.filter(
        authorization_group__user_auth_groups__user=user,
        authorization_group__status=True,
        function__is_active=True,
        function__module__is_active=True,
    ).values(
        'function__code',
        'can_create', 'can_read', 'can_update', 'can_delete',
        'can_approve', 'can_print', 'can_export',
    )

    perms = {}
    for row in gf_qs:
        code = row['function__code']
        if code not in perms:
            perms[code] = { k: False for k in (
                'can_create',
                'can_read',
                'can_update',
                'can_delete',
                'can_approve',
                'can_print',
                'can_export',
            )}
        # OR-merge across multiple groups
        for action in perms[code]:
            if row[action]:
                perms[code][action] = True

    user._rbac_permissions_cache = perms
    return perms


def user_has_permission(user, function_code: str, action: str) -> bool:
    """Utility — check a single user/function/action triple."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perms = get_user_permissions(user)
    
    normalized_codes = [function_code]
    if isinstance(function_code, str):
        if function_code.startswith('INV-'):
            normalized_codes.append(function_code.replace('INV-', 'INVENTORY-', 1))
        if function_code in ('SALES-CUSTOMER', 'SALES-CUSTOMERS', 'COMMERCIAL-CUSTOMERS'):
            normalized_codes.extend(['SALES-CUSTOMER', 'SALES-CUSTOMERS', 'COMMERCIAL-CUSTOMERS'])
        if function_code == 'BUDGET-COMPONENT':
            normalized_codes.append('FINANCE-BUDGET-COMPONENT')
            
        period_map = {
            'GL-PERIOD-ANNUAL': 'SETTINGS-ANNUAL-ACCOUNTING-PERIOD',
            'GL-PERIOD-QUARTER': 'SETTINGS-QUARTER-ACCOUNTING-PERIOD',
            'GL-PERIOD-MONTHLY': 'SETTINGS-MONTHLY-ACCOUNTING-PERIOD',
            'GL-PERIOD-ACCOUNTING': 'SETTINGS-ACCOUNTING-PERIOD',
            'GL-PERIOD-LOG': 'SETTINGS-PERIOD-ACTIVITY-LOG',
        }
        if function_code in period_map:
            normalized_codes.append(period_map[function_code])
        reverse_period_map = {v: k for k, v in period_map.items()}
        if function_code in reverse_period_map:
            normalized_codes.append(reverse_period_map[function_code])
            
        if function_code in ('INV-UNIT-MEASUREMENT', 'INVENTORY-UNIT-MEASUREMENT', 'SETTINGS-UNIT-MEASUREMENT'):
            normalized_codes.extend(['INV-UNIT-MEASUREMENT', 'INVENTORY-UNIT-MEASUREMENT', 'SETTINGS-UNIT-MEASUREMENT'])
        if function_code in ('GL-CHART-OF-ACCOUNT', 'GL-CHART-OF-ACCOUNTS', 'GL-CHART-OF-ACCOUNTS-2'):
            normalized_codes.extend(['GL-CHART-OF-ACCOUNT', 'GL-CHART-OF-ACCOUNTS', 'GL-CHART-OF-ACCOUNTS-2'])
            
    has_perm = False
    for code in normalized_codes:
        if perms.get(code, {}).get(action, False):
            has_perm = True
            break
            
    return has_perm


class HasFunctionPermission(BasePermission):
    """
    View-level permission.
    The View/ViewSet must declare:
        rbac_function_code = 'MODULE-FUNCTION-CODE'

    Optionally override:
        rbac_action_map = {'GET': 'can_read', 'POST': 'can_create', ...}
    """
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        function_code = None
        if hasattr(view, 'get_rbac_function_code'):
            function_code = view.get_rbac_function_code()
        else:
            function_code = getattr(view, 'rbac_function_code', None)
            
        if not function_code:
            # No code declared → deny by default (fail-safe)
            return False

        action_map = getattr(view, 'rbac_action_map', METHOD_ACTION_MAP)
        action = action_map.get(request.method, 'can_read')

        return user_has_permission(request.user, function_code, action)


class IsAdminGroupMember(BasePermission):
    """
    Allows access only to users that are superuser OR belong to any
    group whose group_name starts with 'ADM'.
    Used to protect RBAC management endpoints.
    """
    message = 'Admin group membership required.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.user_auth_groups.filter(
            authorization_group__group_name__startswith='ADM',
            authorization_group__status=True,
        ).exists()

def invalidate_permission_cache(user):
    """
    Panggil ini setiap kali GroupFunction atau UserAuthGroup diubah.
    """
    if hasattr(user, '_rbac_permissions_cache'):
        del user._rbac_permissions_cache