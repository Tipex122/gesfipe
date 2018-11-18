from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
# from django.shortcuts import redirect
from django.views import defaults as default_views

from gesfipe.banksandaccounts.views import banks_and_accounts_list

urlpatterns = [
    # url(r'^$', TemplateView.as_view(template_name='banksandaccounts/banks_and_accounts_list.html'), name='home'),
    # url(r'^$', TemplateView.as_view(template_name='banksandaccounts/banks_and_accounts_list.html'), name='index'),
    url(r'^$', banks_and_accounts_list),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('gesfipe.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),


    # Your stuff: custom urls includes go here
    # url(r'^managegesfi/', include('gesfipe.managegesfi.urls')),
    # url(r'^categories/', include('gesfipe.categories.urls')),
    # url(r'^', include('gesfipe.manageweboob.urls')),
    url(r'^manageweboob/', include('gesfipe.manageweboob.urls')),
    url(r'^managegesfi/', include('gesfipe.managegesfi.urls')),
    url(r'^categories/', include('gesfipe.categories.urls')),
    url(r'^banksandaccounts/', include('gesfipe.banksandaccounts.urls')),


    # path('', include(('gesfipe.banksandaccounts.urls', 'banksandaccounts'), namespace='banksandaccounts')),
    # path('', include('gesfipe.banksandaccounts.urls', namespace='banksandaccounts')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
