from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionTypeViewSet, MasterBankViewSet

router = DefaultRouter()
router.register(r'transaction-type', TransactionTypeViewSet, basename='transaction-type')
router.register(r'master-bank', MasterBankViewSet, basename='master-bank')

urlpatterns = [
    path('', include(router.urls)),
]
