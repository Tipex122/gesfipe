from django.db import models

# Create your models here.
from django.db import models
from decimal import Decimal
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext_lazy as _

from django.contrib.postgres.fields import ArrayField

# Create your models here.


ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'


class SortHeaders:
    """
    Handles generation of an argument for the Django ORM's
    ``order_by`` method and generation of table headers which reflect
    the currently selected sort, based on defined table headers with
    matching sort criteria.

    Based in part on the Django Admin application's ``ChangeList``
    functionality.
    """

    def __init__(self, request, headers, default_order_field=None,
                 default_order_type='asc', additional_params=None):
        """
        request
            The request currently being processed - the current sort
            order field and type are determined based on GET
            parameters.

        headers
            A list of two-tuples of header text and matching ordering
            criteria for use with the Django ORM's ``order_by``
            method. A criterion of ``None`` indicates that a header
            is not sortable.

        default_order_field
            The index of the header definition to be used for default
            ordering and when an invalid or non-sortable header is
            specified in GET parameters. If not specified, the index
            of the first sortable header will be used.

        default_order_type
            The default type of ordering used - must be one of
            ``'asc`` or ``'desc'``.

        additional_params:
            Query parameters which should always appear in sort links,
            specified as a dictionary mapping parameter names to
            values. For example, this might contain the current page
            number if you're sorting a paginated list of items.
        """
        if default_order_field is None:
            for i, (header, query_lookup) in enumerate(headers):
                if query_lookup is not None:
                    default_order_field = i
                    break
        if default_order_field is None:
            raise AttributeError('No default_order_field was specified \
            and none of the header definitions given were sortable.')
        if default_order_type not in ('asc', 'desc'):
            raise AttributeError('If given, default_order_type must be one of \'asc\' or \'desc\'.')
        if additional_params is None:
            additional_params = {}

        self.header_defs = headers
        self.additional_params = additional_params
        self.order_field, self.order_type = default_order_field, default_order_type

        # Determine order field and order type for the current request
        params = dict(request.GET.items())
        if ORDER_VAR in params:
            try:
                new_order_field = int(params[ORDER_VAR])
                if headers[new_order_field][1] is not None:
                    self.order_field = new_order_field
            except (IndexError, ValueError):
                pass  # Use the default
        if ORDER_TYPE_VAR in params and params[ORDER_TYPE_VAR] in ('asc', 'desc'):
            self.order_type = params[ORDER_TYPE_VAR]

    def headers(self):
        """
        Generates dicts containing header and sort link details for
        all defined headers.
        """
        for i, (header, order_criterion) in enumerate(self.header_defs):
            th_classes = []
            new_order_type = 'asc'
            if i == self.order_field:
                th_classes.append('sorted %sending' % self.order_type)
                new_order_type = {'asc': 'desc', 'desc': 'asc'}[self.order_type]
            yield {
                'text': header,
                'sortable': order_criterion is not None,
                'url': self.get_query_string({ORDER_VAR: i, ORDER_TYPE_VAR: new_order_type}),
                'class_attr': (th_classes and ' class="%s"' % ' '.join(th_classes) or ''),
            }

    def get_query_string(self, params):
        """
        Creates a query string from the given dictionary of
        parameters, including any additonal parameters which should
        always be present.
        """
        params.update(self.additional_params)
        return '?%s' % '&amp;'.join(['%s=%s' % (param, value) \
                                     for param, value in params.items()])

    def get_order_by(self):
        """
        Creates an ordering criterion based on the current order
        field and order type, for use with the Django ORM's
        ``order_by`` method.
        """
        return '%s%s' % (
            self.order_type == 'desc' and '-' or '',
            self.header_defs[self.order_field][1],
        )


class Category(MPTTModel):
    """
    Handles categories used to classify transactions.
    Categories are stored in a hierarchical structure which can be as deep as needed thanks to MPTT method. (Modified
    Preorder Tree Traversal)
    At this stage, one can manage categories hierarchy only through admin interface
    """
    name = models.CharField(max_length=100, blank=False, unique=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10,
                                 decimal_places=2,
                                 default=Decimal('0.00'),
                                 verbose_name="Estimated budget",
                                 blank=True, null=True)

    parent = TreeForeignKey('self',
                            null=True,
                            blank=True,
                            related_name='children',
                            db_index=True,
                            on_delete=models.CASCADE)
    # slug = models.SlugField()

    # objects = models.Manager()

    # New from Gesfi1
    tags_lists = ArrayField(ArrayField(models.CharField(max_length=200), blank=True), blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        # ordering = ['name']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):  # __unicode__ on Python 2
        return self.name

    def save(self, *args, **kwargs):
        """
        Used to manage total amount (budget) of a category associated with its sub-categories when modified
        param args:
        param kwargs:
        return: Nothing
        """
        level_amount = 0

        super(Category, self).save(*args, **kwargs)  # Call the "real" save() method.

        for sibling in self.get_siblings(True):
            print("\tsibling.name: {0},     sibling.amount: {1}".format(sibling.name, sibling.amount))
            level_amount = level_amount + sibling.amount
        print('level_amount = {0}'.format(level_amount))

        par = self.parent
        print('Parent {}'.format(par))

        if self.parent is not None:
            '''
            super(Category, self).save(*args, **kwargs)  # Call the "real" save() method.

            for sibling in self.get_siblings(True):
                print("\tsibling.name: {0},     sibling.amount: {1}".format(sibling.name, sibling.amount))
                level_amount = level_amount + sibling.amount
            print('level_amount = {0}'.format(level_amount))
            '''
            ancestor = self.parent
            print(ancestor)
            ancestor.amount = level_amount
            ancestor.save()

            # ancestors = self.get_ancestors(True, False)
            # print(ancestors)
            # print(ancestor)
            # ancestor.amount = level_amount
            # ancestor.save()

        # else:

    def create_tags(self, tags):
        # TODO: what for ? ==> to be explained
        """
        :param tags:
        :return:
        """
        tags = tags.strip()
        tag_list = tags.split(' ')
        for tag in tag_list:
            if tag:
                t, created = Tag.objects.get_or_create(tag=tag.lower(),
                                                       category=self)

    def get_tags(self):
        return Tag.objects.filter(category=self)

    # TODO: not sure it works or it's necessary
    def get_ancestors(self, ascending=False, include_self=False):
        return super(Category, self).get_ancestors(ascending=False, include_self=True)


class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    is_new_tag = models.BooleanField(default=True)
    will_be_used_as_tag = models.BooleanField(default=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        # unique_together = (('tag', 'category'),)
        # index_together = [['tag', 'category'], ]

    def __str__(self):
        return self.tag

    # Not tested !!!!
    @staticmethod
    def get_popular_tags():
        tags = Tag.objects.all()
        count = {}
        for tag in tags:
            # if tag.categry.status == Article.PUBLISHED:
            if tag.tag in count:
                count[tag.tag] = count[tag.tag] + 1
            else:
                count[tag.tag] = 1
        sorted_count = sorted(count.items(), key=lambda t: t[1], reverse=True)
        return sorted_count[:20]
