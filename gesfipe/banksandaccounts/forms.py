# Django
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User

from django import forms

# GesFiPe
from gesfipe.manageweboob.models import WeboobModules
from gesfipe.categories.models import Category
from .models import Banks, Accounts, Transactions

# Others
from mptt.forms import TreeNodeChoiceField


class BankForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = Banks
        widgets = {
            'bank_password': forms.PasswordInput(),
        }
        fields = (
            'name_of_bank',
            'num_of_bank',
            'bank_login',
            'bank_password',
            'module_weboob',
        )


class BankConnectionForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = Banks
        # TODO: Vérifier que les champs ne sont pas vide avant de lancer la connexion
        # TODO: si erreur de connexion, alors raise une erreur et revenir vers une autre page ?
        widgets = {
            'bank_password': forms.PasswordInput(),
        }
        fields =(
            'bank_login',
            'bank_password',
        )


        # bank_password = forms.CharField(widget=forms.PasswordInput)


class AccountForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = Accounts
        fields = (
            'name_of_account',
            'num_of_account',
            'type_int_of_account',
            'bank',  # TODO: How to obtain the list of banks only available for the connected user ?
            'owner_of_account',
        )

    def form_valid(self, form):
        form.instance.owner_of_account = self.request.user
        return super().form_valid(form)


class TransactionForm(LoginRequiredMixin, forms.ModelForm):
    class Meta:
        model = Transactions
        fields = (
            'date_of_transaction',
            'real_date_of_transaction',
            'value_date_of_transaction',
            'type_int_of_transaction',
            'type_of_transaction',
            'name_of_transaction',
            'label_of_transaction',
            'card_transaction',
            'commission_of_transaction',
            'amount_of_transaction',
            'currency_of_transaction',
            'account',
            'category_of_transaction',
            'key_words',
        )
    # type_of_transaction = forms.ChoiceField(choices=Transactions.TYPE_TRANSACTION_CHOICE)
    category_of_transaction = TreeNodeChoiceField(queryset=Category.objects.all(), level_indicator=u'+--')
    # TODO: How to obtain the list of accounts only available for the connected user ?
    # account = forms.ChoiceField(queryset=Accounts.objects.all().filter(owner_of_account=User.get_username))
    # date_of_transaction = forms.DateField(widget=forms.SelectDateWidget())
    # key_words = forms.MultipleChoiceField()

