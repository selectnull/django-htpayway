from django import forms


class SuccessForm(forms.Form):
    pgw_trace_ref = forms.CharField()
    pgw_transaction_id = forms.CharField()
    pgw_order_id = forms.CharField()
    pgw_amount = forms.CharField()
    pgw_installments = forms.CharField()
    pgw_card_type_id = forms.CharField()
    pgw_signature = forms.CharField()


class FailureForm(forms.Form):
    pgw_result_code = forms.CharField()
    pgw_trace_ref = forms.CharField()
    pgw_order_id = forms.CharField()
    pgw_signature = forms.CharField()
