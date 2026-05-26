from django.urls import include, path

from analytics.api.router import router

urlpatterns = [path("api/", include(router.urls))]
