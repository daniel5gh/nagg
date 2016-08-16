# coding=utf-8
import logging

from django.db.models import Count
from rest_framework.filters import BaseFilterBackend
from rest_framework import viewsets, filters

from ..models import NewsItem, NewsItemCollection
from .serializers import (
    NewsItemSerializer, CollectionSerializer,
    NewsItemSourceFacetSerializer)

__author__ = 'Daniël'
_log = logging.getLogger(__name__)

"""TODO
Probably want per year, y/m and y/m/d
date facets::

    select date(publish_date), count(publish_date)
    from nagg_newsitem
    GROUP BY date(publish_date)
    ORDER BY count(publish_date) DESC
;
"""


class SearchFilter(BaseFilterBackend):
    """pg full text search"""

    def filter_queryset(self, request, queryset, view):
        search_string = request.query_params.get('q', '')
        qs = queryset.search(search_string)
        return qs


# ViewSets define the view behavior.
class NewsItemViewSet(viewsets.ModelViewSet):
    queryset = NewsItem.objects.all().order_by('-publish_date')
    serializer_class = NewsItemSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       SearchFilter)
    filter_fields = ('source', 'url', 'publish_date', 'id')


class NewsItemSourceFacet(viewsets.ModelViewSet):
    queryset = \
        (NewsItem.objects
         .values('source')
         .annotate(Count('source'))
         .order_by('-source__count')
         )
    serializer_class = NewsItemSourceFacetSerializer
    pagination_class = None


# ViewSets define the view behavior.
class CollectionViewSet(viewsets.ModelViewSet):
    queryset = \
        (NewsItemCollection.objects
         .all()
         .order_by('id')
         .annotate(doc_count=Count('items'))
         )
    serializer_class = CollectionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'metadata', 'id',)
