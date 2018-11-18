from django.shortcuts import render

# Create your views here.

# from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required

# from .models import Category
from gesfipe.banksandaccounts.models import *
from .models import *
from .forms import TagForm, CategoryForm


# Create your views here.


def category_list(request):
    categories = Category.objects.all()
    jsondata = serializers.serialize('json', categories)
    context = {'categories': categories, 'jsondata': jsondata}
    return render(request, 'Categories/categories_list.html', context)


def category_json(request):
    categories = Category.objects.all()
    return HttpResponse(serializers.serialize('json', categories), content_type="application/json")


LIST_HEADERS_SEARCH_TAGS = (
    ('Name', 'tag'),
    ('New Tag', 'is_new_tag'),
    ('Used as Tag', 'will_be_used_as_tag'),
    ('Category', 'category'),
)


@login_required
def search_tags(request):
    '''
    Gives the list of tags in transaction key_words not associated with a category (tag.is_new_tag = True)
    :param request:
    :return: render
    '''

    sort_headers = SortHeaders(request, LIST_HEADERS_SEARCH_TAGS)
    transaction_list = Transactions.objects.all()
    list_of_tags = Tag.objects.all()

    listoftags = list()
    listoftags_found = list()

    if list_of_tags:
        for t in list_of_tags:
            t.tag.upper()  # In case we forgot to upperize at the very first time
            # t.is_new_tag = False   #Complicated to manage when updating/changing page
            # TODO: to automize new/old Tag without searching each time "new Tags"
            t.save()
            listoftags.append(t.tag)

    for transaction in transaction_list:
        if not transaction.key_words:  # if key_words is empty, we create key_words
            transaction.create_key_words()
            transaction.save()

        for key_tag in transaction.key_words:
            if key_tag not in listoftags_found:
                key_tag.strip(',') # To verify if it's needed to strip ',' (?)
                listoftags_found.append(key_tag)

    # To get a list unique
    # listoftags_found = set(listoftags_found)

    # Back to a list
    # listoftags_found = list(listoftags_found)

    for tag_found in listoftags_found:
        if tag_found not in listoftags:
            tag = Tag()
            tag.tag = tag_found
            tag.is_new_tag = True
            tag.will_be_used_as_tag = True
            listoftags.append(tag_found)
            tag.save()
            # listoftags.sort()

    listtagnew = Tag.objects.order_by(sort_headers.get_order_by()).filter(is_new_tag=True)
    #    listtagnew = Tag.objects.order_by(sort_headers.get_order_by())

    list_of_headers = list(sort_headers.headers())

    context = {
        "listtagnew": listtagnew,
        'headers': list_of_headers,
    }

    return render(request, 'Categories/search_tags.html', context)


LIST_HEADERS_EDIT_TAG = (
    ('Date', 'date_of_transaction'),
    ('Type', 'type_of_transaction'),
    ('Name', 'name_of_transaction'),
    ('Amount', 'amount_of_transaction'),
)


@login_required
def tag_edit(request, pk):
    sort_headers = SortHeaders(request, LIST_HEADERS_EDIT_TAG)
    tags_list = Tag.objects.filter(will_be_used_as_tag=True)

    if pk == '':
        transactions = Transactions.objects.order_by(sort_headers.get_order_by())
        tag = None
    else:
        tag = get_object_or_404(Tag, pk=pk)
        transactions = Transactions.objects.order_by(sort_headers.get_order_by()).filter(
            name_of_transaction__icontains=tag.tag)

    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)

        if form.is_valid():
            tag = form.save(commit=False)
            tag.is_new_tag = False
            tag.will_be_used_as_tag = True
            tag.save()
            return redirect('tag_edit', pk=tag.pk)
    else:
        form = TagForm(instance=tag)

    list_of_headers = list(sort_headers.headers())

    context = {
        'transactions': transactions,
        'tags_list': tags_list,
        'tag': tag,
        'form': form,
        'headers': list_of_headers,
    }
    return render(request, 'Categories/tag_edit.html', context)


@login_required
def show_category(request, node=None):
    cats = Category.objects.all()
    node = node.split('/')
    # print("NNNNNNNNNN OOOOOOOOO DDDDDDDDDDD EEEEEEEEEEEE: {}".format(node))
    if node[-1] == 'None':
        current = Category.objects.filter(parent=None)
        # print("Current: {} \n".format(current))
        ancestors = Category.objects.filter(parent=None)
        # ancestors = None
        # print("Ancestors: {} \n".format(current))

        # children = Category.objects.filter(parent=ancestors[0])
        children = Category.objects.filter(parent=None)
        # children = Category.objects.filter(parent=ancestors)

        # print("Children: {} \n".format(current))

    else:
        current = Category.objects.filter(name=node[-1])
        children = Category.objects.filter(parent__name=node[-1])
        ancestors = current.get_ancestors()

        if not ancestors:
            ancestors = current
        else:
            ancestors = current.get_ancestors(include_self=True)

    return render(request, 'Categories/categories.html',
                  {'cats': cats,
                   'ancestors': ancestors,
                   'children': children,
                   'current': current,
                   })


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(data=request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            # category.owner = request.user
            category.save()
            # form.save_m2m()
            return redirect('categories:show_category')
    else:
        form = CategoryForm()
    context = {'form': form, 'create': True}
    return render(request, 'Categories/category_edit.html', context)


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    cats = Category.objects.all()
    # if bookmark.owner != request.user and not request.user.is_superuser:
    #     raise PermissionDenied
    if request.method == 'POST':
        form = CategoryForm(instance=category, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories:show_category', node=category.parent.name)
            # return redirect('budget')
    else:
        form = CategoryForm(instance=category)
    context = {'cats': cats, 'form': form, 'create': False}
    return render(request, 'Categories/category_edit.html', context)
