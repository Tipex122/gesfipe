from django.contrib import admin

# Register your models here.

from .models import WeboobModules

class WeboobModulesAdmin(admin.ModelAdmin):
    list_display = ('name_of_module', 'description_of_module')


admin.site.register(WeboobModules,)
