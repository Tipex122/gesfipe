from django.shortcuts import render
# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.db.models import Q
from django.shortcuts import get_list_or_404
# from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Gefipe
from gesfipe.manageweboob.models import WeboobModules
from gesfipe.banksandaccounts.models import *
from gesfipe.banksandaccounts.models import Accounts as db_Accounts
from gesfipe.categories.models import *
from gesfipe.users.models import User

# from categories.forms import TagForm

# Weboob
from weboob.core import Weboob
from weboob.capabilities.bank import CapBank

import logging


logger = logging.getLogger(__name__)


# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logs/gesfipe.log',
                    filemode='w')


# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)


# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-12s: %(message)s')

# tell the handler to use this format
console.setFormatter(formatter)

# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Now, we can log to the root logger, or any other logger. First the root...
logging.info('Jackdaws love my big sphinx of quartz.')
logging.debug('Test de debug sur "logging"')

# Now, define a couple of other loggers which might represent areas in your
# application:

logger1 = logging.getLogger(__name__)
logger2 = logging.getLogger('myapp.area2')

logger.debug('## LOGGER ## - Test de LOGGER')

logger1.info('## logger1 ## zephyrs blow, vexing daft Jim.')
logger1.warning('## logger1 ## How quickly daft jumping zebras vex.')
logger2.warning('## logger2 ## Jail zesty vixen who grabbed pay from quack.')
logger2.error('## logger2 ## The five boxing wizards jump quickly.')



# Create your views here.

@login_required
def search(request):
    if 'q' in request.GET:
        querystring = request.GET.get('q').strip()
        if len(querystring) == 0:
            return redirect('/search/')

        try:
            search_type = request.GET.get('type')
            if search_type not in ['banks', 'accounts', 'transactions', 'categories']:
                search_type = 'banks'

        except Exception:
            search_type = 'banks'

        count = {}
        results = {'banks': Banks.objects.filter(Q(name_of_bank__icontains=querystring) |
                                                 Q(num_of_bank__icontains=querystring)),
                   'accounts': Accounts.objects.filter(Q(name_of_account__icontains=querystring) |
                                                       Q(num_of_account__icontains=querystring)),
                   'transactions': Transactions.objects.filter(
                       Q(name_of_transaction__icontains=querystring) |
                       Q(date_of_transaction__icontains=querystring) |
                       Q(type_of_transaction__icontains=querystring) |
                       Q(amount_of_transaction__icontains=querystring) |
                       Q(type_of_transaction__icontains=querystring)),
                   'categories': Category.objects.filter(Q(name__icontains=querystring) |
                                                         Q(description__icontains=querystring) |
                                                         Q(amount__icontains=querystring))}

        # results['transactions'] = Transactions.objects.filter(name_of_transaction__icontains=querystring, parent=None)
        # TODO: chercher la différence entre une recherche "Q()" et la notion de parent
        # TODO: chercher sur une date ... hé hé

        count['banks'] = results['banks'].count()
        count['accounts'] = results['accounts'].count()
        count['transactions'] = results['transactions'].count()
        count['categories'] = results['categories'].count()

        return render(request, 'ManageGesfi/results.html', {
            'hide_search': True,
            'querystring': querystring,
            'active': search_type,
            'count': count,
            'results': results[search_type],
        })
    else:
        return render(request, 'ManageGesfi/search.html', {'hide_search': True})


@login_required
def tag_category_edit(request):
    """
    Allocate a category to each transaction containing an identified Tag
    """
    categories_list = Category.objects.all()
    transactions_with_category = list()
    tags_list = Tag.objects.filter(will_be_used_as_tag=True)
    for tag in tags_list:
        transactions_with_tag = Transactions.objects.filter(name_of_transaction__icontains=tag.tag)
        if transactions_with_tag is not None:
            for transaction in transactions_with_tag:
                if tag.category is not None:
                    transaction.category_of_transaction = tag.category
                    transactions_with_category.append(transaction.name_of_transaction)
                    transaction.save()

    transactions = Transactions.objects.all()
    ancestors = Category.objects.filter(parent=None)
    context = {'transactions': transactions, 'categories_list': categories_list, 'ancestors': ancestors}
    return render(request, 'ManageGesfi/tag_category.html', context)


