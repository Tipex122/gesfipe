from django.conf.urls import url

from .views import *


# TODO: to adapt to Django 2.0

urlpatterns = [
    url(r'update_list_of_available_banks/$', update_list_of_available_banks, name='update_list_of_available_banks'),

]

