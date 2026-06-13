from rest_framework import permissions


class CanManageTemplateRAP(permissions.BasePermission):
    """
    Permission untuk Template RAP:
    - Superuser: boleh semua
    - Employee: hanya boleh manage template RAP untuk budget component
      yang position-nya sama dengan position employee yang login
    """
    message = 'Anda tidak memiliki akses untuk mengelola Template RAP di posisi ini.'

    def has_permission(self, request, view):
        # Superuser bypass
        if request.user.is_superuser:
            return True

        # Check if user has employee profile
        if not hasattr(request.user, 'employee_profile') or not request.user.employee_profile:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Superuser bypass
        if request.user.is_superuser:
            return True

        # Get employee's position
        employee = request.user.employee_profile
        employee_position = employee.position

        # obj could be TemplateRAP or BudgetComponent
        if hasattr(obj, 'budget_component'):
            # obj is TemplateRAP
            target_position = obj.budget_component.position
        elif hasattr(obj, 'position'):
            # obj is BudgetComponent
            target_position = obj.position
        else:
            return False

        # Must match position
        return employee_position == target_position