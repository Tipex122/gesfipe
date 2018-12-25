# Create your views here.

# Python
import logging

# from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render

# django
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Sum, Min, Max, Count
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Weboob
from weboob.core import Weboob
from weboob.capabilities.bank import CapBank

# Gesfipe
from .forms import *
from gesfipe.categories.models import Tag
from gesfipe.managegesfi.views import list_unique_of_numbers


logger = logging.getLogger(__name__)

# Create your views here.
'''
def accounts_info(account_id=0):
    if account_id == 0:
        account_info = Accounts.objects.annotate(
            total_amount_by_account=Sum('transactions__amount_of_transaction'),
            avg_amount_by_account=Avg('transactions__amount_of_transaction'),
            min_amount_by_account=Min('transactions__amount_of_transaction'),
            max_amount_by_account=Max('transactions__amount_of_transaction'),
            num_transac_by_account=Count('transactions'))

    elif account_id != 0:
        account_info = Accounts.objects.filter(id=account_id).annotate(
            total_amount_by_account=Sum('transactions__amount_of_transaction'),
            avg_amount_by_account=Avg('transactions__amount_of_transaction'),
            min_amount_by_account=Min('transactions__amount_of_transaction'),
            max_amount_by_account=Max('transactions__amount_of_transaction'),
            num_transac_by_account=Count('transactions'))

    return account_info


def accounts_info2(request, account_id=0):
    account_info = Accounts.objects.filter(owner_of_account=request.user).annotate(
    total_amount_by_account=Sum('transactions__amount_of_transaction'),
    avg_amount_by_account=Avg('transactions__amount_of_transaction'),
    min_amount_by_account=Min('transactions__amount_of_transaction'),
    max_amount_by_account=Max('transactions__amount_of_transaction'),
    num_transac_by_account=Count('transactions'))

    return account_info
'''


def accounts_info2(request, account_id=0):
    if account_id == 0:
        account_info = Accounts.objects.filter(owner_of_account=request.user).annotate(
            total_amount_by_account=Sum('transactions__amount_of_transaction'),
            avg_amount_by_account=Avg('transactions__amount_of_transaction'),
            min_amount_by_account=Min('transactions__amount_of_transaction'),
            max_amount_by_account=Max('transactions__amount_of_transaction'),
            num_transac_by_account=Count('transactions'))

    elif account_id != 0:
        account_info = Accounts.objects.filter(owner_of_account=request.user).filter(id=account_id).annotate(
            total_amount_by_account=Sum('transactions__amount_of_transaction'),
            avg_amount_by_account=Avg('transactions__amount_of_transaction'),
            min_amount_by_account=Min('transactions__amount_of_transaction'),
            max_amount_by_account=Max('transactions__amount_of_transaction'),
            num_transac_by_account=Count('transactions'))

    return account_info


@login_required
def banks_and_accounts_list(request):
    banks_list = Banks.objects.all()  # .filter(accounts__owner_of_account=request.user)
    accounts_list = Accounts.objects.all().filter(owner_of_account=request.user)
    account_total = \
        Transactions.objects.filter(account__owner_of_account=request.user).aggregate(
            total=Sum('amount_of_transaction'))

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'banks_list': banks_list,
        'accounts_list': accounts_list,
        'account_total': account_total,
        'accounts_info': accounts_info2(request),
        'num_visits': num_visits,
    }
    return render(
        request,
        'banksandaccounts/banks_and_accounts_list.html',
        context
    )


@login_required
def transactions_list(request):
    # banks = Banks.objects.all()
    banks_list = Banks.objects.all()  # .filter(accounts__owner_of_account=request.user)
    # accounts_list = Accounts.objects.all().filter(owner_of_account=request.user)

    # transaction_list = Transactions.objects.all()
    transaction_list = Transactions.objects.filter(account__owner_of_account=request.user)

    account_total = transaction_list.aggregate(Sum('amount_of_transaction'))

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Page de 25 lignes
    num_of_lines_per_page = 25
    paginator = Paginator(transaction_list, num_of_lines_per_page)
    page = request.GET.get('page')

    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)

    logger.warning('In transaction_list : %s', transactions)

    context = {
        'banks_list': banks_list,
        # used for dispatching accounts by bank in sidebar

        'transactions': transactions,
        # used to list transactions related to account(s) with num_of_lines_per_page

        'account_total': account_total,
        # sum of all transactions

        'accounts_info': accounts_info2(request, 0),
        # general information related to all accounts (due to "0")

        'all_accounts': accounts_info2(request, 0),
        # general information related
        # to all accounts (due to "0") and used in sidebar

        'num_visits': num_visits,
        # to count the number of visit on the main page (transactions_list2.html only)
        # just for test to use django.sessions middleware
    }
    return render(request, 'banksandaccounts/transactions_list.html', context)


