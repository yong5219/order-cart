class OrderManager(models.Manager):
    def get_current_order(self, user):
        order = super(OrderManager, self).get_query_set().filter(user=user, status=ORDER_CONFIRMED)
        if len(order) > 1:
            order = order[0]
            order_list = super(OrderManager, self).get_query_set().filter(user=user, status__in=[ORDER_UNCONFIRMED, ORDER_CONFIRMED]).exclude(pk=order.pk)
            order_list.delete()
        elif len(order) == 0:
            order, created = super(OrderManager, self).get_query_set().get_or_create(user=user, status=ORDER_UNCONFIRMED)
        elif len(order) == 1:
            order = order[0]
        OrderProduct.objects.set_previous_unpaid_list(order=order)
        return order

    def get_attempt_delivering_order(self, **kwargs):
        return self.get_query_set().filter(status="8", status_date__isnull=False, **kwargs)


class Order(CommonModel):
    """
    Order model.
    Special Rules:
    1. For all inkjet product, if total_amount < 100, charge RM 15 delivery fee.

    TODO:
    - Move all order.address into Order model.
    """
    user = models.ForeignKey(User, blank=True, null=True)
    address = models.ForeignKey('OrderAddress', blank=True, null=True)
    quotation_address = models.ForeignKey(QuotationAddress, blank=True, null=True)
    delivery_method = models.CharField(_("Delivery"), max_length=15, choices=DELIVERY_CHOICES, default='Self Collect')
    products = models.ManyToManyField(Product, through='OrderProduct')
    total_amount = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    status = models.PositiveSmallIntegerField(choices=ORDER_STATUSES, default=ORDER_UNCONFIRMED)
    status_remark = models.TextField(_("Status Remark"), blank=True, null=True, default="")
    status_date = models.DateTimeField(_("Delivery Date"), blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    priority = models.PositiveIntegerField(max_length=2, default=0)
    self_collect = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    remark = models.TextField(blank=True, null=True)
    courier_company = models.PositiveSmallIntegerField(_("Courier Company"), choices=COURIER_METHOD, blank=True, null=True)
    consignment_no = models.CharField(_("Consignment No."), blank=True, null=True, max_length=15)
    updated_by = models.ForeignKey(User, blank=True, null=True, related_name="updated_by")
    objects = OrderManager()

    def __unicode__(self):
        return u"%s, %s, %s" % (self.pk, self.user, self.status)
