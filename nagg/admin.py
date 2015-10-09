# coding=utf-8
from django.contrib import admin
from django.utils.html import format_html_join, format_html

from .models import NewsItem


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    readonly_fields = ('formatted_text',)
    list_display = ('publish_date', 'get_title', 'source')
    list_display_links = ('get_title',)
    list_filter = ('source',)
    date_hierarchy = 'publish_date'

    fieldsets = (
        (None, {
            'fields': ('formatted_text',)
        }),
        ('Edible Hmmmm', {
            'classes': ('collapse',),
            'fields': ('source', 'url', 'text',
                       'publish_date', 'retrieval_date')
        }),
    )

    @staticmethod
    def formatted_text(instance):
        lines = instance.text.split('\n')
        if len(lines) > 1:
            title = lines[0]
            rest = lines[1:]
        else:
            title = ''
            rest = lines

        title = format_html('<h1>{}</h1>', title)
        g = ((_,) for _ in rest if _)
        return title + format_html_join(
            sep='\n',
            format_string='<p>{}</p>',
            args_generator=g
        )
