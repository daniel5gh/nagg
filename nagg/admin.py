# coding=utf-8
from django.contrib import admin
from .models import NewsItem


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('publish_date', 'get_title', 'source')
    list_display_links = ('get_title',)
    list_filter = ('source',)
    date_hierarchy = 'publish_date'

