from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import search as search_views
from .views import *

from django.contrib import admin
#from controlcenter.views import controlcenter

# TODO: to adapt to Django 2.0

app_name = 'managegesfi'

urlpatterns = [
    url(r'search/$', search_views, name='search'),
    url(r'display_meta/$', display_meta, name='display_meta'),

    # TODO: To delete following url 'info_to_print'
    url(r'^info_to_print/(?P<pk>[0-9]+)/$', connect_bank, name='info_to_print'),

    url(r'transactions_by_category/search_categories/$', tag_category_edit, name='tag_category_edit'),
    url(r'^transactions_by_category/(?P<pk>)$', transactions_by_category, name='transactions_by_category'),
    url(r'^transactions_by_category/(?P<pk>[0-9]+)/$', transactions_by_category, name='transactions_by_category'),

    # url(r'list_of_available_banks/$', get_list_of_managed_banks, name='get_list_of_managed_banks'),
    url(r'list_of_available_accounts/$', get_list_of_available_accounts, name='get_list_of_available_accounts'),
    url(r'load_transactions/$', load_transactions, name='load_transactions'),
    url(r'list_unique_numbers/$', list_unique_numbers, name='list_unique_numbers'),

    # url(r'progress_bar/(?P<task_id>[\w-]+)/$', progress_view, name='progress_view_status')
    url(r'progress_bar/$', progress_view, name='progress_view_status')
]

