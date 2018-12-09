from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class WeboobModules(models.Model):
    name_of_module = models.CharField(
        'Nom du module',
        default='Nom du module',
        max_length=256)

    description_of_module = models.CharField(
        'Description du module',
        default='Description',
        max_length=256)

    # is_in_database = models.BooleanField(False)
    is_in_database = models.BooleanField(
        False,
        default=False
    )

    def __str__(self):
        return "%s" % self.name_of_module

    class Meta:
        verbose_name = _('weboob module')
        verbose_name_plural = _('weboob modules')
        ordering = ['name_of_module']
