from django.urls import include, path

from transactions.api.router import router

urlpatterns = [path("api/", include(router.urls))]
