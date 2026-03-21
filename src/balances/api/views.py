from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from balances.api.serializers import BalanceRecordSerializer
from balances.models import BalanceRecord


class BalanceRecordViewSet(ModelViewSet):
    serializer_class = BalanceRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            BalanceRecord.objects.filter(account__user=self.request.user)
            .select_related("account")
            .order_by("-date", "-created_at")
        )

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)
