from django.urls import include, path

from balances.api.router import router

urlpatterns = [path("api/", include(router.urls))]
