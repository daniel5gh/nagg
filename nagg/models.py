# coding=utf-8
from django.db import models
from django_pgjson.fields import JsonBField
from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField


class NewsItem(models.Model):
    """A NewsItem represents an article fetched from the internets."""

    #: From where the article has been fetched.
    source = models.TextField()
    url = models.URLField()
    text = models.TextField()
    publish_date = models.DateTimeField()
    retrieval_date = models.DateTimeField()

    search_index = VectorField()

    objects = SearchManager(
        fields=('text',),
        # config = 'pg_catalog.english',  # this is default
        config = 'pg_catalog.simple',  # this is default
        search_field = 'search_index',  # this is default
        auto_update_search_field = True
    )

    def get_title(self):
        parts = self.text.split('\n')
        if parts:
            return parts[0]
        else:
            ''

    def __str__(self):
        return self.get_title()


class NewsItemCollection(models.Model):
    """A collection of news items.

    This models has a m2m relation with NewsItem.  Collections of
    NewsItems are used in various analysis operations. Typically
    an analysis is done on a subset, a Collection represents
    such a subset.
    """

    name = models.TextField()
    items = models.ManyToManyField(NewsItem, through='NewsItemCollectionMembership')
    metadata = JsonBField(default=dict)


class NewsItemCollectionMembership(models.Model):
    newsitem = models.ForeignKey(NewsItem)
    newsitemcollection = models.ForeignKey(NewsItemCollection)
    data = JsonBField(default=dict)

