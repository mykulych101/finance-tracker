import tablib
from django.db.transaction import atomic
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.api.serializers import AccountSerializer, AccountSlimSerializer
from accounts.models import Account
from transactions.api.resources import TransactionResource


class AccountViewSet(ModelViewSet):
    serializer_class = AccountSerializer
    autocomplete_serializer_class = AccountSlimSerializer
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    @extend_schema(responses={200: AccountSlimSerializer(many=True)})
    @action(detail=False, methods=["GET"], serializer_class=AccountSlimSerializer)
    def autocomplete(self, request, *args, **kwargs):
        return self.list(self.request, *args, **kwargs)

    @atomic
    @extend_schema(
        request={
            "multipart/form-data": {"type": "object", "properties": {"file": {"type": "string", "format": "binary"}}}
        },
        responses={200: None},
    )
    @action(detail=True, methods=["POST"], parser_classes=[MultiPartParser])
    def import_transaction(self, request, *args, **kwargs):
        account = self.get_object()
        file = request.FILES.get("file")
        if not file:
            raise ValidationError({"error": "No file provided"})
        try:
            book = tablib.Dataset().load(file.read().decode("utf-8"), format="csv")
        except (tablib.UnsupportedFormat, tablib.InvalidDimensions, ValueError, IndexError) as e:
            raise ValidationError({"error": f"Invalid file format: {e}"})

        resource = TransactionResource(account=account)
        result = resource.import_data(book, dry_run=False)
        if result.has_errors() or result.has_validation_errors():
            raise ValidationError({"error": "CSV contains invalid rows"})
        return Response({"imported": result.total_rows}, status=status.HTTP_200_OK)
