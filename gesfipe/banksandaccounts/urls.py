from django.conf.urls import url

from . import views

#TODO: Mettre à jour de Django 2.0

urlpatterns = [
    url(r'^transactions_list/$', views.transactions_list, name='transactions_list'),
    url(r'^toto/$', views.TransactionsListView.as_view(), name='transactions_list3'),

    # url(r'^toto/$', views.transactions_list2, name='transactions_list2'),
    # url(r'^$', views.TransactionsListView.as_view(), name='transactions_list'),

    url(r'^transaction_detail/(?P<transaction_id>[0-9]+)/$', views.transaction_detail, name='transaction_detail'),
    url(r'^transaction_edit/(?P<pk>[0-9]+)/$', views.transaction_edit, name='transaction_edit'),
    url(r'^transaction_create/$', views.transaction_create, name='transaction_create'),

    url(r'^account/(?P<account_id>[0-9]+)/$', views.account_list, name='account_list'),
    url(r'^banks_and_accounts_list/$', views.banks_and_accounts_list, name='banks_and_accounts_list'),
    url(r'^$', views.banks_and_accounts_list, name='home'),
    #    url(r'^keywords/(?P<tag_name>[a-z,\',\*,A-Z]+)/$',
    #    views.transactions_with_tag, name='transactions_with_tag'),
]

