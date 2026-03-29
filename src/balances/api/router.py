from rest_framework.routers import DefaultRouter

from balances.api.views import BalanceRecordViewSet

router = DefaultRouter()
router.register(r"balances", BalanceRecordViewSet, basename="balances")

urlpatterns = router.urls
