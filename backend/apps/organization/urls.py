from django.urls import path
from .views import (
    CompanyDetailView, DepartmentDetailView, DepartmentPositionDetailView, 
    DepartmentPositionListView, DepartmentTreeView, EmployeeSignatureView,
    PositionListView, EmployeeListCreateView, EmployeeDetailView,
)

urlpatterns = [
    path('company/',              CompanyDetailView.as_view(),    name='company-detail'),
    path('departments/',          DepartmentTreeView.as_view(),   name='department-tree'),
    path('positions/',            PositionListView.as_view(),     name='position-list'),
    path('employees/',            EmployeeListCreateView.as_view(),name='employee-list'),
    path('employees/',                        EmployeeListCreateView.as_view()),
    path('employees/<int:pk>/',               EmployeeDetailView.as_view()),
    path('employees/<int:pk>/signature/',     EmployeeSignatureView.as_view()),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    
    path('departments/<int:dept_id>/positions/',
         DepartmentPositionListView.as_view(),
         name='department-positions'),

    path('departments/<int:dept_id>/positions/<int:pk>/',
         DepartmentPositionDetailView.as_view(),
         name='department-position-detail'),
]