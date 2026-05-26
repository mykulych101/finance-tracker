from rest_framework.routers import DefaultRouter

from analytics.api.views import AnalyticsViewSet

router = DefaultRouter()
router.register(r"analytics", AnalyticsViewSet, basename="analytics")

urlpatterns = router.urls
