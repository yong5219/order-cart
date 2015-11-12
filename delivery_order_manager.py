
# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from order.models import Order
from order.choices import ORDER_STATUSES

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    1. Filter out all order status is "attempt delivery"
    2. Check if the status_date less than today date 2day than change the status become Delivered
    """
    def handle(self, **options):
        attempt_deliverys = Order.objects.get_attempt_delivering_order()
        if attempt_deliverys:
            for attempt_delivery in attempt_deliverys:
                if (attempt_delivery.status_date + timezone.timedelta(hours=48)) < timezone.now():
                    attempt_delivery.status = ORDER_STATUSES[7][0]
                    attempt_delivery.save(update_fields=['status'])

                    logger.info(u"User [%s| %s] attempt_delivery" % (attempt_delivery.pk, attempt_delivery.status))
