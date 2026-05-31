from django.urls import path
from .views import (
    CompanyDetailView, DepartmentTreeView,
    PositionListView, EmployeeListCreateView, EmployeeDetailView,
)

urlpatterns = [
    path('company/',              CompanyDetailView.as_view(),    name='company-detail'),
    path('departments/',          DepartmentTreeView.as_view(),   name='department-tree'),
    path('positions/',            PositionListView.as_view(),     name='position-list'),
    path('employees/',            EmployeeListCreateView.as_view(),name='employee-list'),
    path('employees/<int:pk>/',   EmployeeDetailView.as_view(),   name='employee-detail'),
]