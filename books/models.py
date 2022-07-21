from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db import models


class Book(models.Model):
    """
    Model that holds information about every book in the library.
    """
    
    name = models.CharField(_("name"), max_length=255, unique=True)
    qty = models.IntegerField(_("quantity"), default=0)
    available_qty = models.IntegerField(_("available quantity"), default=0)

    class Meta:
        verbose_name = _("book")
        verbose_name_plural = _("books")

    def __str__(self):
        return self.name


class BorrowedBook(models.Model):
    """
    Relationship of books that are borrowed students.
    """
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("student"), on_delete=models.CASCADE)
    book = models.ForeignKey(Book, verbose_name=_("book"), on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(_("book checkout date"), auto_now=False, auto_now_add=False)
    due_date = models.DateTimeField(_("due date"), auto_now=False, auto_now_add=False)
    return_date = models.DateTimeField(_("book return date"), auto_now=False, auto_now_add=False, blank=True, null=True)
    is_renewed = models.BooleanField(_("is renewed"), default=False)
    
    class Meta:
        verbose_name = _("borrowed books")
        verbose_name_plural = _("borrowed books")

    def __str__(self):
        return self.name
