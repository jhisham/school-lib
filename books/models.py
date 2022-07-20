from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models

class Book(models.Model):
    name = models.CharField(_("name"), max_length=255, unique=True)
    qty = models.IntegerField(_("quantity"), default=0)
    

    class Meta:
        verbose_name = _("book")
        verbose_name_plural = _("books")

    def __str__(self):
        return self.name
