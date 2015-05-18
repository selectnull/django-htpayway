from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from htpayway.models import Transaction
from htpayway.payments import PayWay


def transaction_create(request):
    payway_instance = PayWay()
    shop_id = pawyay_instance.data['ShopID']
    Transaction.objects.create(user=request.user)

    pass


def transaction_success(request):
    if request.method == 'POST':
        Payway_instance = PayWay()
        order_id = request.cleaned_data['pgw_order_id']
        try:
            transaction = Transaction.objects.get(id=order_id)
        except ObjectDoesNotExist:
            return HttpResponse('doom')
        trace_ref = request.cleaned_data['pgw_trace_ref']
        transaction_ref = request.cleaned_data['pgw_transaction_id']
        amount = request.cleaned_data['pgw_amount']
        signature = PayWay.create_signature_for_success(
            trace_ref=trace_ref, transaction_ref=transaction_ref,
            order_id = order_id
        )

        if signature == request.cleaned_data['pgw_signature']:
            transaction.success = 1
            transaction.status = 'Failure'
            payway_instance.after_success()
    return HttpResponse('success')


def transaction_failure(request):
    if request.method == 'POST':
        payway_instance = PayWay()
        order_id = request.cleaned_data['pgw_order_id']
        try:
            transaction = Transaction.objects.get(id=order_id)
        except ObjectDoesNotExist:
            return HttpResponse('doom')
        result_code = request.cleaned_data['pgw_result_code']
        trace_ref = request.cleaned_data['pgw_trace_ref']
        signature = PayWay.create_signature_for_success(
            result_code=result_code, trace_ref=trace_ref,
            order_id=order_id
        )

        if signature == request.cleaned_data['pgw_signature']:
            transaction.status = 'Success'
            payway_instance.after_failure()
    return HttpResponse('failure')
