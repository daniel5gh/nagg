# coding=utf-8
from django.db import models


class NewsItem(models.Model):
    """A NewsItem represents an article fetched from the internets."""

    #: From where the article has been fetched.
    source = models.TextField()
    url = models.URLField()
    text = models.TextField()
    publish_date = models.DateTimeField()
    retrieval_date = models.DateTimeField()

    def get_title(self):
        parts = self.text.split('\n')
        if parts:
            return parts[0]
        else:
            ''

    def __str__(self):
        return self.get_title()


