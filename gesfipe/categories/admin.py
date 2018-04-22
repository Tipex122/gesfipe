from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Tag


# Register your models here.

class TagAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['tag', ]}),
        ('Info Genre',
         {'fields': ['category', 'will_be_used_as_tag', 'is_new_tag', ]}),
    ]
    list_display = ('tag', 'is_new_tag', 'will_be_used_as_tag', 'category')
    # search_fields = ['tag', 'category',]
    search_fields = ['tag',]
    list_filter = ('category', 'will_be_used_as_tag', 'is_new_tag',)


admin.site.register(Tag, TagAdmin)


# admin.site.register(Tag)


# class CategoryAdmin(DjangoMpttAdmin ):
class CategoryAdmin(DraggableMPTTAdmin):
    #    fields = ['name', 'description', 'amount', 'parent']
    '''
    fieldsets = [
        (None, {'fields': ['indented_title']}),
        ('Info Catégorie', {'fields': ['parent', 'description', 'amount']}),
    #   ('Tags associés', {'fields': ['tag',]})
    ]
    '''
    list_display = ('tree_actions', 'indented_title', 'amount',)
    list_display_links = ('indented_title',)
    search_fields = ['name', 'amount', ]
    # list_filter = ('parent',)


# mptt_level_indent = 20

# admin.site.register(Category, CategoryAdmin)
admin.site.register(Category, CategoryAdmin)
