from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

admin.site.site_header = "NEWPROJECTNAME | Admin console"
# admin.site.enable_nav_sidebar = False


urlpatterns = [
    path("superadmin/doc/", include("django.contrib.admindocs.urls")),
    path("superadmin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # drf-spectacular URLs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Redoc UI
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", include("accounts.urls")),
    path("", include("core.urls")),
]

# Serve media files via Django
# import django.views.static
# urlpatterns += [
#     re_path(r'media/(?P<path>.*)$',
#         django.views.static.serve, {
#             'document_root': settings.MEDIA_ROOT,
#             'show_indexes': True,
#         }),
# ]


# For debug mode only
if settings.CONFIGURATION == "dev":
    # Turn on debug toolbar
    import debug_toolbar

    urlpatterns += [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ]
