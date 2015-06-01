from django.contrib import admin
from htpayway.models import Transaction


class TransactionAdmin(admin.ModelAdmin):
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
            'fields': ('response_received_on', 'response_signature_valid')
        }),
        ('Pgw data', {
            'fields': (
                'pgw_transaction_id',
                'pgw_shop_id',
                'pgw_order_id',
                'pgw_amount',
                'pgw_authorization_type',
                'pgw_signature',
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