@login_required
def transactions_by_category(request, pk=None):
    """
    List of transactions by category.
    For all categories or category by category selected
    """
    # TODO: In transactions_by_category.html to list transactions of the catagory selected AND descendant of the category
    if pk == '' or get_object_or_404(Category, pk=pk).is_root_node():
        transactions = Transactions.objects.all().order_by('category_of_transaction__name')
        ancestors = Category.objects.filter(parent=None)
    else:
        category_selected = get_object_or_404(Category, pk=pk)
        ancestors = category_selected.get_ancestors(include_self=True)
        transactions = Transactions.objects.filter(category_of_transaction=category_selected)

    categories = Category.objects.all()

    context = {'transactions': transactions, 'ancestors': ancestors, 'categories': categories, }
    return render(request, 'ManageGesfi/transactions_by_category.html', context)


@login_required
def display_meta(request):
    values = request.META.items()
    meta_info = []
    for k, v in values:
        info = {}
        info['data'] = k
        info['description'] = v
        meta_info.append(info)

    meta_info.sort(key=lambda k: k['data'])
    context = {'meta_info': meta_info}

    return render(request, 'ManageGesfi/list_of_meta_info.html', context)


def check_weboob_repositories(w):
    if not w.repositories.check_repositories():
        w.repositories.update()
        print("WeBoob a été mis à jour (répertoires de config) \n")
    else:
        print("Répertoires à jour\n")
    return w

'''
@login_required
def get_list_of_managed_banks(request):
    w = Weboob()
    w.update()
    # check_weboob_repositories(w)

    
    # w.load_backends(CapBank)
    # print('get_all_modules_info societegenerale:::: \n {}'.format(
    #     w.repositories.get_all_modules_info(CapBank)['societegenerale'].description))
    # print('\n *************************\n {} \n *************************** \n'.format(list(w.iter_accounts())))

    # l = list(w.iter_accounts())
    # for account in l:
    #     # Test if get_account works
    #     print("\n====================================================================================================")
    #     print('Account Id: {0} \t\t Account description: {1}'.format(account.id, account.label))
    #     print("====================================================================================================")
    

    listbanks = w.repositories.get_all_modules_info('CapBank')

    # acc = next(iter(w.iter_accounts()))
    # bal = acc.balance
    # print('\n ********** \n {}\n **********\n'.format(acc))
    # print('\n ********** \n {}\n **********\n'.format(bal))

    logger.warning("+++ workdir : %s", w.workdir)
    logger.warning("+++ repositories : %s", w.repositories.modules_dir)

    print("========================================================================================================")
    print('workdir : {}'.format(w.workdir))
    print('repositories : {}'.format(w.repositories.modules_dir))
    print("========================================================================================================")

    list_of_banks = []
    for key, val in listbanks.items():
        # print("Banque key (Dict) : {} \t\t\t ===> \t {}".format(key, val.description))
        data_bank = {}
        data_bank['module'] = key
        data_bank['description'] = val.description
        # print('val de account: {}'.format(val))
        list_of_banks.append(data_bank)
    list_of_banks.sort(key=lambda k: k['module'])

    context = {'list_of_banks': list_of_banks}

    return render(request, 'ManageGesfi/list_of_available_backends.html', context)
'''

