from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionTypeViewSet

router = DefaultRouter()
router.register(r'transaction-type', TransactionTypeViewSet, basename='transaction-type')

urlpatterns = [
    path('', include(router.urls)),
]
