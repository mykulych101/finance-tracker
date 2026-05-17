from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from transactions.api.filters import TransactionFilters
from transactions.api.serializers import ReadTransactionSerializer, WriteTransactionSerializer
from transactions.api.services import destroy_transaction
from transactions.models import Transaction


class TransactionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TransactionFilters

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return WriteTransactionSerializer
        return ReadTransactionSerializer

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__user=user).select_related("account")

    def destroy(self, request, *args, **kwargs):
        destroy_transaction(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)
