from django.urls import path
from .views import (
    MenuTreeView, ModuleListCreateView, ModuleDetailView,
    FunctionListCreateView, FunctionDetailView,
    AuthGroupListCreateView, AuthGroupDetailView,
    GroupFunctionListView, GroupFunctionBulkAssignView,
    GroupUsersView, GroupAssignUsersView, GroupRemoveUserView,
    MyPermissionsView, CheckPermissionView,
)

urlpatterns = [
    # Modules
    path('modules/',          ModuleListCreateView.as_view(),  name='module-list'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(),      name='module-detail'),

    # Functions
    path('functions/',          FunctionListCreateView.as_view(), name='function-list'),
    path('functions/<int:pk>/', FunctionDetailView.as_view(),     name='function-detail'),

    # Authorization Groups  (screenshots 1 & 2)
    path('groups/',          AuthGroupListCreateView.as_view(), name='group-list'),
    path('groups/<int:pk>/', AuthGroupDetailView.as_view(),     name='group-detail'),

    # Group → Functions  (screenshot 3)
    path('groups/<int:group_id>/functions/',         GroupFunctionListView.as_view(),       name='group-functions'),
    path('groups/<int:group_id>/functions/assign/',  GroupFunctionBulkAssignView.as_view(), name='group-functions-assign'),

    # Group → Users
    path('groups/<int:group_id>/users/',                          GroupUsersView.as_view(),       name='group-users'),
    path('groups/<int:group_id>/users/assign/',                   GroupAssignUsersView.as_view(), name='group-users-assign'),
    path('groups/<int:group_id>/users/<int:user_id>/remove/',     GroupRemoveUserView.as_view(),  name='group-users-remove'),

    # Permission helpers (for Vue frontend)
    path('my-permissions/',   MyPermissionsView.as_view(),   name='my-permissions'),
    path('check-permission/', CheckPermissionView.as_view(), name='check-permission'),

    path('menu-tree/', MenuTreeView.as_view(), name='menu-tree'),
]
