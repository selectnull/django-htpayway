from django.shortcuts import render_to_response, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from htpayway.models import Transaction
from htpayway.forms import SuccessForm, FailureForm, PaymentForm
from htpayway.utils import import_callable
import settings


def create(request):
    payway_instance = import_callable(settings.HTPAYWAY_CLASS)
    payway_instance = payway_instance()
    payway_instance.create(request)
    form = PaymentForm(initial=payway_instance.data)
    pgw_authorization_type = payway_instance.pgw_authorization_type
    pgw_shop_id = payway_instance.pgw_shop_id
    pgw_amount = payway_instance.order.total
    pgw_order_id = payway_instance.order.id
    Transaction.objects.create(user=request.user, pgw_shop_id=pgw_shop_id,
                               pgw_order_id=pgw_order_id,
                               pgw_amount=pgw_amount,
                               pgw_authorization_type=pgw_authorization_type,
                               )
    return render_to_response('htpayway/create.html', {'form': form})


@csrf_exempt
def success(request):
    form = SuccessForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payway_instance = import_callable(settings.HTPAYWAY_CLASS)
        payway_instance = payway_instance()
        pgw_order_id = form.cleaned_data['pgw_order_id']
        try:
            transaction = Transaction.objects.get(pgw_order_id=pgw_order_id)
        except ObjectDoesNotExist:
            return render_to_response('htpayway/success.html',
                                      context_instance=RequestContext(request))

        # extract data from response
        pgw_trace_ref = form.cleaned_data['pgw_trace_ref']
        pgw_transaction_id = form.cleaned_data['pgw_transaction_id']
        pgw_amount = form.cleaned_data['pgw_amount']
        pgw_installments = form.cleaned_data[
            'pgw_installments']
        pgw_card_type_id = form.cleaned_data['pgw_card_type_id']

        signature = payway_instance.create_signature_for_success(
            pgw_trace_ref=pgw_trace_ref,
            pgw_transaction_id=pgw_transaction_id,
            pgw_order_id=pgw_order_id, pgw_amount=pgw_amount,
            pgw_installments=pgw_installments,
            pgw_card_type_id=pgw_card_type_id
        )

        if signature == form.cleaned_data['pgw_signature']:
            transaction.pgw_transaction_id = pgw_transaction_id
            payway_instance.after_success()
            transaction.success = True
            transaction.status = 'su'
        else:
            transaction.success = False

        transaction.signature = form.cleaned_data['pgw_signature']
        transaction.save()
    return render_to_response('htpayway/success.html',
                              context_instance=RequestContext(request))


@csrf_exempt
def failure(request):
    form = FailureForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payway_instance = import_callable(settings.HTPAYWAY_CLASS)
        payway_instance = payway_instance()
        pgw_order_id = form.data['pgw_order_id']
        try:
            transaction = Transaction.objects.get(pgw_order_id=pgw_order_id)
        except ObjectDoesNotExist:
            return render_to_response('htpayway/failure.html',
                                      context_instance=RequestContext(request))

        # extract data from response
        pgw_result_code = form.cleaned_data['pgw_result_code']
        pgw_trace_ref = form.cleaned_data['pgw_trace_ref']
        pgw_signature = payway_instance.create_signature_for_failure(
            pgw_result_code=pgw_result_code, pgw_trace_ref=pgw_trace_ref,
            pgw_order_id=pgw_order_id
        )

        if pgw_signature == form.cleaned_data['pgw_signature']:
            payway_instance.after_failure()
            transaction.success = True
            transaction.status = 'fa'
        else:
            transaction.success = False
        transaction.pgw_signature = form.cleaned_data['pgw_signature']
        transaction.save()
    return render_to_response('htpayway/failure.html',
                              context_instance=RequestContext(request))
