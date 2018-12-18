from django.conf.urls import url

from .views import *


# TODO: to adapt to Django 2.0

app_name = 'manageweboob'

urlpatterns = [
    url(r'update_list_of_managed_banks/$', update_list_of_managed_banks, name='update_list_of_managed_banks'),
    url(r'load_list_of_modules_in_database/$', load_list_of_modules_in_database, name='load_list_of_modules_in_database'),
    url(r'list_of_modules_in_database/$', list_of_modules_in_database, name='list_of_modules_in_database'),
]

