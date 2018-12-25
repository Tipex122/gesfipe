from django.contrib import admin

# Register your models here.
from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Banks
from .models import Accounts
from .models import Transactions


# Register your models here.


class TransactionsResource(resources.ModelResource):
    class Meta:
        model = Transactions
        # exclude = ('id', 'creation_date','account','category_of_transaction',)
        # exclude = ('id',)
        # import_id_fields = ('name_of_transaction',)
        skip_unchanged = True

        fields = (
            'real_date_of_transaction',
            'type_int_of_transaction',
            'name_of_transaction',
            'amount_of_transaction',
            'currency_of_transaction',
            # 'account',
            # 'category_of_transaction',
            # 'id',
        )

        # widgets = {
        #    'date_of_transaction': {'format': '%d/%m/%Y'},
        #    'creation_date': {'format': '%d/%m/%Y'},

# class TransactionsAdmin(ImportExportModelAdmin, admin.ModelAdmin):
class TransactionsAdmin(ImportExportModelAdmin):
    resource_class = TransactionsResource

    fieldsets = [
        (None,
         {'fields':
              ['date_of_transaction',
               'real_date_of_transaction',
               'value_date_of_transaction',
               'type_int_of_transaction',
               'type_of_transaction',
               'name_of_transaction',
               'label_of_transaction',
                              ]
          }
         ),
        # ('Info Genre', {'fields':
        # ['amount_of_transaction','currency_of_transaction', 'bank_of_account','create_date','account']}),
        ('Detailed info',
         {'fields':
              [
                'name_of_transaction',
                'amount_of_transaction',
                'currency_of_transaction',
                'commission_of_transaction',
                'creation_date',
                'account',
                'category_of_transaction',
                'card_transaction',
                'unique_id_of_transaction',
                'key_words',
               ]
          }
         ),
    ]
    # TODO: Comment faire apparaître le nom de la banque associée à la transaction et au compte ? ==> A creuser
    list_display = ('real_date_of_transaction',
                    'type_int_of_transaction',
                    'label_of_transaction',
                    'account',
                    # 'account__bank',
                    # 'account.bank',
                    'amount_of_transaction',
                    'category_of_transaction',
                    )

    list_filter = ('date_of_transaction',
                   'account',
                   'category_of_transaction'
                   )

    date_hierarchy = 'date_of_transaction'

    search_fields = ['name_of_transaction',
                     'amount_of_transaction'
                     ]

admin.site.register(Transactions, TransactionsAdmin)


class AccountsAdmin(admin.ModelAdmin):
    list_display = ('num_of_account',
                    'name_of_account',
                    'type_int_of_account',
                    'type_of_account',
                    # 'get_users',
                    'get_list_users',
                    # 'owner_of_account',
                    'bank')

    list_filter = ('bank','owner_of_account',)
    filter_horizontal = ('owner_of_account',)

admin.site.register(Accounts, AccountsAdmin)


class BanksAdmin(admin.ModelAdmin):
    list_display = ('name_of_bank', 'num_of_bank', 'bank_password', 'module_weboob',)

admin.site.register(Banks, BanksAdmin)

