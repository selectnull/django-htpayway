from django import forms


class SuccessForm(forms.Form):
    trace_ref = forms.CharField()
    transaction_id = forms.CharField()
    order_id = forms.CharField()
    amount = forms.CharField()
    installments = forms.CharField()
    card_type_id = forms.CharField()
    signature = forms.CharField()


class FailureForm(forms.Form):
    result_code = forms.CharField()
    trace_ref = forms.CharField()
    order_id = forms.CharField()
    signature = forms.CharField()
