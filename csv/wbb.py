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
from weboob.core.backendscfg import BackendsConfig
from weboob.capabilities.bank import CapBank

import codecs
streamWriter = codecs.lookup('utf-8')[-1]
sys.stdout = streamWriter(sys.stdout)
reload(sys) # il faut reloader pour pouvoir passer en encoding utf8
sys.setdefaultencoding('utf8')


wcfg = WeboobCfg()
test = wcfg.do_modules('modules CapBank,')
# print(test)


# wcfg.do_list('CapBank')

print("BeboobCfg - Configuration de Weboob : ~~~~~~~~~~~~~~~~~~~~~~~~~\n")
print(" {} \n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n".format(wcfg))


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

if not w.repositories.check_repositories():
    w.repositories.update()
    print("WeBoob a été mis à jour (répertoires de config) \n")
else:
    print("Repertoires à jour \n\n")
    # w.repositories.update()


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

# print('get_all_modules_info :\n {} \n'.format(w.repositories.get_all_modules_info(CapBank)))


listbanks = w.repositories.get_all_modules_info(CapBank)
print("========================================================================================================")
print("Liste des banques et de leur description")
print("========================================================================================================")
for key, val in listbanks.items():
    print("Banque key (Dict) : {} \t\t\t ===> \t {}".format(key, val.description))

print("========================================================================================================\n")

'''
# Les lignes entre guillemets fonctionnent - temporairement anhihilées pour gagner du temps

print('get_all_modules_info societegenerale:::: \n {}'.format(w.repositories.get_all_modules_info(CapBank)['societegenerale'].description))


l = list(w.iter_accounts())
for account in l:
    # Test if get_account works
    print("\n========================================================================================================")
    print('Account Id: {0} \t\t Account description: {1}'.format(account.id, account.label))
    print("========================================================================================================")
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
    #  print(_id)
'''

# Ligne ci-dessous crée une entrée CIC dans le fichier de config: /home/xavier/.config/weboob/backends
# par contre signale une erreur ensuite si mauvais login ou mdp dans le fichier de config
# lorsqu'on lance la fonction : list(w.iter_accounts())
# w.backends_config.add_backend('CIC', 'cic', {'login': '', 'password': ''})


print("------------------------------------------------------------------------------------")
print("------------------------------------------------------------------------------------")

