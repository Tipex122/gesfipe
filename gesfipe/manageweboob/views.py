from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from weboob.core import Weboob
from weboob.capabilities.bank import CapBank
# from weboob.core.backendscfg import BackendsConfig

from gesfipe.banksandaccounts.models import Accounts as db_Accounts
from gesfipe.manageweboob.models import WeboobModules

import logging

logger = logging.getLogger(__name__)


# Create your views here.


def check_weboob_repositories(w):
    if not w.repositories.check_repositories():
        w.repositories.update()
        print("WeBoob a été mis à jour (répertoires de config) \n")
    else:
        print("Répertoires à jour\n")
    return w


@login_required
def update_list_of_managed_banks(request):
    w = Weboob()
    # check_weboob_repositories(w)

    # TODO: Ajouter la liste des modules Banks accessibles dans la base de données
    # TODO: voir si cette fonction ne doit pas faire partie de WeboobModules (models.py). Comparer d'abord si le module existe

    '''
    w.load_backends(CapBank)
    print('get_all_modules_info societegenerale:::: \n {}'.format(
        w.repositories.get_all_modules_info(CapBank)['societegenerale'].description))
    print('\n *************************\n {} \n *************************** \n'.format(list(w.iter_accounts())))

    l = list(w.iter_accounts())
    for account in l:
        # Test if get_account works
        print("\n====================================================================================================")
        print('Account Id: {0} \t\t Account description: {1}'.format(account.id, account.label))
        print("====================================================================================================")
    '''

    listbanks = w.repositories.get_all_modules_info(CapBank)
    # TODO: créer form quand on clique sur banque pour entrer login et password
    amex = w.load_backend('americanexpress', 'American Express', {'login': '', 'password': ''})
    list_accounts = list(amex.iter_accounts())

    logger.warning("=================================================================================================")
    logger.warning("info sur amex : _____/\_______ : %s", amex)
    logger.warning("info sur amex : _____/\_______ : %s", amex.CONFIG)
    logger.warning("info sur amex : _____/\_______ : %s", amex.iter_accounts())
    # logger.info("info sur amex : _____/\_______ : %s", amex.type)
    for account in list_accounts:
        logger.warning("Accounts of AMEX: ...... : %s", account)
    logger.warning("=================================================================================================")

    # db_accounts_list = db_Accounts.objects.all().filter(owner_of_account=request.user)
    db_accounts_list = db_Accounts.objects.all()

    list_of_db_accounts = []

    for key in db_accounts_list:
        list_of_db_accounts.append(key.num_of_account)
    '''
    if amex.id not in list_of_db_accounts:
        new_account = db_Accounts()
        new_account.num_of_account = amex.id
        new_account.name_of_account = amex.label
        new_account.type_int_of_account = amex.type
        # TODO: affecter un user + le type (en texte)
        # new_account.owner_of_account = request.user
        # print('new_account.name_of_account = {}'.format(new_account.name_of_account))
        new_account.save()
    
    
    logger.info("=================================================================================================")
    logger.info("info sur amex : _____/\_______ : %s", amex)
    logger.info("info sur amex : _____/\_______ : %s", amex.id)
    logger.info("info sur amex : _____/\_______ : %s", amex.label)
    logger.info("info sur amex : _____/\_______ : %s", amex.type)
    logger.info("=================================================================================================")
    '''

    # module = w.load_backend("societegenerale", "societegenerale")
    # print('********************* w.load_backend(): {} \n'.format(module))
    # print('********************* w.backends_config.get_backend: {}'.format(w.backends_config.get_backend('societegenerale')))
    # print('w.load_or_install_module("axabanque") : {}'.format(w.load_or_install_module('axabanque')))
    # print('\n *************************\n {} \n *************************** \n'.format(list(w.iter_accounts())))

    # if not w.backends_config.backend_exists('cic'):
    #    w.backends_config.add_backend('cic','cic', {'login': 'toto', 'password': 'tutu'})

    # print('\n _____#####_____\n iter_backedns : {} \n _____####_____\n'.format(list(w.backends_config.iter_backends())))

    #    print('********************* w.backends_config.get_backend: {}'.format(
    #        w.backends_config.get_backend('axabanque')))

    # acc = next(iter(w.iter_accounts()))
    # bal = acc.balance
    # print('\n ********** \n {}\n **********\n'.format(acc))
    # print('\n ********** \n {}\n **********\n'.format(bal))

    # print("========================================================================================================")
    # print('workdir : {}'.format(w.workdir))
    # print('repositories : {}'.format(w.repositories.modules_dir))
    #  print("========================================================================================================")

    logger.warning("=================================================================================================")
    logger.warning('logger.warning Workdir ==> ==> ==> : %s', w.workdir)
    logger.warning('logger.warning Repositories ==> ==> ==> : %s', w.repositories.modules_dir)
    logger.warning("=================================================================================================")

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

    return render(request, 'ManageWeboob/list_of_available_backends.html', context)


@login_required
def load_list_of_modules_in_database(request):
    '''
    function to load list of weboob modules in database
    :param request:
    :return:
    '''
    w = Weboob()
    w.update()

    listbanks = w.repositories.get_all_modules_info(CapBank)

    db_wm_list = WeboobModules.objects.all()

    list_of_db_modules = []
    for key in db_wm_list:
        list_of_db_modules.append(key.name_of_module)

    list_of_banks = []
    for key, val in listbanks.items():
        wm = WeboobModules()
        data_bank = {}

        data_bank['module'] = key
        wm.name_of_module = key

        data_bank['description'] = val.description
        wm.description_of_module = val.description

        list_of_banks.append(data_bank)
        if wm.name_of_module not in list_of_db_modules:
            wm.save()

    list_of_banks.sort(key=lambda k: k['module'])

    db_wm_list = WeboobModules.objects.all()


    # context = {'list_of_banks': list_of_banks}
    context = {'list_of_banks': db_wm_list}

    return render(request, 'ManageWeboob/list_of_available_modules.html', context)
