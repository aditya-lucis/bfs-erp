from django.urls import path
from .views import (
    RAPTypeListView, RAPTypeDetailView, 
    ProjectListView, ProjectDetailView, ProjectActionView,
    ProjectTypeListView, ProjectTypeDetailView,
    ProjectCategoryListView, ProjectCategoryDetailView,
    RAPListView, RAPDetailView, RAPGetTemplateView, RAPSubmitView
)

urlpatterns = [
    path('rap-types/', RAPTypeListView.as_view(), name='rap-type-list'),
    path('rap-types/<int:pk>/', RAPTypeDetailView.as_view(), name='rap-type-detail'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/action/', ProjectActionView.as_view(), name='project-action'),
    path('project-types/', ProjectTypeListView.as_view(), name='project-type-list'),
    path('project-types/<int:pk>/', ProjectTypeDetailView.as_view(), name='project-type-detail'),
    path('project-categories/', ProjectCategoryListView.as_view(), name='project-category-list'),
    path('project-categories/<int:pk>/', ProjectCategoryDetailView.as_view(), name='project-category-detail'),
    
    path('raps/', RAPListView.as_view(), name='rap-list'),
    path('raps/<int:pk>/', RAPDetailView.as_view(), name='rap-detail'),
    path('raps/get-template/', RAPGetTemplateView.as_view(), name='rap-get-template'),
    path('raps/<int:pk>/submit/', RAPSubmitView.as_view(), name='rap-submit'),
]



