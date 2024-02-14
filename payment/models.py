from django.utils.translation import gettext_lazy as _
from django.db import models
from .validators import validate_phone_number
from datetime import datetime


class PGPaymentRequestLogManager(models.Manager):
    def create(self, *args, **kwargs):
        model_field_names = [field.name for field in self.model._meta.fields]
        valid_kwargs = {key: value for key,
                        value in kwargs.items() if key in model_field_names}
        pg_payment_req = super(PGPaymentRequestLogManager, self).create(
            **valid_kwargs
        )
        return pg_payment_req


class PGPaymentRequestLog(models.Model):
    class CurrencyTypes(models.TextChoices):
        USD = "USD", _("USD")
        BDT = "BDT", _("BDT")

    store_id = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_("Merchant ID Provided by aamarPay"),
        error_messages={
            'null': _("store_id cannot be null")
        },
        verbose_name=_('store id'),
    )
    tran_id = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_("The identification number or order ID, or invoice number"),
        error_messages={
            'null': _("tran_id cannot be null")
        },
        verbose_name=_('transaction id'),
    )
    amount = models.DecimalField(
        null=False,
        blank=False,
        help_text=_(' the total amount you wish to pay for the transaction.'),
        verbose_name=_('amount'),
        max_digits=15,
        decimal_places=2,
        error_messages={
            'blank': _('amount paid by a user must be provided')
        }
    )
    currency = models.CharField(
        max_length=5,
        verbose_name=_('currency'),
        null=False,
        blank=False,
        default=CurrencyTypes.BDT,
        choices=CurrencyTypes.choices,
        help_text=_(
            'The currency field should only contain uppercase letters corresponding to the desired currency'),
        error_messages={
            'null': _('currency cannot be null')
        }
    )
    desc = models.TextField(
        max_length=200,
        null=True,
        blank=False,
        help_text=_(
            "he description field allows the payer to provide additional information or notes related to the payment."
        ),
        error_messages={
            'null': _("details cannot be null")
        },
        verbose_name=_('description'),
    )
    cus_name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_("Customer Full Name"),
        error_messages={
            'null': _("customer name cannot be null")
        },
        verbose_name=_('customer name'),
    )
    cus_email = models.EmailField(
        max_length=30,
        null=False,
        blank=False,
        help_text=_("Customer Email Address"),
        error_messages={
            'null': _("customer email cannot be null")
        },
        verbose_name=_('customer email'),
    )
    cus_phone = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        help_text=_("Phone number of the customer who is making the payment."),
        error_messages={
            'null': _("Customer Phone cannot be null")
        },
        verbose_name=_('customer Phone'),
        validators=[validate_phone_number]
    )
    success_url = models.URLField(
        max_length=200,
        blank=False,
        null=False,
        help_text="The success_url is the designated URL to which the payment gateway will redirect customers after a successful payment transaction.",
        verbose_name="success URL",
        error_messages={
            'null': _("success URL cannot be null")
        },
    )
    fail_url = models.URLField(
        max_length=200,
        blank=False,
        null=False,
        help_text="The fail_url is the designated URL to which the payment gateway will redirect customers after a failed payment transaction.",
        verbose_name="fail URL",
        error_messages={
            'null': _("fail URL cannot be null")
        },
    )
    cancel_url = models.URLField(
        max_length=200,
        blank=False,
        null=False,
        help_text="	URL to return customers to your product page or home page.",
        verbose_name="cancel URL",
        error_messages={
            'null': _("cancel URL cannot be null")
        },
    )

    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
        help_text=_("The timestamp when the request was made to the API"),
    )

    objects = PGPaymentRequestLogManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('PG payment Request log')
        verbose_name_plural = _('PG payment request logs')
        db_table_comment = "PG payment request logs"


class PGPaymentResponseLogManager(models.Manager):
    def create(self, pg_payment_request, is_successful=False, *args, **kwargs):
        model_field_names = [field.name for field in self.model._meta.fields]
        valid_kwargs = {key: value for key,
                        value in kwargs.items() if key in model_field_names}
        valid_kwargs['pay_time'] = datetime.strptime(
            valid_kwargs['pay_time'][0], '%Y-%m-%d %H:%M:%S'
        )
        pg_payment_res = super(PGPaymentResponseLogManager, self).create(
            is_successful=is_successful,
            pg_payment_request=pg_payment_request,
            ** valid_kwargs
        )
        return pg_payment_res


