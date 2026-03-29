from django.db import models
from django.db.models import OuterRef, Subquery


class BalanceRecordManager(models.Manager):
    def latest_per_account(self, user):
        latest = (
            self.filter(account=OuterRef("account"), account__user=user)
            .order_by("-date", "-created_at")
            .values("id")[:1]
        )
        return self.filter(id__in=Subquery(latest)).select_related("account")
