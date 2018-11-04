from django.conf.urls import url

from .views import *


# TODO: to adapt to Django 2.0

urlpatterns = [
    url(r'update_list_of_managed_banks/$', update_list_of_managed_banks, name='update_list_of_managed_banks'),
    url(r'list_of_modules_in_database/$', load_list_of_modules_in_database, name='load_list_of_modules_in_database'),
]

