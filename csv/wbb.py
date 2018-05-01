#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import inspect
from datetime import datetime, timedelta
from collections import OrderedDict

import weboob.applications

from weboob.tools.application.console import ConsoleApplication

from weboob.applications.weboobcfg import WeboobCfg
from weboob.applications.boobank import Boobank

from weboob.core import Weboob
from weboob.capabilities.bank import CapBank


wcfg = WeboobCfg()
test = wcfg.do_modules('modules CapBank,')
# print(test)


# wcfg.do_list('CapBank')

print(wcfg)


# bbk = Boobank()
# test_bbk = bbk.do_list('CapBank,')
# print(test_bbk)

w = Weboob()

# =============== It doesn't work ============ enter the good path !
# capApplicationDict = init_CapApplicationDict(w)
# print(list(capApplicationDict.keys()))

# for cle in capApplicationDict:
#     print('\n ==========> \n {}\n <==========\n'.format(cle))
# ==================================================================


w.load_backends(CapBank)

# capApplicationDict = w.init_CapApplicationDict()
# for cle in capApplicationDict:
#    print(cle)

# applications = capApplicationDict[cap]
# applications = capApplicationDict['CapBank']

# print('\n ==========> \n {}\n <==========\n'.format(application))

print('\n *************************\n {} \n *************************** \n'.format(list(w.iter_accounts())))

acc = next(iter(w.iter_accounts()))
bal = acc.balance
print('\n ********** \n {}\n **********\n'.format(acc))
print('\n ********** \n {}\n **********\n'.format(bal))

print('workdir : {}'.format(w.workdir))
print('repositories : {} \n'.format(w.repositories.modules_dir))
print('get_all_modules_info : {} \n'.format(w.repositories.get_all_modules_info(CapBank)))

if not w.repositories.check_repositories():
    w.repositories.update()
else:
    print("Répertoires à jour \n")
    # w.repositories.update()

listbanks = w.repositories.get_all_modules_info(CapBank)
for key, val in listbanks.items():
    print("Banque key (Dict) : {} \t\t\t ===> \t {}".format(key, val.description))

print('get_all_modules_info societegenerale:::: \n {}'.format(w.repositories.get_all_modules_info(CapBank)['societegenerale'].description))


l = list(w.iter_accounts())
for account in l:
    # Test if get_account works
    print('\nAccount Id: {0} \t\t Account description: {1}'.format(account.id, account.label))
    # w.show_history(account.id)
    print(w.iter_history(account.id))
    m = w.iter_history(account)
    for transaction in m:
        print(transaction)
    # _id = w.get_account(account.id)
    # w.assertTrue(_id.id == account.id)
    # Methods can use Account objects or id. Try one of them
    # id_or_account = random.choice([account, account.id])
    # history = list(w.iter_history(account.id))
    # print(_id)