# TODO: Access management ==> to be improved with ListView
# class TransactionsListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
class TransactionsListView(LoginRequiredMixin, generic.ListView):
    model = Transactions
    paginate_by = 25

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TransactionsListView, self).get_context_data(**kwargs)
        # Get the blog from id and add it to the context
        context['account_total'] = Transactions.objects.aggregate(Sum('amount_of_transaction'))
        # context['banks'] = Banks.objects.all()
        context['banks'] = Banks.objects.all().filter(accounts__owner_of_account=self.request.user)
        # context['accounts_info'] = accounts_info(0)
        context['accounts_info'] = accounts_info2(self.request, 0)
        # context['all_accounts'] = accounts_info(0)
        context['all_accounts'] = accounts_info2(self.request, 0)

        return context

    def get_queryset(self):
        return Transactions.objects.filter(account__owner_of_account=self.request.user)

    context_object_name = 'transactions_list'  # your own name for the list as a template variable
    queryset = Transactions.objects.all()  # [:55] Get 55 transactions
    template_name = 'banksandaccounts/transactions_list3.html'  # Specify your own template name/location


@login_required
def account_list(request, account_id):
    # accounts = Accounts.objects.all()
    banks_list = Banks.objects.all()
    # banks = Banks.objects.all().filter(accounts__owner_of_account=request.user)

    transac_list = Transactions.objects.filter(account_id=account_id)
    # transactions_list = Transactions.objects.get(id=account_id)

    account_total = Transactions.objects.filter(account_id=account_id).aggregate(Sum('amount_of_transaction'))

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Page de 25 lignes
    num_of_lines_per_page = 25
    paginator = Paginator(transac_list, num_of_lines_per_page)
    page = request.GET.get('page')

    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)

    context = {
        'banks_list': banks_list,
        # used for dispatching accounts by bank in sidebar

        'transactions': transactions,
        # used to list transactions related to account(s)

        'account_total': account_total,
        # sum of all transactions

        'accounts_info': accounts_info2(request, account_id),
        # general information related to selectede account

        'all_accounts': accounts_info2(request, 0),
        # general information related to all accounts (due to "0") and used in sidebar

        'num_visits': num_visits,
        # to count the number of visit on the main page (transactions_list2.html only)
        # just for test to use django.sessions middleware

    }

    return render(request, 'banksandaccounts/transactions_list.html', context)


class BankUpdate(LoginRequiredMixin, UpdateView):
    model = Banks
    fields = ['name_of_bank', 'num_of_bank', 'bank_login', 'bank_password', 'module_weboob' ]


class BankDelete(LoginRequiredMixin, DeleteView):
    model = Banks
    # TODO: to redirect sommewhere else (obligé de resélectionner la banque pour qu'elle soit supprimée)
    success_url = reverse_lazy('banksandaccounts:banks_list')


@login_required
def bank_detail(request, bank_id):
    bank = Banks.objects.get(id=bank_id)
    context = {'bank': bank}
    return render(request, 'banksandaccounts/bank_detail.html', context)


@login_required
def banks_list(request):
    banks = Banks.objects.all() # TODO: with filter we repeat Banks as many times as it exists accounts: .filter(accounts__owner_of_account=request.user)
    context = {'banks': banks}
    return render(request, 'banksandaccounts/banks_list.html', context)


@login_required
def bank_create(request):
    banks_list = Banks.objects.all()  # .filter(accounts__owner_of_account=request.user)

    if request.method == 'POST':
        form = BankForm(data=request.POST)

        if form.is_valid():
            bank = form.save(commit=False)
            # category.owner = request.user
            bank.save()
            # form.save_m2m()
            # return redirect('transactions_list', transaction.account.id)
            return redirect('banksandaccounts:banks_list')

    else:
        form = BankForm()

    context = {
        'form': form,
        'create': True
    }
    return render(request, 'banksandaccounts/bank_edit.html', context)

