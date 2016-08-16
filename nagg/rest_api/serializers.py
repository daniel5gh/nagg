# coding=utf-8
import logging

from rest_framework import serializers

from ..models import NewsItem, NewsItemCollection

__author__ = 'Daniël'
_log = logging.getLogger(__name__)


class NewsItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NewsItem
        fields = ('id', 'url', 'source', 'text', 'publish_date', 'retrieval_date')


# noinspection PyAbstractClass
class NewsItemSourceFacetSerializer(serializers.Serializer):
    source = serializers.CharField(read_only=True)
    source__count = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('source', 'source__count')


# Serializers define the API representation.
class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    doc_count = serializers.IntegerField()

    class Meta:
        model = NewsItemCollection
        fields = ('name', 'metadata', 'doc_count')
