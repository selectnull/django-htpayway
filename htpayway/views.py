from django.shortcuts import render_to_response, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from .models import Transaction
from .forms import SuccessForm, FailureForm, PaymentForm
from .utils import import_callable

from django.conf import settings
import datetime


def create(request):
    payway_instance = import_callable(settings.HTPAYWAY_CLASS)
    payway_instance = payway_instance()
    payway_instance.create(request)
    form = PaymentForm(initial=payway_instance.data)

    pgw_authorization_type = payway_instance.pgw_authorization_type
    pgw_shop_id = payway_instance.pgw_shop_id
    amount = payway_instance.order.total
    pgw_amount = str(amount).replace(',', '').replace('.', '')
    pgw_order_id = str(payway_instance.order.id)
    pgw_signature = payway_instance.data['pgw_signature']
    pgw_first_name = payway_instance.order.first_name
    pgw_last_name = payway_instance.order.last_name
    pgw_street = payway_instance.order.street
    pgw_city = payway_instance.order.city
    pgw_post_code = payway_instance.order.post_code
    pgw_country = payway_instance.order.country
    pgw_email = payway_instance.order.email

    if request.user.is_authenticated():
        user = request.user
    else:
        user = None
    Transaction.objects.create(
        user=user, pgw_shop_id=pgw_shop_id,
        pgw_order_id=pgw_order_id,
        pgw_amount=pgw_amount, amount=amount,
        pgw_authorization_type=pgw_authorization_type,
        pgw_signature=pgw_signature,
        pgw_first_name=pgw_first_name,
        pgw_last_name=pgw_last_name,
        pgw_street=pgw_street,
        pgw_city=pgw_city,
        pgw_post_code=pgw_post_code,
        pgw_country=pgw_country,
        pgw_email=pgw_email,
        status='created'
    )
    return render_to_response('htpayway/create.html', {'form': form})


@csrf_exempt
def success(request):
    now = datetime.datetime.now()
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
            transaction.response_signature_valid = True
            transaction.status = 'succeeded'
        else:
            transaction.response_signature_valid = False

        transaction.signature = form.cleaned_data['pgw_signature']
        transaction.response_received_on = now
        transaction.save()
    return render_to_response('htpayway/success.html',
                              context_instance=RequestContext(request))


@csrf_exempt
def failure(request):
    now = datetime.datetime.now()
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
            transaction.response_signature_valid = True
            transaction.status = 'failed'
        else:
            transaction.response_signature_valid = False

        transaction.pgw_signature = form.cleaned_data['pgw_signature']
        transaction.response_received_on = now
        transaction.save()
    return render_to_response('htpayway/failure.html',
                              context_instance=RequestContext(request))