@login_required
def bank_create_with_weboob_module(request, pk):
    # TODO: renvoyer vers un formulaire ayant été prérempli par pk = weboob_module
    # name of banque = weboo_mdule.description_of_module
    # au lieu de "save" ==> "save and load accounts"
    # utiliser quelque chose comme cleaned_data.module_weboob = Weboob.objects.get(pk = pk)
    # et cleaned_data.name_of_bank = Weboob.objects.get(pk = pk).description_of_module

    if request.method == 'POST':
        form = BankForm(data=request.POST)
        if form.is_valid():
            bank = form.save(commit=False)
            # category.owner = request.user
            bank.save()
            # form.save_m2m()
            # return redirect('transactions_list', transaction.account.id)
            return redirect('banksandaccounts:banks_list')

    else:
        form = BankForm()
    
    context = {
        'form': form,
        'create': True
        #TODO: ajouter un flag "create with weboob" pour rediriger vers load_transactions (et créer les comptes)
    }
    return render(request, 'banksandaccounts/bank_edit.html', context)


@login_required
def bank_edit(request, pk):
    bank = get_object_or_404(Banks, pk=pk)

    ## banks_list = Banks.objects.all()   # .filter(accounts__owner_of_account=request.user)

    ## accounts_list = Accounts.objects.all().filter(owner_of_account=request.user)

    if request.method == 'POST':
        form = BankForm(instance=bank, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('banksandaccounts:banks_list')

            # return redirect('budget')
    else:
        ## data = {'Bank': banks_list, }
        # print(data)
        form = BankForm(instance=bank)

    # form.account = forms.Select(choices=Accounts.objects.all().filter(owner_of_account=request.user))

    context = {
        'bank': bank,
        ## 'all_accounts': accounts_info2(request, 0),
        # general information related
        # to all accounts (due to "0") and used in sidebar
        # 'account': account,
        ## 'banks_list': banks_list,
        ## 'accounts_list': accounts_list,
        'form': form,
        'create': False
    }
    return render(request, 'banksandaccounts/bank_edit.html', context)


@login_required
def load_transactions(request, w = Weboob(), bank = Banks(), list_of_accounts = []):
    '''
    Function to download transactions (or any related information) from banks through backends managed by Weboob
    And load them in the database managed by GesfiPe
    :param request: request parameter
    :param w: Weboob instance
    :param list_of_accounts: list of accounts provided by banks
    :return: render: to render the list of transactions got from accounts managed by Weboob Backends
    '''

    # List of accounts in Gesfipe DataBase
    # db_accounts_list = Accounts.objects.all() # .filter(owner_of_account=request.user)
    logger.warning('\n REGUEST: === @@@@@@@@@ === : %s \n', request.POST)
    db_accounts_list_id = Accounts.objects.values_list('num_of_account', flat=True)

    logger.warning('list_of_accounts (param function) ++++++> : \n %s \n   ||| db_account_list ++++++> : \n %s \n', list_of_accounts, db_accounts_list_id)

    # First chek if real_account (given by bank with weboob) exist in database. 
    # If not: one must create new account in Gesfipe Database
    for real_account in list_of_accounts:
        logger.warning('_______ real_account _______  : %s', real_account)
        if real_account.id not in db_accounts_list_id:
            act = Accounts()
            act.name_of_account = real_account.label
            act.num_of_account = real_account.id
            act.type_int_of_account = real_account.type            
            act.bank = bank

            logger.warning(
                'Ceating new account: ++++++> : %s --- Num : %s --- Type : %s', 
                act.name_of_account, 
                act.num_of_account, 
                act.type_int_of_account
            )
            act.save()
            # TODO: how to set owner_of_account ?
            # act.owner_of_account = request.user
        else:
            logger.warning('Account already exists in GesFipe Database!!!!!')
    
    # Updating list of accounts after potential creation of new ones
    db_accounts_list = Accounts.objects.all()
    db_accounts_list_id = Accounts.objects.values_list('num_of_account', flat=True)

    # Get unique_number of each transaction 
    # (to identify if the new transactions coming from banks have been already loaded or not)
    list_uniques = list_unique_of_numbers()

    # To store new transactions coming from bank history and show them
    # TODO: To set in place a flag to be able to show, when needed, those "newly" loaded transactions in Gesfipe database
    list_of_transactions = []

    # real_account: account given by bank
    for real_account in list_of_accounts:
        # TODO: suivant que le compte est de type TYPE_LOAN ou TYPE_CARD ou ... les informations ou transactions à charger sont différente. Faire des tests et charger les "transactions en fonction dy type de compte."
        
        # Following test not necessary ==> already tested previously in this function : to remove ?
        # if real_account.id not in db_accounts_list_id:
        #     act = Accounts()
        #     act.name_of_account = real_account.label
        #     logger.warning('act.name_of_account = real_account.label ++++++> : %s', act.name_of_account)
        #     act.num_of_account = real_account.id
        #     logger.warning('act.name_of_account = act.num_of_account ++++++> : %s', act.num_of_account)
        #     act.type_int_of_account = real_account.type
        #     act.bank = bank
        #     act.save()
        #     # act.owner_of_account = request.user
            

        # db_account: account in gesfipe database
        for db_account in db_accounts_list:

            if real_account.id == db_account.num_of_account:
                logger.warning("------------------------------------")
                logger.warning("db_account.num_of_account = {} --- Type of account = {}".format(db_account.num_of_account, db_account.type_int_of_account))
                logger.warning("------------------------------------")
                
                # TODO: Injecter la dernière date en base de donnée dans w.iter_history(real_account, date) afin de limiter la vérification
                transactions_of_banks_account = w.iter_history(real_account)

                for transaction in transactions_of_banks_account:
                    # print(transaction)
                    transac = {}
                    Trans = Transactions()

                    Trans.account = db_account
                    # print(Trans.account)

                    # Debit date on the bank statement
                    transac['date'] = transaction.date  
                    Trans.date_of_transaction = transaction.date
                    # print(Trans.date_of_transaction)
                    
                    # Real date, when the payment has been made; usually extracted from the label or from credit card info
                    transac['rdate'] = transaction.rdate  
                    Trans.real_date_of_transaction = transaction.rdate
                    # print(Trans.real_date_of_transaction)

                    # Value date, or accounting date; usually for professional accounts
                    transac['vdate'] = transaction.vdate  
                    Trans.value_date_of_transaction = transaction.vdate
                    # print(Trans.value_date_of_transaction)

                    # Type of transaction, use TYPE_* constants', default=TYPE_UNKNOWN
                    transac['type'] = transaction.type  
                    Trans.type_int_of_transaction = transaction.type
                    # Trans.type_of_transaction = transaction.type
                    # print(Trans.type_int_of_transaction)

                    # Raw label of the transaction
                    transac['raw'] = transaction.raw  
                    Trans.name_of_transaction = transaction.raw
                    # print(Trans.name_of_transaction)

                    if transaction.category:
                        transac['category'] = transaction.category  # Category of the transaction
                        Trans.type_of_transaction = transaction.category
                    else:
                        transac['category'] = 'Unknown'  # Category of the transaction
                        Trans.type_of_transaction = 'Unknown'

                    if transaction.label:
                        transac['label'] = transaction.label  # Pretty label
                        # logger.warning('transac["label"] = transaction.label +++++ >>>> : %s', transaction.label)
                        Trans.label_of_transaction = transaction.label
                    else:
                        transac['label'] = transaction.raw 
                        Trans.label_of_transaction = transaction.raw
                        # logger.warning('transac["label"] = transaction.label +++++ >>>> : %s : NO LABEL FOUND - REPLACED BY RAW', transac['label'])
                    # print(Trans.label_of_transaction)

                    transac['amount'] = transaction.amount  # Amount of the transaction
                    Trans.amount_of_transaction = transaction.amount
                    # print(Trans.amount_of_transaction)

                    Trans.create_key_words()
                    # print(Trans.key_words)

                    Trans.unique_id_of_transaction = Trans.unique_id(account_id=db_account.num_of_account)
                    # print(Trans.unique_id_of_transaction)

                    if Trans.unique_id_of_transaction not in list_uniques:
                        Trans.save()
                        list_uniques.append(Trans.unique_id_of_transaction)
                        list_of_transactions.append(transac)
                        # print('Sauvegarde de Trans: ===>>>>>> {}\n'.format(Trans))
                        logger.warning('Sauvegarde de Trans: ===>>>>>> %s', Trans)


    context = {'list_of_transactions': list_of_transactions, }
    return context



@login_required
def bank_connection_and_load_transactions(request, pk):
    bank = get_object_or_404(Banks, pk=pk)
    w = Weboob()
    # TODO: Vérifier que les champs ne sont pas vide avant de lancer la connexion
    # TODO: si erreur de connexion, alors raise une erreur et revenir vers une autre page ?
    if request.method == 'POST':
        form = BankConnectionForm(instance=bank, data=request.POST)

        if form.is_valid():
            w.load_backend(
                bank.module_weboob.name_of_module, 
                bank.name_of_bank, 
                {'login': form.cleaned_data['bank_login'], 
                'password': form.cleaned_data['bank_password']}
            )
            
            # Get list of available account(s) in the bank
            list_of_accounts = list(w.iter_accounts())
            
            # Get list of transactions coming from bank history
            context = load_transactions(request, w, bank, list_of_accounts)
            # TODO: Rediriger vaer la liste transactions chargées
            return render(request, 'ManageGesfi/load_transactions_from_account.html', context)

    else:
        form = BankConnectionForm(instance=bank)
    
    context = {'bank': bank, 'form': form, }
    return render(request, 'banksandaccounts/bank_connection_and_load_transactions.html', context)


@login_required
def account_detail(request, account_id):
    account = Accounts.objects.get(id=account_id)
    context = {'account': account}
    return render(request, 'banksandaccounts/account_detail.html', context)


@login_required
def account_create(request):
    accounts_list = Accounts.objects.all()  # .filter(accounts__owner_of_account=request.user)

    if request.method == 'POST':
        form = AccountForm(data=request.POST)

        if form.is_valid():
            account = form.save(commit=False)
            # category.owner = request.user
            # account.owner_of_account.set(request.user.id)
            logger.warning('Création compte: ==/\== owner_of_account : %s', form.cleaned_data['owner_of_account'])
            account.save()
            # account.owner_of_account.set(request.user.id)
            # form.save_m2m()
            # return redirect('transactions_list', transaction.account.id)
            # TODO: prévoir une redirection vers la liste des comptes par banque
            # TODO: par défaut il faudrait que le propriétaire du compte soit défini dés la création (celui qui le crée est propriétaire)
            return redirect('banksandaccounts:accounts_list')
    else:
        form = AccountForm()

    context = {
        'all_accounts': accounts_info2(request, 0),
        # general information related to all accounts (due to "0") and used in sidebar

        'form': form,
        'accounts_list': accounts_list,
        'create': True
    }
    return render(request, 'banksandaccounts/account_edit.html', context)


@login_required
def account_edit(request, pk):
    account = get_object_or_404(Accounts, pk=pk)

    banks_list = Banks.objects.all()  # .filter(accounts__owner_of_account=request.user)

    if request.method == 'POST':
        form = AccountForm(instance=account, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('banksandaccounts:account_list', account.id)
    else:
        form = AccountForm(instance=account)

    # form.account = forms.Select(choices=Accounts.objects.all().filter(owner_of_account=request.user))

    context = {
        'account': account,
        'all_accounts': accounts_info2(request, 0),
        'banks_list': banks_list,
        'form': form,
        'create': False
    }
    return render(request, 'banksandaccounts/account_edit.html', context)


class AccountListView(LoginRequiredMixin, generic.ListView):
    model = Accounts

    class Meta:
        ordering = ['bank.name_of_bank', 'name_of_account']

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AccountListView, self).get_context_data(**kwargs)
        # Get total amount of all accounts of a user
        context['account_total'] = Transactions.objects.filter(account__owner_of_account=self.request.user).aggregate(Sum('amount_of_transaction'))
        # Get total amount by account
        context['accounts_info'] = accounts_info2(self.request, 0).filter(owner_of_account=self.request.user)
        return context

    def get_queryset(self):
        return Accounts.objects.filter(owner_of_account=self.request.user)

    context_object_name = 'accounts_list'  # your own name for the list as a template variable (not used)
    queryset = Accounts.objects.all()
    template_name = 'banksandaccounts/accounts_list.html'  # Specify your own template name/location

@login_required
def transaction_detail(request, transaction_id):
    transaction = Transactions.objects.get(id=transaction_id)
    context = {'transaction': transaction}
    return render(request, 'banksandaccounts/transaction_detail.html', context)


@login_required
def transaction_create(request):
    # TODO: How to obtain the list of accounts only available for the connected user ?
    banks_list = Banks.objects.all()  # .filter(accounts__owner_of_account=request.user)

    if request.method == 'POST':
        form = TransactionForm(data=request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            # category.owner = request.user
            transaction.save()
            # form.save_m2m()
            # return redirect('transactions_list', transaction.account.id)
            return redirect('banksandaccounts:account_list', transaction.account.id)

    else:
        form = TransactionForm()

    context = {
        'all_accounts': accounts_info2(request, 0),
        # general information related
        # to all accounts (due to "0") and used in sidebar

        'form': form,
        'banks_list': banks_list,
        'create': True
    }
    return render(request, 'banksandaccounts/transaction_edit.html', context)


@login_required
def transaction_edit(request, pk):
    # TODO: How to obtain the list of accounts only available for the connected user ?
    transaction = get_object_or_404(Transactions, pk=pk)
    # TODO: Tester le numéro unique de la transaction
    print('=============> num_of_account :: {}'.format(transaction.account.num_of_account))
    print('=============> UNIQUE_ID :: {}'.format(transaction.unique_id(account_id=transaction.account.num_of_account)))
    # print('=============> UNIQUE_ID :: {}'.format(transaction.unique_id()))

    banks_list = Banks.objects.all()  # .filter(accounts__owner_of_account=request.user)
    # account = forms.ChoiceField(queryset=Accounts.objects.all().filter(owner_of_account=request.user))

    # account = Accounts.objects.all().filter(accounts__owner_of_account=request.user)
    # XLH print('User ==== {}'.format(request.user))
    # XLH print('=======================================================================')
    # XLH print('Request {}'.format(request.POST))
    # XLH print('=======================================================================')

    list_accounts = Accounts.objects.all().filter(owner_of_account=request.user)
    # XLH print('Choice ==== {}'.format(list_accounts))
    # choix = [tuple(list_accounts)]
    # print('Choice ==== {}'.format(choix))
    # print(form.as_table())

    if request.method == 'POST':
        form = TransactionForm(instance=transaction, data=request.POST)
        # form.account = Accounts.objects.all().filter(owner_of_account=request.user)
        # form.account = forms.ChoiceField(queryset=Accounts.objects.all().filter(owner_of_account=request.user))
        # XLH print('User ==== {}'.format(request.user))
        # XLH print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        # XLH print('Request {}'.format(request.POST))
        # XLH print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        # form = form.as_ul()
        if form.is_valid():
            form.save()
            return redirect('banksandaccounts:account_list', transaction.account.id)

            # return redirect('budget')
    else:
        data = {'Account': list_accounts, }
        # print(data)
        form = TransactionForm(instance=transaction)
        # print('############## form = TransactionForm(instance=transaction)  {}'.format(form))
        # form = form.as_table()
        # form.account = forms.ChoiceField(choices=Accounts.objects.all().filter(owner_of_account=request.user))

    # *****************************************************************************************************************
    form.account = forms.Select(choices=Accounts.objects.all().filter(owner_of_account=request.user))
    # print(form.account.choices)
    # form.account = forms.ChoiceField(choices=choix)

    # *****************************************************************************************************************

    context = {
        'transaction': transaction,
        'all_accounts': accounts_info2(request, 0),
        # general information related
        # to all accounts (due to "0") and used in sidebar
        # 'account': account,
        'banks_list': banks_list,
        'form': form,
        'create': False
    }
    return render(request, 'banksandaccounts/transaction_edit.html', context)


# TODO: to verify if this function is used (transactions_with_tag ?: not sure)
@login_required
def transactions_with_tag(request, tag_name):
    if tag_name == "*ALL*":
        transactions = Transactions.objects.all()
    else:
        transactions = \
            Transactions.objects.filter(
                name_of_transaction__icontains=tag_name
            )

    tags_list = Tag.objects.filter(will_be_used_as_tag=True)
    context = {
        'tag_name': tag_name,
        'transactions': transactions,
        'tags_list': tags_list
    }
    return render(
        request,
        'banksandaccounts/transactions_with_tag.html',
        context
    )
