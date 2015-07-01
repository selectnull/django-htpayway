from django.contrib import admin
from htpayway.models import Transaction


class TransactionAdmin(admin.ModelAdmin):

    def pgw_name(self):
        return u'{} {}'.format(self.pgw_first_name, self.pgw_last_name)

    list_display = (
        'id', pgw_name, 'user', 'created_on', 'amount',
        'pgw_transaction_id', 'status'
    )
    search_fields = [
        'pgw_first_name', 'pgw_last_name', 'pgw_email',
        'pgw_transaction_id',
    ]
    list_filter = ('created_on', 'status',)
    readonly_fields = ('created_on',)
    fieldsets = (
        ('Order', {
            'fields': (
                'user',
                'created_on',
                'amount',
                'status'
            )
        }),
        ('Response', {
            'fields': (
                ('response_received_on', 'response_signature_valid'),
                ('pgw_trace_ref', 'pgw_transaction_id'),
                ('pgw_installments', 'pgw_card_type_id')
            )
        }),
        ('Pgw data', {
            'fields': (
                'pgw_shop_id',
                'pgw_order_id',
                'pgw_amount',
                'pgw_authorization_type',
                'pgw_first_name',
                'pgw_last_name',
                'pgw_street',
                'pgw_city',
                'pgw_post_code',
                'pgw_country',
                'pgw_email')
        }),
    )


admin.site.register(Transaction, TransactionAdmin)
