from django.contrib import admin

from import_export.admin import (
    ExportActionModelAdmin,
    ImportExportModelAdmin,
    ImportMixin,
)
from import_export.fields import Field, ForeignKeyField
from import_export.resources import ModelResource, RelatedObjectResource

from .forms import CustomConfirmImportForm, CustomExportForm, CustomImportForm
from .models import Author, Book, Category, Child, EBook, LegacyBook


class ChildAdmin(ImportMixin, admin.ModelAdmin):
    pass


class BookResource(ModelResource):

    class Meta:
        model = Book

    def for_delete(self, row, instance):
        return self.fields['name'].clean(row) == ''


class BookNameResource(ModelResource):

    class Meta:
        model = Book
        fields = ['id', 'name']
        name = "Export/Import only book names"


class BookAuthorResource(RelatedObjectResource):
    book_name = Field(attribute='name')
    author_name = ForeignKeyField(attribute='author__name', saves_null_values=False)
    author_birthday = ForeignKeyField(attribute='author__birthday', saves_null_values=False)

    class Meta:
        model = Book
        fields = ['id', 'book_name', 'author_email', 'author_name', 'author_birthday']
        name = "Import book and author"


class BookAdmin(ImportExportModelAdmin):
    list_display = ('name', 'author', 'added')
    list_filter = ['categories', 'author']
    resource_classes = [BookResource, BookNameResource, BookAuthorResource]
    change_list_template = "core/admin/change_list.html"


class CategoryAdmin(ExportActionModelAdmin):
    pass


class AuthorAdmin(ImportMixin, admin.ModelAdmin):
    pass


class CustomBookAdmin(BookAdmin):
    """BookAdmin with custom import forms"""
    import_form_class = CustomImportForm
    confirm_form_class = CustomConfirmImportForm
    export_form_class = CustomExportForm

    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)
        # Pass on the `author` value from the import form to
        # the confirm form (if provided)
        if import_form:
            initial['author'] = import_form.cleaned_data['author'].id
        return initial

    def get_import_resource_kwargs(self, request, *args, **kwargs):
        # update resource kwargs so that the Resource is passed the authenticated user
        # This is included as an example of how dynamic values can be passed to resources
        kwargs = super().get_resource_kwargs(request, *args, **kwargs)
        kwargs.update({"user": request.user})
        return kwargs


class LegacyBookAdmin(BookAdmin):
    """
    BookAdmin with deprecated function overrides.
    This class exists solely to test import works correctly using the deprecated
    functions.
    This class can be removed when the deprecated code is removed.
    """

    def get_import_form(self):
        return super().get_import_form()

    def get_confirm_import_form(self):
        return super().get_confirm_import_form()

    def get_form_kwargs(self, form, *args, **kwargs):
        return super().get_form_kwargs(form, *args, **kwargs)

    def get_export_form(self):
        return super().get_export_form()


admin.site.register(Book, BookAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(EBook, CustomBookAdmin)
admin.site.register(LegacyBook, LegacyBookAdmin)
