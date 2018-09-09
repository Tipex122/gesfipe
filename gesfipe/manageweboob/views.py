from django.shortcuts import render

from weboob.core import Weboob
from weboob.capabilities.bank import CapBank

# Create your views here.


def check_weboob_repositories(w):
    if not w.repositories.check_repositories():
        w.repositories.update()
        print("WeBoob a été mis à jour (répertoires de config) \n")
    else:
        print("Répertoires à jour\n")
    return w

@login_required
def update_list_of_available_banks(request):
    w = Weboob()
    check_weboob_repositories(w)

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

    # acc = next(iter(w.iter_accounts()))
    # bal = acc.balance
    # print('\n ********** \n {}\n **********\n'.format(acc))
    # print('\n ********** \n {}\n **********\n'.format(bal))

    print('workdir : {}'.format(w.workdir))
    print('repositories : {} \n'.format(w.repositories.modules_dir))
    print("========================================================================================================\n")

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