class PGPaymentResponseLog(models.Model):
    pg_payment_request = models.OneToOneField(
        to=PGPaymentRequestLog,
        on_delete=models.RESTRICT,
        related_name=_('respone_from_pg_payment_request'),
        verbose_name=_('pg payment request'),
        unique=True,
        blank=False,
        null=False,
        primary_key=True,
        help_text=_(
            'the pg payment request from which the response was generated'
        ),
        error_messages={
            'null': _('the payment request must be provided'),
            'unique': _('the request instance must be unique')
        }
    )
    pg_service_charge_bdt = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "The service charge for the payment gateway is calculated in Bangladeshi Taka (BDT)."
        ),
        error_messages={
            'null': _("pg service charge cannot be null")
        },
        verbose_name=_('pg service charge bdt'),
    )
    amount_original = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        help_text=_(
            'The amount paid by the customer in Bangladeshi Taka (BDT).'
        ),
        verbose_name=_('amount original'),
        error_messages={
            'blank': _('amount original paid by a user must be provided')
        }
    )
    card_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text=_(
            'card number'
        ),
        verbose_name=_('card number'),
    )
    status_code = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        help_text=_(
            "A status code of 2 signifies a successful transaction, whereas a status code of 7 indicates a failed transaction."
        ),
        error_messages={
            'null': _("status code cannot be null")
        },
        verbose_name=_('status code'),
    )
    pay_status = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "The payment status in text format (e.g., Successful or Failed)."
        ),
        error_messages={
            'null': _("pay status cannot be null")
        },
        verbose_name=_('pay status'),
    )
    currency_merchant = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        help_text=_(
            "This refers to the currency that you have forwarded to the payment gateway."
        ),
        error_messages={
            'null': _("currency merchant cannot be null")
        },
        verbose_name=_('currency merchant status'),
    )
    convertion_rate = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        help_text=_(
            "If you submit currency in USD to the gateway, you are aware of the conversion rate from this end."
        ),
        error_messages={
            'null': _("convertion rate cannot be null")
        },
        verbose_name=_('convertion rate status'),
    )
    pg_txnid = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "This is the unique transaction ID provided by the Payment Gateway for each transaction."
        ),
        error_messages={
            'null': _("pg transaction id cannot be null")
        },
        verbose_name=_('pg transaction id'),
    )
    mer_txnid = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "The unique transaction ID which is created on merchant end"
        ),
        error_messages={
            'null': _("merchant transaction id cannot be null")
        },
        verbose_name=_('merchant transaction id'),
    )
    store_id = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "Unique ID for every merchant"
        ),
        error_messages={
            'null': _("store id cannot be null")
        },
        verbose_name=_('store id'),
    )
    merchant_id = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "Unique ID for every merchant"
        ),
        error_messages={
            'null': _("merchant id cannot be null")
        },
        verbose_name=_('merchant id'),
    )
    currency = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "This field will provide information about in which currency the customer has paid the money"
        ),
        error_messages={
            'null': _("currency cannot be null")
        },
        verbose_name=_('currency'),
    )
    store_amount = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        help_text=_(
            'After deducting the payment gateway charge, this amount will the merchant get.'
        ),
        verbose_name=_('store amount'),
        error_messages={
            'blank': _('store amount must be provided')
        }
    )
    pay_time = models.DateTimeField(
        verbose_name=_('pay time'),
        help_text=_("	Payment Time"),
    )
    amount = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        help_text=_(
            'The amount the customer has paid'
        ),
        verbose_name=_('amount'),
        error_messages={
            'blank': _('amount must be provided')
        }
    )
    bank_txn = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "Bank Transaction Number"
        ),
        error_messages={
            'null': _("bank transaction number cannot be null")
        },
        verbose_name=_('bank transaction number'),
    )
    card_type = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "The customer has used which medium to pay"
        ),
        error_messages={
            'null': _("card type cannot be null")
        },
        verbose_name=_('card type'),
    )
    reason = models.TextField(
        max_length=300,
        null=False,
        blank=False,
        help_text=_(
            "If the transaction failed on the bank end and they send any response then you will get it here"
        ),
        error_messages={
            'null': _("reason cannot be null")
        },
        verbose_name=_('reason'),
    )
    pg_card_risklevel = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "Payment gateway card risk level (no risk = 0)"
        ),
        error_messages={
            'null': _("pg card risk level cannot be null")
        },
        verbose_name=_('pg card risk level'),
    )
    pg_error_code_details = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text=_(
            "If payment fails in the payment gateway end then you will get the reason here"
        ),
        error_messages={
            'null': _("pg error code details cannot be null")
        },
        verbose_name=_('pg error code details'),
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        help_text=_('pg payment response'),
        auto_now_add=True
    )
    is_successful = models.BooleanField(
        verbose_name=_('payment Successful'),
        null=False,
        blank=False,
        default=False,
        help_text=_(
            "Indicates whether the payment process was successful"
        ),
        error_messages={
            'null': _('payment process indication cannnot be null')
        }
    )

    objects = PGPaymentResponseLogManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PG Payment Response Log'
        verbose_name_plural = 'PG Payment Response Logs'


