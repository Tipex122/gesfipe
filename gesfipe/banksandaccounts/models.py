# Python
from binascii import crc32
import re
import datetime

# Django
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

# GesFiPe
from gesfipe.categories.models import Category
from gesfipe.users.models import User
from gesfipe.manageweboob.models import WeboobModules


# WeBoob
from weboob.capabilities.base import empty
from weboob.tools.compat import unicode


class Banks(models.Model):
    name_of_bank = models.CharField(
        'Name of Bank',
        default='Name of Bank',
        max_length=256
    )

    num_of_bank = models.CharField(
        'Id of Bank',
        default='Id',
        max_length=256
    )

    bank_password = models.CharField(
        'Password',
        blank=True,
        max_length=64
    )

    # TODO: Plutôt prévoir une ForeignKey to modules weboob database ?
    module_weboob = models.CharField(
        'Bank module',
        blank=True,
        null=True,
        max_length=64
    )

    # module_weboob = models.ForeignKey(
    #     'WeboobModules',
    #     blank=True,
    #     null=True,
    #     on_delete=models.SET_NULL,
    # )

    def get_weboob_module(self):
        return self.module_weboob

    def __str__(self):
        return "%s" % self.name_of_bank

    class Meta:
        verbose_name = _('bank')
        verbose_name_plural = _('banks')
        ordering = ['name_of_bank']

    def get_absolute_url(self):
        return reverse('bank_detail', kwargs={'pk': self.pk})


class Accounts(models.Model):
    TYPE_UNKNOWN = 0            # Unknown
    TYPE_CHECKING = 1           # Transaction, everyday transactions
    TYPE_SAVINGS = 2            # Savings/Deposit, can be used for every banking
    TYPE_DEPOSIT = 3            # Term of Fixed Deposit, has time/amount constraints
    TYPE_LOAN = 4               # Loan account
    TYPE_MARKET = 5             # Stock market or other variable investments
    TYPE_JOINT = 6              # Joint account
    TYPE_CARD = 7               # Card account
    TYPE_LIFE_INSURANCE = 8     # Life insurances
    TYPE_PEE = 9                # Employee savings PEE
    TYPE_PERCO = 10             # Employee savings PERCO
    TYPE_ARTICLE_83 = 11        # Article 83
    TYPE_RSP = 12               # Employee savings RSP
    TYPE_PEA = 13               # Share savings
    TYPE_CAPITALISATION = 14    # Life Insurance capitalisation
    TYPE_PERP = 15              # Retirement savings
    TYPE_MADELIN = 16           # Complementary retirement savings
    TYPE_MORTGAGE = 17          # Mortgage
    TYPE_CONSUMER_CREDIT = 18   # Consumer credit
    TYPE_REVOLVING_CREDIT = 19  # Revolving credit

    TYPE_ACCOUNT_CHOICE = (
        (TYPE_UNKNOWN, 'Unknown'),
        (TYPE_CHECKING, 'Everyday transactions'),
        (TYPE_SAVINGS, 'Savings/Deposit'),
        (TYPE_DEPOSIT, 'Term of Fixed Deposit, has time/amount constraints'),
        (TYPE_LOAN, 'Loan account'),
        (TYPE_MARKET, 'Stock market or other variable investments'),
        (TYPE_JOINT, 'Joint account'),
        (TYPE_CARD, 'Card account'),
        (TYPE_LIFE_INSURANCE, 'Life insurances'),
        (TYPE_PEE, 'Employee savings PEE'),
        (TYPE_PERCO, 'Employee savings PERCO'),
        (TYPE_ARTICLE_83, 'Article 83'),
        (TYPE_RSP, 'Employee savings RSP'),
        (TYPE_PEA, 'Share savings'),
        (TYPE_CAPITALISATION, 'Life Insurance capitalisation'),
        (TYPE_PERP, 'Retirement savings'),
        (TYPE_MADELIN, 'Complementary retirement savings'),
        (TYPE_MORTGAGE, 'Mortgage'),
        (TYPE_CONSUMER_CREDIT, 'Consumer credit"'),
        (TYPE_REVOLVING_CREDIT, 'Revolving credit'),
    )

    name_of_account = models.CharField(
        'Name of the account',
        default='Name of bank account',
        max_length=256,
        help_text='Enter name of account'
    )

    num_of_account = models.CharField(
        'Account Id',
        default='Id',
        max_length=256,
        help_text='Enter number of account'
    )

    type_int_of_account = models.IntegerField(
        'Type of account (int)',  # use TYPE_* constants
        default=TYPE_UNKNOWN,
        choices=TYPE_ACCOUNT_CHOICE,
        help_text='Please select a type of account',
    )

    # TODO: A priori à supprimer: type_int_of_account suffit
    type_of_account = models.CharField(
        'Type of account',
        default=TYPE_UNKNOWN,
        # choices=TYPE_ACCOUNT_CHOICE,
        # default='Unknown',
        max_length=128,
        help_text='Enter type of account (this field will be deleted in next version)'
    )

    bank = models.ForeignKey('Banks', null=True, blank=False, on_delete=models.SET_NULL)

    # TODO: Il faut pouvoir affecter un User à un 'Bank account' (ce n'est pas le cas: tout le monde est 'owner'). Voir bank_edit en MultiSelect et faire un "add"
    owner_of_account = models.ManyToManyField(User, related_name='user_of_account')

    # Get lis of all users
    def get_users(self):
        return "\n".join([u.username for u in User.objects.all()])

    # Get list of users, owner of account
    def get_list_users(self):
        return "\n".join([u.username for u in self.owner_of_account.all()])
    
    def get_absolute_url(self):
        return reverse('account_detail', kwargs={'pk': self.pk})

    # TODO: To be tested
    def get_total_amount(self):
        total_amount = 0
        return Transactions.objects.filter(account__owner_of_account=self.request.user).aggregate(Sum('amount_of_transaction'))

    def __str__(self):
        return "%s" % self.name_of_account

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        ordering = ['name_of_account']


