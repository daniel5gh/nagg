# coding=utf-8
from django.db import models


class NewsItem(models.Model):
    source = models.TextField()
    url = models.URLField()
    text = models.TextField()
    publish_date = models.DateTimeField()
    retrieval_date = models.DateTimeField()

    def get_title(self):
        return self.text.split('\n')[0]

    def __str__(self):
        return self.get_title()