class PGPaymentVerificationResponseLogManager(models.Manager):
    def create(self, pg_response, *args, **kwargs):
        model_field_names = [field.name for field in self.model._meta.fields]
        valid_kwargs = {key: value for key,
                        value in kwargs.items() if key in model_field_names}
        valid_kwargs['date_processed'] = datetime.strptime(
            valid_kwargs['date_processed'], '%Y-%m-%d %H:%M:%S'
        )
        pg_payment_verification_res = super(PGPaymentVerificationResponseLogManager, self).create(
            pg_response=pg_response,
            ** valid_kwargs
        )
        return pg_payment_verification_res


class PGPaymentVerificationResponseLog(models.Model):
    pg_response = models.OneToOneField(
        to=PGPaymentResponseLog,
        on_delete=models.RESTRICT,
        related_name=_('verification_response_from_pg_response'),
        verbose_name=_('pg payment response'),
        unique=True,
        blank=False,
        null=False,
        primary_key=True,
        help_text=_(
            'the pg payment request from which the response was generated'
        ),
        error_messages={
            'null': _('the payment request must be provided'),
            'unique': _('the request instance must be unique')
        }
    )
    amount_bdt = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "amount BDT."
        ),
        error_messages={
            'null': _("amount bdt cannot be null")
        },
        verbose_name=_('amount bdt'),
    )
    status_title = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "status title"
        ),
        error_messages={
            'null': _("status title cannot be null")
        },
        verbose_name=_('status title'),
    )
    approval_code = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "approval code"
        ),
        error_messages={
            'null': _("approval code cannot be null")
        },
        verbose_name=_('approval code'),
    )
    payment_processor = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "payment processor"
        ),
        error_messages={
            'null': _("payment processor cannot be null")
        },
        verbose_name=_('payment processor'),
    )
    bank_trxid = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "bank transaction id"
        ),
        error_messages={
            'null': _("bank transaction id cannot be null")
        },
        verbose_name=_('bank transaction id'),
    )
    payment_type = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "payment type"
        ),
        error_messages={
            'null': _("payment type id cannot be null")
        },
        verbose_name=_('payment type'),
    )
    error_code = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "error code"
        ),
        error_messages={
            'null': _("error code cannot be null")
        },
        verbose_name=_('error code'),
    )
    error_title = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "error title"
        ),
        error_messages={
            'null': _("error title cannot be null")
        },
        verbose_name=_('error title'),
    )
    date_processed = models.DateTimeField(
        verbose_name=_('date processed'),
        help_text=_("date processed"),
    )
    amount_currency = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "amount currency"
        ),
        error_messages={
            'null': _("amount currency cannot be null")
        },
        verbose_name=_('amount currency'),
    )
    rec_amount = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "rec amount"
        ),
        error_messages={
            'null': _("rec amount cannot be null")
        },
        verbose_name=_('rec amount'),
    )
    processing_ratio = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "processing ratio"
        ),
        error_messages={
            'null': _("processing ratio cannot be null")
        },
        verbose_name=_('processing ratio'),
    )
    processing_charge = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "processing charge"
        ),
        error_messages={
            'null': _("processing charge cannot be null")
        },
        verbose_name=_('processing charge'),
    )
    verify_status = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "verify status"
        ),
        error_messages={
            'null': _("verify status cannot be null")
        },
        verbose_name=_('verify status'),
    )
    checkout_status = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "checkout status"
        ),
        error_messages={
            'null': _("checkout status cannot be null")
        },
        verbose_name=_('checkout status'),
    )
    objects = PGPaymentVerificationResponseLogManager()


class UserTransaction(models.Model):
    user_id = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=_(
            "user id"
        ),
        error_messages={
            'null': _("user id cannot be null")
        },
        verbose_name=_('user id'),
    )
    payment_verification_response = models.OneToOneField(
        to=PGPaymentVerificationResponseLog,
        on_delete=models.RESTRICT,
        related_name=_('user_transaction_payment_verification_response'),
        verbose_name=_('payment verification response'),
        unique=True,
        blank=False,
        null=False,
        primary_key=True,
        help_text=_(
            'the pg payment verification response'
        ),
        error_messages={
            'null': _('payment verification response must be provided'),
            'unique': _('payment verification response must be unique')
        }
    )

    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        help_text=_('User Transaction creation timestamp'),
        auto_now_add=True,
        null=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Transaction'
        verbose_name_plural = 'User Transactions'
