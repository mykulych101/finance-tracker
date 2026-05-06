from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from accounts.api.serializers import AccountSerializer
from accounts.models import Account


class AccountViewSet(ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
