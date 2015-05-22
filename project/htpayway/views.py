from django.shortcuts import render_to_response, RequestContext, render
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from htpayway.models import Transaction
from payments.payway import PayWay
from htpayway.tests import CustomPayWay
from htpayway.forms import SuccessForm, FailureForm


def transaction_create(request):
    payway_instance = CustomPayWay('hr')
    post_data, post_url = payway_instance.create()
    authorization_type = payway_instance.data['AuthorizationType']
    shop_id = payway_instance.data['ShopID']
    amount = payway_instance.order.total
    order_id = payway_instance.order.id
    Transaction.objects.create(user=request.user, shop_id=shop_id,
                               order_id=order_id, amount=amount,
                               authorization_type=authorization_type,
                               )
    return HttpResponseRedirect(post_url)
    return render_to_response('creation.html')


def transaction_success(request):
    form = SuccessForm(request.GET or None)
    if request.method == 'GET':
        return render(request, 'success.html', {'form': form})
    # if request.method == 'POST':
    if request.method == 'GET' and form.is_valid():
        print 'aaa'
        payway_instance = CustomPayWay('hr')
        order_id = request.cleaned_data['pgw_order_id']
        try:
            transaction = Transaction.objects.get(id=order_id)
        except ObjectDoesNotExist:
            return HttpResponse('doom')

        # extract data from response
        trace_ref = request.cleaned_data['pgw_trace_ref']
        transaction_id = request.cleaned_data['pgw_transaction_id']
        amount = request.cleaned_data['pgw_amount']
        installments = request.cleaned_data['pgw_installments']
        card_type_id = request.cleaned_data['pgw_card_type_id']

        signature = PayWay.create_signature_for_success(
            trace_ref=trace_ref, transaction_id=transaction_id,
            order_id=order_id, amount=amount, installments=installments,
            card_type_id=card_type_id
        )

        if signature == request.cleaned_data['pgw_signature']:
            transaction.transaction_id = transaction_id
            payway_instance.after_success()
            transaction.success = True
        else:
            transaction.success = False

        transaction.signature = request.cleaned_data['pgw_signature']
        transaction.status = 'su'
        transaction.save()
    return render_to_response('success.html',
                              context_instance=RequestContext(request))


def transaction_failure(request):
    if request.method == 'POST':
        payway_instance = PayWay()
        order_id = request.cleaned_data['pgw_order_id']
        try:
            transaction = Transaction.objects.get(id=order_id)
        except ObjectDoesNotExist:
            return HttpResponse('doom')

        # extract data from response
        result_code = request.cleaned_data['pgw_result_code']
        trace_ref = request.cleaned_data['pgw_trace_ref']
        signature = PayWay.create_signature_for_failure(
            result_code=result_code, trace_ref=trace_ref,
            order_id=order_id
        )

        if signature == request.cleaned_data['pgw_signature']:
            transaction.success = True
            payway_instance.after_failure()
        else:
            transaction.success = False
        transaction.signature = request.cleaned_data['pgw_signature']
        transaction.status = 'fa'
        transaction.save()
    return HttpResponse('failure')