@login_required
def get_list_of_available_accounts(request):
    '''
    Function to get list of accounts of  bank with local backend (cf. ~/.config/weboob/backends
    :param request:
    :return: render: to render list_of_banks and list_of_accounts (but banks and account are not linked (to be updated)
    '''
    logger.warning("Entering in function get_list_of_available_accounts")
    w = Weboob()
    check_weboob_repositories(w)
    listbanks = w.load_backends(CapBank)
    list_of_banks = []
    list_of_db_accounts = []

    # db_accounts_list = db_Accounts.objects.all().filter(owner_of_account=request.user)
    db_accounts_list = db_Accounts.objects.all()

    for key in db_accounts_list:
        # print('db_accounts_list::::::: {}'.format(key.num_of_account))
        list_of_db_accounts.append(key.num_of_account)

    for key, val in listbanks.items():
        # print("Banque key (Dict) : {} \t\t\t ===> \t {}".format(key, val.description))
        data_bank = {}
        data_bank['module'] = key
        data_bank['name'] = val.DESCRIPTION
        list_of_banks.append(data_bank)
    list_of_banks.sort(key=lambda k: k['module'])

    # print('************************ : {}'.format(list_of_banks))
    logger.warning('list_of_banks ==> ==> ==> : %s', list_of_banks)

    # TODO: cela fonctionne car je n'ai qu'une banque  en backends mais sinon la liste des "accounts" sera globale.
    # TODO: il manque donc l'association account et banque

    list_of_accounts = list(w.iter_accounts())

    for real_account in list_of_accounts:
        # print('REAL ACCOUNT: {}'.format(real_account))
        # print('LIST_OF_DB_ACCOUNTS: {}'.format(list_of_db_accounts))
        if real_account.id in list_of_db_accounts:
            # print('if real_account.id in list_of_db_accounts: ==>> REAL ACCOUNT.ID: {}'.format(real_account.id))
            # print('if real_account.id in list_of_db_accounts: ==>> LIST_OF_DB_ACCOUNTS: {}'.format(list_of_db_accounts))
            # erase old data and replace by data coming from bank
            db_account = db_Accounts.objects.get(num_of_account=real_account.id)
            # print('if real_account.id == db_account.num_of_account en base de données: {}  -- à la banque: {}'.format(db_account.name_of_account, real_account.label))
            db_account.name_of_account = real_account.label
            db_account.type_int_of_account = real_account.type
            db_account.balance_of_account = real_account.balance
            # TODO: ajouter le nom de la banque au compte
            # TODO: ajouter le user en cours
            # db_account.bank = real_account.parent.name
            # u = User.objects.get(name=request.user.name)
            # u.db_accounts_set.add(db_account)
            # db_account.owner_of_account.set([request.user,])
            db_account.save()

        else:
            # print('Else: ==>> REAL ACCOUNT.ID: {}'.format(real_account.id))
            #  print('Else: ===> LIST_OF_DB_ACCOUNTS: {}'.format(list_of_db_accounts))
            # create account
            new_account = db_Accounts()
            new_account.num_of_account = real_account.id
            new_account.name_of_account = real_account.label
            new_account.type_int_of_account = real_account.type
            new_account.balance_of_account = real_account.balance
            # TODO: affecter un user + le type (en texte)
            # new_account.owner_of_account = request.user
            # print('new_account.name_of_account = {}'.format(new_account.name_of_account))
            new_account.save()
            # new_account.owner_of_account.set(request.user)
            # new_account.create()

    # list_of_accounts.sort(key=lambda k: k['label'])
    context = {'list_of_banks': list_of_banks, 'list_of_accounts': list_of_accounts, }

    logger.warning("Entering in function get_list_of_available_accounts")

    return render(request, 'ManageGesfi/list_of_available_accounts.html', context)


@login_required
def list_unique_numbers(request):
    # list_unique = get_list_or_404(Transactions, unique_id_of_transaction<>False)
    # TODO: To delete following line which is not used
    list_unique = Transactions.objects.all()
    
    list_unique_of_numbers()
    # logger.warning('List of unique Numbers ==> ==> ==> : %s', list_unique)
    context = {'list_unique': list_unique}
    return render(request, 'ManageGesfi/list_of_unique_numbers.html', context)


def list_unique_of_numbers():
    '''
    Function to obtain the list of unique Id of each transaction
    In addition : replace 'unique_id' by a true unique number
    :return: list of Transactions.unique_id_of_transaction
    '''
    transac = Transactions.objects.all()
    list_of_numbers = []
    for trans in transac:
        num_id = trans.unique_id_of_transaction
        if num_id == 'unique_id':
            # To compute a real 'unique_id' (due to creation of "unique_id_of_transaction" 
            # filled with 'unique_id' when this field has been created in database)
            num_id = trans.unique_id(account_id=trans.account.num_of_account)
            trans.unique_id_of_transaction = num_id
            trans.save()

        list_of_numbers.append(trans.unique_id_of_transaction)
    
    # logger.warning('List of unique Numbers ==> ==> ==> : %s', list_of_numbers)
    return list_of_numbers

