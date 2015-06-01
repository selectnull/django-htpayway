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


class PaymentForm(forms.Form):
    pgw_shop_id = forms.CharField(max_length=8)
    pgw_order_id = forms.CharField(max_length=50)
    pgw_amount = forms.CharField(max_length=12)
    pgw_authorization_type = forms.CharField(max_length=1)
    pgw_language = forms.CharField(max_length=2)
    pgw_return_method = forms.CharField(max_length=4)
    pgw_success_url = forms.CharField(max_length=1000)
    pgw_failure_url = forms.CharField(max_length=1000)
    pgw_first_name = forms.CharField(max_length=20)
    pgw_last_name = forms.CharField(max_length=20)
    pgw_street = forms.CharField(max_length=40)
    pgw_city = forms.CharField(max_length=20)
    pgw_post_code = forms.CharField(max_length=9)
    pgw_country = forms.CharField(max_length=50)
    pgw_telephone = forms.CharField(max_length=50)
    pgw_email = forms.CharField(max_length=50)
    pgw_disable_installments = forms.CharField(max_length=1)
    pgw_signature = forms.CharField(max_length=40)

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].widget = forms.HiddenInput()
            self.fields[f].required = False
