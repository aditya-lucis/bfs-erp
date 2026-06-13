from django.urls import path
from . import views

urlpatterns = [
    # Budget Component
    path('budget-components/',
         views.BudgetComponentListView.as_view(),
         name='budget-component-list'),
    path('budget-components/<int:pk>/',
         views.BudgetComponentDetailView.as_view(),
         name='budget-component-detail'),

    # Template RAP
    path('templates-rap/',
         views.TemplateRAPListView.as_view(),
         name='template-rap-list'),
    path('templates-rap/<int:pk>/',
         views.TemplateRAPDetailView.as_view(),
         name='template-rap-detail'),

    # Template RAP Detail — FIX: flat path, no template_id in URL
    path('templates-rap-details/',
         views.TemplateRAPDetailListView.as_view(),
         name='template-rap-detail-list'),
    path('templates-rap-details/<int:pk>/',
         views.TemplateRAPDetailDetailView.as_view(),
         name='template-rap-detail-detail'),

    # Item Picker
    path('items/picker/',
         views.ItemPickerListView.as_view(),
         name='item-picker'),

    # Department Positions
    path('departments/<int:dept_id>/positions/',
          views.DepartmentPositionListView.as_view(),
          name='department-positions'),
]