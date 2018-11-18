from django.conf.urls import url

from .views import *

# TODO: Mettre à jour en fonction de Django 2.0

app_name = 'categories'

urlpatterns = [
    #    url(r'^$', 'categories.views.category_list', name='category_list'),
    url(r'^category/(?P<node>.+)/$', show_category, name='show_category'),
    # url(r'^category/(?P<hierarchy>.+)/$', show_category, name='show_category'),

    #    url(r'^category/(?P<hierarchy>)/$', show_category, name='category'),

    url(r'^budget/$', category_list, name='budget'),
    url(r'^test/$', category_json, name='categories_json'),

    url(r'^tags/search_tags/$', search_tags, name='search_tags'),

    url(r'^tag_edit/(?P<pk>)$', tag_edit, name='tag_edit'),
    url(r'^tag_edit/(?P<pk>[0-9]+)/$', tag_edit, name='tag_edit'),

    url(r'^category_create/$', category_create, name='category_create'),
    # url(r'^category_edit/(?P<pk>\d+)/$', category_edit, name='category_edit'),
    url(r'^category_edit/(?P<pk>[0-9]+)/$', category_edit, name='category_edit'),

]

