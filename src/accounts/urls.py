from django.urls import include, path

from accounts.api.router import router

urlpatterns = [path("api/", include(router.urls))]
