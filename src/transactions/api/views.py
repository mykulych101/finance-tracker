from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from transactions.api.serializers import ReadTransactionSerializer, WriteTransactionSerializer
from transactions.models import Transaction


class TransactionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return WriteTransactionSerializer
        return ReadTransactionSerializer

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__user=user).select_related("account")