class Transactions(models.Model):
    TYPE_UNKNOWN       = 0
    TYPE_TRANSFER      = 1
    TYPE_ORDER         = 2
    TYPE_CHECK         = 3
    TYPE_DEPOSIT       = 4
    TYPE_PAYBACK       = 5
    TYPE_WITHDRAWAL    = 6
    TYPE_CARD          = 7
    TYPE_LOAN_PAYMENT  = 8
    TYPE_BANK          = 9
    TYPE_CASH_DEPOSIT  = 10
    TYPE_CARD_SUMMARY  = 11
    TYPE_DEFERRED_CARD = 12

    TYPE_TRANSACTION_CHOICE = (
        (TYPE_UNKNOWN, 'Unknown'),
        (TYPE_TRANSFER, 'Transfer'),
        (TYPE_ORDER, 'Order'),
        (TYPE_CHECK,'Check'),
        (TYPE_DEPOSIT,'Deposit'),
        (TYPE_PAYBACK, 'Payback'),
        (TYPE_WITHDRAWAL, 'Withdrawal'),
        (TYPE_CARD, 'Credit card'),
        (TYPE_LOAN_PAYMENT, 'Loan payment'),
        (TYPE_BANK, 'Bank'),
        (TYPE_CASH_DEPOSIT, 'Cash deposit'),
        (TYPE_CARD_SUMMARY, 'Card summary'),
        (TYPE_DEFERRED_CARD, 'Deferred card'),
    )
    date_of_transaction = models.DateField(
        'Debit date on the bank statement',
        default=datetime.datetime.now
    )

    real_date_of_transaction = models.DateField(
        'Real date, when the payment has been made; usually extracted from the label or from credit card info',
        default=datetime.datetime.now
    )

    value_date_of_transaction = models.DateField(
        'Value date, or accounting date; usually for professional accounts',
        default=datetime.datetime.now
    )

    type_int_of_transaction = models.IntegerField(
        'Type of transaction (int)',  # use TYPE_* constants
        default=TYPE_UNKNOWN,
        choices=TYPE_TRANSACTION_CHOICE,
    )

    # type_of_transaction is used to store weboob account category
    type_of_transaction = models.CharField(
        'Type of transaction',
        default='Unknown',
        # choices=TYPE_TRANSACTION_CHOICE,
        max_length=128
    )

    name_of_transaction = models.CharField(
        'Raw label of the transaction',
        max_length=256
    )

    label_of_transaction = models.CharField(
        'Pretty label',
        default='Pretty label',
        max_length=128
    )

    card_transaction = models.CharField(
        'Card number (if any)',
        default='Credit Card',
        blank=True,
        max_length=128
    )

    commission_of_transaction = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Commission part on the transaction (in account currency)',
        blank=True,
        null=True
    )

    amount_of_transaction = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Transaction amount',
        blank=True,
        null=True
    )

    currency_of_transaction = models.CharField(
        'Currency',
        default='EUR',
        max_length=3
    )

    # Date of creation of the transaction in the database server (not in the bank)
    creation_date = models.DateField(
        'Creation date of the transaction in  database',
        default=datetime.datetime.now
    )

    account = models.ForeignKey(
        Accounts,
        # null=True,
        # blank=True,
        related_name='transactions',
        on_delete=models.CASCADE
    )

    unique_id_of_transaction = models.CharField(
        'Unique Id based on date_of_transaction, amount_of_transaction and name_of_transaction',
        default='unique_id',
        max_length=128
    )

    category_of_transaction = models.ForeignKey(
        Category,
        null=True,
        # default='Budget',
        blank=True,
        on_delete=models.CASCADE
    )

    key_words = ArrayField(models.CharField(max_length=256, blank=True, null=True), blank=True, null=True)

    def get_absolute_url(self):
        return reverse('transaction_detail', kwargs={'pk': self.pk})

    def unique_id(self, seen=None, account_id=None):
        """
        Get an unique ID for the transaction based on date_of_transaction, amount_of_transaction and name_of_transaction.

        :param seen: if given, the method uses this dictionary as a cache to
                     prevent several transactions with the same values to have the same
                     unique ID.
        :type seen: :class:`dict`
        :param account_id: if given, add the account ID in data used to create
                           the unique ID. Can be useful if you want your ID to be unique across
                           several accounts.
        :type account_id: :class:`str`
        :returns: an unique ID encoded in 8 length hexadecimal string (for example ``'a64e1bc9'``)
        :rtype: :class:`str`
        """

        crc = crc32(unicode(self.date_of_transaction).encode('utf-8'))
        crc = crc32(unicode(self.amount_of_transaction).encode('utf-8'), crc)
        # if not empty(self.name_of_transaction.name):
        if not self.name_of_transaction:
            label_of_transaction = self.name_of_transaction
        else:
            label_of_transaction = self.label_of_transaction

        crc = crc32(re.sub('[ ]+', ' ', label_of_transaction).encode("utf-8"), crc)

        if account_id is not None:
            crc = crc32(unicode(account_id).encode('utf-8'), crc)

        if seen is not None:
            while crc in seen:
                crc = crc32(b"*", crc)
            seen.add(crc)

        return "%08x" % (crc & 0xffffffff)

    def create_key_words(self):
        '''
        function used to create keywords the first time data are loaded in database (via load-data.py)
        '''
        # if key_words not empty we consider it has already been created or modified
        # As we don't want to modify what has already been saved we place an "if"
        # TODO: to create a form to modify manually the content of key_words (?)
        if not self.key_words:
            key_tags = self.name_of_transaction.split()
            key_words_list = []
            for key_tag in key_tags:
                if len(key_tag) > 2 and key_tag.isalpha():
                    # print ('=====> ', key_tag)
                    key_tag = key_tag.upper()
                    # self.key_words.append(key_tag)
                    key_words_list.append(key_tag)
            self.key_words = key_words_list

    def get_key_words(self):
        return self.key_words

    def __repr__(self):
        return "<Transaction date=%r label=%r amount=%r>" % (self.date_of_transaction,
                                                             self.label_of_transaction,
                                                             self.amount_of_transaction)

    def __str__(self):
        return "[%s] -- %s ===>  %s ++++ account: %s  +++ category %s  +++++ type: %s" % (
            self.date_of_transaction,
            self.name_of_transaction,
            self.amount_of_transaction,
            self.account,
            self.category_of_transaction,
            self.type_of_transaction,
        )

    #    def __init__(self):
    #        tags = self.tags
    #        super(Transactions, self).__init__(self, *args, **kwargs)

    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')
        ordering = ['-date_of_transaction']

