from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from balances.api.filters import BalanceRecordFilters
from balances.api.serializers import BalanceRecordSerializer, LatestBalanceRecordSerializer
from balances.models import BalanceRecord


class BalanceRecordViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericViewSet
):
    serializer_class = BalanceRecordSerializer
    queryset = BalanceRecord.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = BalanceRecordFilters

    def get_queryset(self):
        if self.action == "latest":
            return BalanceRecord.objects.latest_per_account(self.request.user)
        return (
            BalanceRecord.objects.filter(account__user=self.request.user)
            .select_related("account")
            .order_by("-date", "-created_at")
        )

    @extend_schema(
        tags=["balances", "accounts"],
        request=BalanceRecordSerializer(many=True),
        responses={201: None},
        description="Bulk create balance records.",
        parameters=[],
    )
    @action(detail=False, methods=["POST"], url_path="bulk-create")
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(filters=True)
    @action(detail=False, methods=["GET"], url_path="latest")
    def latest(self, request):
        qs = self.filter_queryset(self.get_queryset())
        serializer = LatestBalanceRecordSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
