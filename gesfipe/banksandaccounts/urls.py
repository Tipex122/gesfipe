from django.conf.urls import url

from . import views

#TODO: Mettre à jour de Django 2.0

urlpatterns = [
    url(r'^transactions_list/$', views.transactions_list, name='transactions_list'),
    url(r'^toto/$', views.TransactionsListView.as_view(), name='transactions_list3'),

    # url(r'^toto/$', views.transactions_list2, name='transactions_list2'),
    # url(r'^$', views.TransactionsListView.as_view(), name='transactions_list'),

    url(r'^bank_detail/(?P<bank_id>[0-9]+)/$', views.bank_detail, name='bank_detail'),
    url(r'^bank_edit/(?P<pk>[0-9]+)/$', views.bank_edit, name='bank_edit'),
    url(r'^bank_create/$', views.bank_create, name='bank_create'),
    url(r'^banks_list/$', views.banks_list, name='banks_list'),

    url(r'^account_detail/(?P<account_id>[0-9]+)/$', views.account_detail, name='account_detail'),
    url(r'^account_edit/(?P<pk>[0-9]+)/$', views.account_edit, name='account_edit'),
    url(r'^account_create/$', views.account_create, name='account_create'),
    url(r'^accounts_list/$', views.AccountListView.as_view(), name='accounts_list'),

    url(r'^transaction_detail/(?P<transaction_id>[0-9]+)/$', views.transaction_detail, name='transaction_detail'),
    url(r'^transaction_edit/(?P<pk>[0-9]+)/$', views.transaction_edit, name='transaction_edit'),
    url(r'^transaction_create/$', views.transaction_create, name='transaction_create'),

    url(r'^account/(?P<account_id>[0-9]+)/$', views.account_list, name='account_list'),
    url(r'^banks_and_accounts_list/$', views.banks_and_accounts_list, name='banks_and_accounts_list'),
    url(r'^$', views.banks_and_accounts_list, name='home'),
    #    url(r'^keywords/(?P<tag_name>[a-z,\',\*,A-Z]+)/$',
    #    views.transactions_with_tag, name='transactions_with_tag'),
]

