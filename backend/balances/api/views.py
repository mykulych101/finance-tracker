from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from balances.api.serializers import BalanceRecordSerializer, LatestBalanceRecordSerializer
from balances.models import BalanceRecord


class BalanceRecordViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet
):
    serializer_class = BalanceRecordSerializer
    permission_classes = [IsAuthenticated]
    queryset = BalanceRecord.objects.all()

    def get_queryset(self):
        return (
            BalanceRecord.objects.filter(account__user=self.request.user)
            .select_related("account")
            .order_by("-date", "-created_at")
        )

    @action(detail=False, methods=["GET"], url_path="latest")
    def latest(self, request):
        latest_records = BalanceRecord.objects.latest_per_account(request.user)
        serializer = LatestBalanceRecordSerializer(latest_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
