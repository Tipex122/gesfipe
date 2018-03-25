from django import forms
from mptt.forms import TreeNodeChoiceField

from .models import Tag
from categories.models import Category


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('tag', 'is_new_tag', 'will_be_used_as_tag', 'category',)

    # widgets = {
    #            'category':TreeNodeChoiceField(queryset=Category.objects.all()),
    #        }

    category = TreeNodeChoiceField(queryset=Category.objects.all(), level_indicator=u'+-')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = {'name', 'description', 'amount'}
