from django.contrib import admin

from ..models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority',)
    search_fields = ('name',)
    ordering = ('priority',)

    fieldsets = (
        (None, {
            'fields': ('name', 'priority',)
        }),
        # TODO - Use a better way to show the adapter code (CodeMirror or django-markdownx)
        ('Adapter Code', {
            'fields': ('adapter_code',),
            'classes': ('show',),
        }),
    )
