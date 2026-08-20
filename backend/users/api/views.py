from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.tasks import send_email
from users.utils import account_activation_token, build_activation_url

from .serializers import (
    ChangePasswordSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
    MyTokenObtainPairSerializer,
    UserProfileSerializer,
    UserSerializer,
)


@extend_schema(tags=["authentication"])
@extend_schema_view(
    post=extend_schema(
        request=UserSerializer,
        responses={201: UserSerializer},
    ),
)
class RegisterView(generics.CreateAPIView):
    """Create an account and email an activation link.

    No JWT tokens here on purpose: they would be useless until the email is
    confirmed, since every data endpoint sits behind `IsVerified`. Tokens are
    issued by `LoginView` once the account is activated.
    """

    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_email.delay(
            subject="Activate your account",
            template="email/activation_email.html",
            recipients=[user.email],
            context={"user_name": user.name, "activation_link": build_activation_url(user)},
        )


@extend_schema(
    tags=["authentication"],
    request=MyTokenObtainPairSerializer,
    responses=LoginResponseSerializer,
)
class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class LogoutView(APIView):
    # Deliberately not IsVerified: ending a session must work even if the
    # account loses its verified status while the token is still alive.
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=LogoutSerializer,
        responses={
            204: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Bad Request"),
        },
    )
    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            # Blacklist the refresh token
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (KeyError, TokenError):
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password updated successfully."),
            400: OpenApiResponse(description="Bad Request"),
        },
    )
    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # Set the new password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        parameters=[
            OpenApiParameter("uidb64", type=str, location=OpenApiParameter.PATH),
            OpenApiParameter("token", type=str, location=OpenApiParameter.PATH),
        ],
        responses={
            200: OpenApiResponse(description="Account activated successfully"),
            400: OpenApiResponse(description="Invalid activation link"),
        },
    )
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if account_activation_token.check_token(user, token):
                user.is_verified = True
                user.save()
                return Response({"detail": "Account activated successfully"}, status=status.HTTP_200_OK)
            return Response({"detail": "Activation link is invalid"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Activation link is invalid"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        responses=UserProfileSerializer,
    ),
    put=extend_schema(
        request=UserProfileSerializer,
        responses=UserProfileSerializer,
    ),
    patch=extend_schema(
        request=UserProfileSerializer,
        responses=UserProfileSerializer,
    ),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
