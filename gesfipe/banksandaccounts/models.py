# Python
from binascii import crc32
import re
import datetime

# Django
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _

# GesFiPe
from gesfipe.categories.models import Category
from gesfipe.users.models import User


# WeBoob
from weboob.capabilities.base import empty
from weboob.tools.compat import unicode


class Banks(models.Model):
    name_of_bank = models.CharField(
        'Nom de la banque',
        default='Nom de la banque',
        max_length=256)

    num_of_bank = models.CharField(
        'Identifiant de la banque',
        default='Identifiant',
        max_length=256)

    def __str__(self):
        return "%s" % self.name_of_bank

    class Meta:
        verbose_name = _('bank')
        verbose_name_plural = _('banks')
        ordering = ['name_of_bank']


class Accounts(models.Model):
    TYPE_UNKNOWN = 0
    TYPE_CHECKING = 1
    "Transaction, everyday transactions"
    TYPE_SAVINGS = 2
    "Savings/Deposit, can be used for every banking"
    TYPE_DEPOSIT = 3
    "Term of Fixed Deposit, has time/amount constraints"
    TYPE_LOAN = 4
    "Loan account"
    TYPE_MARKET = 5
    "Stock market or other variable investments"
    TYPE_JOINT = 6
    "Joint account"
    TYPE_CARD = 7
    "Card account"
    TYPE_LIFE_INSURANCE = 8
    "Life insurances"
    TYPE_PEE = 9
    "Employee savings PEE"
    TYPE_PERCO = 10
    "Employee savings PERCO"
    TYPE_ARTICLE_83 = 11
    "Article 83"
    TYPE_RSP = 12
    "Employee savings RSP"
    TYPE_PEA = 13
    "Share savings"
    TYPE_CAPITALISATION = 14
    "Life Insurance capitalisation"
    TYPE_PERP = 15
    "Retirement savings"
    TYPE_MADELIN = 16
    "Complementary retirement savings"
    TYPE_MORTGAGE = 17
    "Mortgage"
    TYPE_CONSUMER_CREDIT = 18
    "Consumer credit"
    TYPE_REVOLVING_CREDIT = 19
    "Revolving credit"

    name_of_account = models.CharField(
        'Name of the account',
        default='Name of bank account',
        max_length=256
    )

    def get_users(self):
        return "\n".join([u.username for u in User.objects.all()])

    num_of_account = models.CharField(
        'Account Id',
        default='Id',
        max_length=256)

    type_int_of_account = models.IntegerField(
        'Type of account (int)',  # use TYPE_* constants
        default=TYPE_UNKNOWN
    )

    type_of_account = models.CharField(
        'Type of account',
        default='Unknown',
        max_length=128
    )

    bank = models.ForeignKey('Banks', null=True, blank=True, on_delete=models.CASCADE)

    # owner_of_account = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO: Il faut pouvoir affecter un User à un 'Bank account' (ce n'est pas le cas: tout le monde est 'owner'
    # Nota: remplacer "get_users" par "owner_of_account" dans "AccountsAdmin" pour revenir à la solution "ForeignKey"
    owner_of_account = models.ManyToManyField(User)

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
        'Type of transaction (int)', # use TYPE_* constants
        default=TYPE_UNKNOWN
    )

    type_of_transaction = models.CharField(
        'Type of transaction',
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

    creation_date = models.DateField(
        'Creation date of the transaction in  database',
        default=datetime.datetime.now
    )

    account = models.ForeignKey(
        Accounts,
        # null=True,
        # blank=True,
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
        blank=True,
        on_delete=models.CASCADE
    )

    key_words = ArrayField(models.CharField(max_length=256, blank=True, null=True), blank=True, null=True)

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

        # print('+++++ Value of uniq_id transaction octal: {} ++++++'.format("%08x" % (crc & 0xffffffff)))
        # print('+++++ Value of uniq_id transaction: {} ++++++'.format(crc))

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