# TODO: function to delete ==> use password stored on local disc
@login_required
def load_transactions(request):
    '''
    Function to download transactions (or any related information) from banks through backends managed by Weboob
    And load them in the database managed by Gesfi
    :param request:
    :return: render: to render the list of transactions got from accounts managed by Weboob Backends
    '''

    w = Weboob()

    # Check if repositories where à located Backends are up to date
    check_weboob_repositories(w)

    # List of Banks in Backends with Weboob (for which we have te capability to connect with to get information)
    listbanks = w.load_backends(CapBank)

    # List of accounts got from Banks
    list_of_accounts = list(w.iter_accounts())

    # List of accounts in DataBase manage by Gesfipe
    db_accounts_list = Accounts.objects.all().filter(owner_of_account=request.user)
    print(db_accounts_list)

    # list_trans = Transactions.objects.all()
    list_uniques = list_unique_of_numbers()
    # TODO: Vérifier d'abord si la liste chargée existe déjà dans la base de données (via comparaison avec unique_id_of_transaction)

    list_of_transactions = []

    for real_account in list_of_accounts:
        # print(real_account)
        for db_account in db_accounts_list:
            if real_account.id == db_account.num_of_account:
                logger.warning("------------------------------------")
                logger.warning("real_account.id = {} ******  db_account.num_of_account = {}".format(real_account.id,
                                                                               db_account.num_of_account))
                logger.warning("Type of account = {}".format(db_account.type_int_of_account))
                logger.warning("------------------------------------")
                # TODO: Injecter la dernière date en base de donnée dans w.iter_history(real_account, date) afin de limiter la vérification
                transactions_of_banks_account = w.iter_history(real_account)

                for transaction in transactions_of_banks_account:
                    # print(transaction)
                    transac = {}
                    Trans = Transactions()

                    Trans.account = db_account
                    # print(Trans.account)

                    transac['date'] = transaction.date  # Debit date on the bank statement
                    Trans.date_of_transaction = transaction.date
                    # print(Trans.date_of_transaction)

                    # Real date, when the payment has been made; usually extracted from the label or from credit card info
                    if transaction.rdate:
                        transac['rdate'] = transaction.rdate
                        Trans.real_date_of_transaction = transaction.rdate
                    else:
                        transac['rdate'] = transaction.date
                        Trans.real_date_of_transaction = transaction.date
                    # print(Trans.real_date_of_transaction)

                    # Value date, or accounting date; usually for professional accounts
                    if transaction.vdate:
                        transac['vdate'] = transaction.vdate
                        Trans.value_date_of_transaction = transaction.vdate
                    else:
                        transac['vdate'] = transaction.rdate
                        Trans.value_date_of_transaction = transaction.rdate
                    # print(Trans.value_date_of_transaction)

                    transac[
                        'type'] = transaction.type  # Type of transaction, use TYPE_* constants', default=TYPE_UNKNOWN
                    Trans.type_int_of_transaction = transaction.type
                    # Trans.type_of_transaction = transaction.type
                    # print(Trans.type_int_of_transaction)

                    transac['raw'] = transaction.raw  # Raw label of the transaction
                    Trans.name_of_transaction = transaction.raw
                    # print(Trans.name_of_transaction)

                    transac['category'] = transaction.category  # Category of the transaction
                    Trans.type_of_transaction = transaction.category
                    # logger.warning('transaction.category ==> ==> ==> : %s', transaction.category)
                    # Trans.category_of_transaction = transaction.category
                    # print(Trans.type_of_transaction)

                    transac['label'] = transaction.label  # Pretty label
                    Trans.label_of_transaction = transaction.label
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

    context = {'list_of_accounts': list_of_accounts, 'list_of_transactions': list_of_transactions, }

    return render(request, 'ManageGesfi/load_transactions_from_account.html', context)



# TODO: prévoir une fonction qui vérifie si la banque existe, sinon la créer et créer une "form" pour récupérer login et password
# TODO: fonction non testée
@login_required
def connect_bank(request, pk):
    '''
    Function to connect to a bank
    :param request:
    :param kwargs:
    :return: HttpResponse
    '''

    module = get_object_or_404(WeboobModules, pk=pk)

    bank_in_database = Banks.objects.filter(module_weboob=module.name_of_module)

    if bank_in_database:
        logger.warning("bank in database with corresponding webbo module: %s", bank_in_database)
        context = {'data_to_print': module.name_of_module}
    else:
        logger.warning("No bank found with weboob module names: %s", module.name_of_module)
        context = {'data_to_print': "No bank  found in database with module named {}".format(module.name_of_module)}

    return render(request, 'info_to_print.html', context)
