from django.conf.urls import url
from django.contrib.auth import views as auth_views

from .views import search as search_views
from .views import *

from django.contrib import admin
#from controlcenter.views import controlcenter

# TODO: to adapt to Django 2.0

urlpatterns = [
# SUPPR XLH    url(r'^login/$', auth_views.login, name='gesfi_login'),
# SUPPR XLH    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='gesfi_logout'),
    url(r'^search/$', search_views, name='search'),
    url(r'display_meta/$', display_meta, name='display_meta'),

#    url(r'^keywords/search_tags/$', search_tags, name='search_tags'),
#    url(r'^tag_edit/(?P<pk>)$', tag_edit, name='tag_edit'),
#    url(r'^tag_edit/(?P<pk>[0-9]+)/$', tag_edit, name = 'tag_edit'),
    url(r'^transactions_by_category/search_categories/$', tag_category_edit, name='tag_category_edit'),
    url(r'^transactions_by_category/(?P<pk>)$', transactions_by_category, name='transactions_by_category'),
    url(r'^transactions_by_category/(?P<pk>[0-9]+)/$', transactions_by_category, name='transactions_by_category'),
# SUPPR XLH    url(r'^admin/dashboard/', controlcenter.urls),
    url(r'list_of_banks_available/$', gest_list_of_banks_available, name='gest_list_of_banks_available'),
]

