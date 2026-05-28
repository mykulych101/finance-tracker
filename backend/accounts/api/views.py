import hashlib

import tablib
from django.db import IntegrityError
from django.db.transaction import atomic
from drf_spectacular.utils import extend_schema
from import_export.results import RowResult
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.api.serializers import AccountSerializer, AccountSlimSerializer, WriteAccountSerializer
from accounts.models import Account
from transactions.api.resources import TransactionResource
from transactions.models import TransactionImport


class AccountViewSet(ModelViewSet):
    autocomplete_serializer_class = AccountSlimSerializer
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return WriteAccountSerializer
        return AccountSerializer

    def get_queryset(self):
        return Account.objects.with_latest_balance().filter(user=self.request.user, is_active=True)

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
        Account.objects.select_for_update().get(pk=account.pk)
        file = request.FILES.get("file")
        if not file:
            raise ValidationError({"error": "No file provided"})
        file_bytes = file.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        try:
            book = tablib.Dataset().load(file_bytes.decode("utf-8"), format="csv")
        except (tablib.UnsupportedFormat, tablib.InvalidDimensions, ValueError, IndexError) as e:
            raise ValidationError({"error": f"Invalid file format: {e}"})
        try:
            TransactionImport.objects.create(account=account, file_hash=file_hash)
        except IntegrityError:
            raise ValidationError({"error": "This file has already been imported for this account"})

        resource = TransactionResource(account=account)
        result = resource.import_data(book, dry_run=False)
        if result.has_errors() or result.has_validation_errors():
            raise ValidationError({"error": "CSV contains invalid rows"})
        return Response({"imported": result.totals[RowResult.IMPORT_TYPE_NEW]}, status=status.HTTP_200_OK)
