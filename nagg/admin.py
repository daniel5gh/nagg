# coding=utf-8
from django.contrib import admin
from .models import NewsItem


class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('publish_date', 'get_title', 'source')
    list_display_links = ('get_title',)
    list_filter = ('source',)

admin.site.register(NewsItem, NewsItemAdmin)
