from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionTypeViewSet, MasterBankViewSet, PaymentToViewSet

router = DefaultRouter()
router.register(r'transaction-type', TransactionTypeViewSet, basename='transaction-type')
router.register(r'master-bank', MasterBankViewSet, basename='master-bank')
router.register(r'payment-to', PaymentToViewSet, basename='payment-to')

urlpatterns = [
    path('', include(router.urls)),
]
