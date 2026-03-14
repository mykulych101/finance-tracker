from django.urls import include, path

from .api import router as api_router

urlpatterns = [
    # Include the API URLs under 'api/'
    path("api/", include((api_router.api_urlpatterns, "users_api"), namespace="users_api")),
]
