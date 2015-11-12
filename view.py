@login_required
def order_cart(request):
    profile = request.user.get_profile()
    order = Order.objects.get_current_order(request.user)
    address = None

    if order.status == ORDER_CONFIRMED:
        return redirect('order_checkout')

    remark_form = OrderRemarkForm(instance=order)
    address = order.address if order.address else None
    order_form = OrderForm()
    order_product_selection_form = OrderProductSelectionForm(order=order)
    delivery_method_form = OrderDeliveryMethodForm(initial={
        'delivery_method': profile.delivery,
    })

    if address:
        address_form = OrderAddressForm(instance=address)
    else:
        address_form = OrderAddressForm(initial={
            'contact_person': profile.contact_person,
            'contact_number': profile.tel_no,
            'address': profile.address,
            'town': profile.town,
            'postcode': profile.postcode,
            'state': profile.state,
            'country': profile.country,
        })

    order_product_list = OrderProduct.objects.filter(order=order)

    if request.method == 'POST':
        remark_form = OrderRemarkForm(request.POST, instance=order)
        delivery_method_form = OrderDeliveryMethodForm(request.POST)
        address_form = OrderAddressForm(request.POST)
        order_form = OrderForm(request.POST)
        order_product_selection_form = OrderProductSelectionForm(request.POST, order=order)
        form_checked = False

        if delivery_method_form.is_valid():
            if delivery_method_form.cleaned_data['delivery_method'] == 'Delivery':
                if address_form.is_valid():
                    address = address_form.save(commit=False)
                    address.user = request.user
                    form_checked = True
            else:
                form_checked = True

        if remark_form.is_valid() and order_form.is_valid() and order_product_selection_form.is_valid() and form_checked:
            op_checkout_pk_list = order_product_selection_form.cleaned_data['op_check']
            #op_checkout_list = order.orderproduct_set.filter(pk__in=op_checkout_pk_list)
            #op_checkout_list.update(checkout=True)
            for op in order.orderproduct_set.all():
                if unicode(op.pk) in op_checkout_pk_list:
                    op.checkout = True
                else:
                    op.checkout = False
                op.save()
            remark_form.save()
            order = Order.objects.get_current_order(request.user)
            order.delivery_method = delivery_method_form.cleaned_data['delivery_method']
            if order.delivery_method == 'Self Collect':
                order.self_collect = True
            else:
                order.self_collect = False

            try:
                if address_form.cleaned_data['state'] == 'Sabah' or address_form.cleaned_data['state'] == 'Sarawak':
                    order.delivery_fee = 0
                    order.total_amount = order.total_amount
                else:
                    order.delivery_fee = order.get_delivery_fee()
                    order.total_amount = order.total_amount + order.delivery_fee
            except:
                order.delivery_fee = order.get_delivery_fee()
                order.total_amount = order.total_amount + order.delivery_fee

            if not request.user.profile_user.check_balance(amount=order.total_amount):
                messages.error(request, u'Not enough balance. Please reload.')
            else:
                if address:
                    address.save()
                    order.address = address

                order.status_confirmed()
                order.save()
                return redirect('order_checkout')

    context = {
        'order': order,
        'order_product_list': order_product_list,
        'selected_page': 'order_cart',
        'sub_selected_page': 'order_cart',
        'remark_form': remark_form,
        'address_form': address_form,
        'delivery_method_form': delivery_method_form,
        'order_form': order_form,
        'order_product_selection_form': order_product_selection_form,
    }
    return render_to_response('order/order_cart.html', context, RequestContext(request))
