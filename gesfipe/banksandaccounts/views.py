from django.shortcuts import render

# Create your views here.
# from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render

from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.http import HttpResponse
from django.db.models import Avg, Sum, Min, Max, Count

from gesfipe.categories.models import Tag

from django.contrib.auth.decorators import login_required

from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


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
    banks_list = Banks.objects.all().filter(accounts__owner_of_account=request.user)
    accounts_list = Accounts.objects.all().filter(owner_of_account=request.user)
    account_total =\
        Transactions.objects.filter(account__owner_of_account=request.user).aggregate(total=Sum('amount_of_transaction'))
    # TODO: To place num_visits on each view and all contexts to get the number of view on each bottom page (or only on the main page?)
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
        'BanksAndAccounts/banks_and_accounts_list.html',
        context
    )


@login_required
def transactions_list(request):
    # banks = Banks.objects.all()
    banks = Banks.objects.all().filter(accounts__owner_of_account=request.user)
    # accounts = Accounts.objects.all()
    # transaction_list = Transactions.objects.all()
    transaction_list = Transactions.objects.filter(account__owner_of_account=request.user)

    # account_total = Transactions.objects.aggregate(Sum('amount_of_transaction'))
    account_total = transaction_list.aggregate(Sum('amount_of_transaction'))

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Page de 25 lignes
    paginator = Paginator(transaction_list, 25)
    page = request.GET.get('page')

    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)
    # TODO: vérifier si on a vraiment besoin de tout ce contexte
    # all_accounts is used for sidebar
    # - accounts_info is used for selection of one account
    context = {
        'banks': banks,  # used for dispatching accounts by bank in sidebar
        # 'accounts': accounts,                # ???
        'transactions': transactions,
        # used to list transactions related to account(s)
        'account_total': account_total,
        # sum of all transactions ==> not really used in fact
        'accounts_info': accounts_info2(request, 0),
        # general information related to all accounts (due to "0")
        'all_accounts': accounts_info2(request, 0),
        # general information related
        # to all accounts (due to "0") and used in sidebar
        'num_visits': num_visits,
        # to count the number of visit on the main page (transactions_list2.html only)
        # just for test to use django.sessions middleware
    }
    return render(request, 'BanksAndAccounts/transactions_list.html', context)


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
        context['all_accounts'] = accounts_info2(self.request,0)

        return context

    def get_queryset(self):
        return Transactions.objects.filter(account__owner_of_account=self.request.user)

    context_object_name = 'transactions_list'  # your own name for the list as a template variable
    queryset = Transactions.objects.all() #[:55] Get 55 transactions
    template_name = 'BanksAndAccounts/transactions_list3.html'  # Specify your own template name/location


@login_required
def account_list(request, account_id):
    transactions_list = Transactions.objects.filter(account_id=account_id)
    # transactions_list = Transactions.objects.get(id=account_id)

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    account_total = Transactions.objects.filter(
            account_id=account_id).aggregate(Sum('amount_of_transaction'))

    # Page de 25 lignes
    paginator = Paginator(transactions_list, 25)
    page = request.GET.get('page')

    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)

    # accounts = Accounts.objects.all()
    # banks = Banks.objects.all()
    banks = Banks.objects.all().filter(accounts__owner_of_account=request.user)

    context = {
        'banks': banks,
        # used for dispatching accounts by bank in sidebar
        'transactions': transactions, # pour utilisation avec transactions_list.html
        # 'transactions_list': transactions_list, # pour utilisation avec transactions_list3.html

        # used to list transactions related to account(s)
        'account_total': account_total,
        # sum of all transactions ==> not really used in fact
        # 'accounts_info': accounts_info(account_id),
        'accounts_info': accounts_info2(request, account_id),
        # general information related to selectede account
        # 'all_accounts': accounts_info(0)
        'all_accounts': accounts_info2(request, 0),
        # general information related
        # to alla accounts (due to "0") and used in sidebar
        'num_visits': num_visits,
        # to count the number of visit on the main page (transactions_list2.html only)
        # just for test to use django.sessions middleware

    }

    return render(request, 'BanksAndAccounts/transactions_list.html', context)


@login_required
def transaction_detail(request, transaction_id):
    transaction = Transactions.objects.get(id=transaction_id)
    context = {'transaction': transaction}
    return render(request, 'BanksAndAccounts/transaction_detail.html', context)

@login_required
def transaction_create(request):
    # TODO: How to obtain the list of accounts only available for the connected user ?
    banks = Banks.objects.all().filter(accounts__owner_of_account=request.user)

    if request.method == 'POST':
        form = TransactionForm(data=request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            # category.owner = request.user
            transaction.save()
            # form.save_m2m()
            # return redirect('transactions_list', transaction.account.id)
            return redirect('account_list', transaction.account.id)

    else:
        form = TransactionForm()

    context = {
        'all_accounts': accounts_info2(request, 0),
        # general information related
        # to all accounts (due to "0") and used in sidebar

        'form': form,
        'banks':banks,
        'create': True
    }
    return render(request, 'BanksAndAccounts/transaction_edit.html', context)


@login_required
def transaction_edit(request, pk):
    # TODO: How to obtain the list of accounts only available for the connected user ?
    transaction = get_object_or_404(Transactions, pk=pk)
    banks = Banks.objects.all().filter(accounts__owner_of_account=request.user)
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
            return redirect('account_list', transaction.account.id)

            # return redirect('budget')
    else:
        data = {'Account':list_accounts,}
        print(data)
        form = TransactionForm(instance=transaction)
        print('############## form = TransactionForm(instance=transaction)  {}'.format(form))
        # form = form.as_table()
        # form.account = forms.ChoiceField(choices=Accounts.objects.all().filter(owner_of_account=request.user))

    # *****************************************************************************************************************
    form.account = forms.Select(choices=Accounts.objects.all().filter(owner_of_account=request.user))
    print(form.account.choices)
    # form.account = forms.ChoiceField(choices=choix)

    # *****************************************************************************************************************

    context = {
        'transaction': transaction,
        'all_accounts': accounts_info2(request, 0),
        # general information related
        # to all accounts (due to "0") and used in sidebar
        # 'account': account,
        'banks': banks,
        'form': form,
        'create': False
    }
    return render(request, 'BanksAndAccounts/transaction_edit.html', context)


# TODO: to verify if this function is used (transactions_with_tag ?: not sure)
@login_required
def transactions_with_tag(request, tag_name):
    if tag_name == "*ALL*":
        transactions = Transactions.objects.all()
    else:
        transactions =\
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
        'BanksAndAccounts/transactions_with_tag.html',
        context
    )

