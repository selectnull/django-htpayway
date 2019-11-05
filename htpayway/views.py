from django.shortcuts import render_to_response, RequestContext, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404

from .models import Transaction
from .forms import SuccessForm, FailureForm, PaymentForm
from .utils import get_payway_class

import datetime


def begin(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        pk=int(transaction_id), status='created')
    payway = get_payway_class()(request=request,
                                transaction=transaction,
                                **transaction.pgw_data())

    form = PaymentForm(initial=payway.pgw_data())
    return render_to_response('htpayway/begin.html', {'form': form, 'form_url': payway.form_url})


@csrf_exempt
def success(request):
    if request.method == 'POST':
        now = datetime.datetime.now()
        form = SuccessForm(request.POST)
        callback = False
        result = {}
        if form.is_valid():
            payway = get_payway_class()()
            pgw_order_id = form.cleaned_data['pgw_order_id']
            transaction = Transaction.objects.get(pgw_order_id=pgw_order_id, status='created')

            # extract data from response
            pgw_trace_ref = form.cleaned_data['pgw_trace_ref']
            pgw_transaction_id = form.cleaned_data['pgw_transaction_id']
            pgw_amount = form.cleaned_data['pgw_amount']
            pgw_installments = form.cleaned_data['pgw_installments']
            pgw_card_type_id = form.cleaned_data['pgw_card_type_id']

            signature = payway.calc_incoming_signature([
                pgw_trace_ref, pgw_transaction_id, pgw_order_id, pgw_amount,
                pgw_installments, pgw_card_type_id])

            if signature == form.cleaned_data['pgw_signature']:
                transaction.pgw_transaction_id = pgw_transaction_id
                transaction.pgw_trace_ref = pgw_trace_ref
                transaction.pgw_installments = pgw_installments
                transaction.pgw_card_type_id = pgw_card_type_id
                callback = True
                transaction.response_signature_valid = True
                transaction.status = 'succeeded'
            else:
                transaction.response_signature_valid = False

            transaction.response_received_on = now
            transaction.save()

            if callback:
                result = payway.on_success(transaction)
                if isinstance(result, HttpResponse):
                    return result
        return render_to_response('htpayway/success.html', result,
                                  context_instance=RequestContext(request))
    else:
        raise Http404


@csrf_exempt
def failure(request):
    if request.method == 'POST':
        now = datetime.datetime.now()
        form = FailureForm(request.POST)
        callback = False
        result = {}
        if form.is_valid():
            payway = get_payway_class()()
            pgw_order_id = form.cleaned_data['pgw_order_id']
            transaction = Transaction.objects.get(pgw_order_id=pgw_order_id, status='created')

            # extract data from response
            pgw_result_code = form.cleaned_data['pgw_result_code']
            pgw_trace_ref = form.cleaned_data['pgw_trace_ref']
            pgw_signature = payway.calc_incoming_signature(
                [pgw_result_code, pgw_trace_ref, pgw_order_id])

            if pgw_signature == form.cleaned_data['pgw_signature']:
                transaction.pgw_result_code = pgw_result_code
                transaction.pgw_trace_ref = pgw_trace_ref
                callback = True
                transaction.response_signature_valid = True
                transaction.status = 'failed'
            else:
                transaction.response_signature_valid = False

            transaction.pgw_signature = form.cleaned_data['pgw_signature']
            transaction.response_received_on = now
            transaction.save()

            if callback:
                result = payway.on_failure(transaction)
                if isinstance(result, HttpResponse):
                    return result
        return render_to_response('htpayway/failure.html', result,
                                  context_instance=RequestContext(request))
    else:
        raise Http404
