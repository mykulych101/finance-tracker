from django.urls import path

from accounts.api import views

api_urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("activate/<uidb64>/<token>/", views.ActivateAccountView.as_view(), name="activate"),
]
