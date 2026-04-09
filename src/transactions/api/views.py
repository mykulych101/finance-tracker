from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from transactions.api.serializers import TransactionSerializer
from transactions.models import Transaction


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__user=user).select_related("account")

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)
