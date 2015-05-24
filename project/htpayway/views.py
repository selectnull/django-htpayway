from django.shortcuts import render_to_response, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from htpayway.models import Transaction
from htpayway.tests import CustomPayWay
from htpayway.forms import SuccessForm, FailureForm


def transaction_create(request):
    payway_instance = CustomPayWay('hr')
    form, post_url = payway_instance.create()
    authorization_type = payway_instance.data['pgw_authorization_type']
    shop_id = payway_instance.data['pgw_shop_id']
    amount = payway_instance.order.total
    order_id = payway_instance.order.id
    Transaction.objects.create(user=request.user, shop_id=shop_id,
                               order_id=order_id, amount=amount,
                               authorization_type=authorization_type,
                               )
    return render_to_response('creation.html', {'form': form})


# TODO fix csrf
@csrf_exempt
def transaction_success(request):
    form = SuccessForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payway_instance = CustomPayWay('hr')
        order_id = form.cleaned_data['pgw_order_id']
        try:
            transaction = Transaction.objects.get(order_id=order_id)
        except ObjectDoesNotExist:
            return render_to_response('success.html',
                                      context_instance=RequestContext(request))

        # extract data from response
        trace_ref = form.cleaned_data['pgw_trace_ref']
        transaction_id = form.cleaned_data['pgw_transaction_id']
        amount = form.cleaned_data['pgw_amount']
        installments = form.cleaned_data['pgw_installments']
        card_type_id = form.cleaned_data['pgw_card_type_id']

        signature = payway_instance.create_signature_for_success(
            trace_ref=trace_ref, transaction_id=transaction_id,
            order_id=order_id, amount=amount, installments=installments,
            card_type_id=card_type_id
        )

        if signature == form.cleaned_data['pgw_signature']:
            transaction.transaction_id = transaction_id
            payway_instance.after_success()
            transaction.success = True
            transaction.status = 'su'
        else:
            transaction.success = False

        transaction.signature = form.cleaned_data['pgw_signature']
        transaction.save()
    return render_to_response('success.html',
                              context_instance=RequestContext(request))


# TODO fix
@csrf_exempt
def transaction_failure(request):
    form = FailureForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payway_instance = CustomPayWay('hr')
        order_id = form.data['pgw_order_id']
        try:
            transaction = Transaction.objects.get(order_id=order_id)
        except ObjectDoesNotExist:
            return render_to_response('failure.html',
                                      context_instance=RequestContext(request))

        # extract data from response
        result_code = form.cleaned_data['pgw_result_code']
        trace_ref = form.cleaned_data['pgw_trace_ref']
        signature = payway_instance.create_signature_for_failure(
            pgw_result_code=result_code, pgw_trace_ref=trace_ref,
            pgw_order_id=order_id
        )

        if signature == form.cleaned_data['pgw_signature']:
            transaction.success = True
            payway_instance.after_failure()
            transaction.status = 'fa'
        else:
            transaction.success = False
        transaction.signature = form.cleaned_data['pgw_signature']
        transaction.save()
    return render_to_response('failure.html',
                              context_instance=RequestContext(request))
