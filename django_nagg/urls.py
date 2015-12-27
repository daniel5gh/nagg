# coding=utf-8
"""django_nagg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.db.models import Count
from rest_framework import routers, serializers, viewsets

from nagg.models import NewsItem


# Serializers define the API representation.
class NewsItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NewsItem
        fields = ('id', 'url', 'source', 'text', 'publish_date', 'retrieval_date')


# ViewSets define the view behavior.
class NewsItemViewSet(viewsets.ModelViewSet):
    queryset = NewsItem.objects.all().order_by('-publish_date')
    serializer_class = NewsItemSerializer


# noinspection PyAbstractClass
class NewsItemSourceFacetSerializer(serializers.Serializer):
    source = serializers.CharField(read_only=True)
    source__count = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('source', 'source__count')


class NewsItemSourceFacet(viewsets.ModelViewSet):
    queryset = NewsItem.objects.values('source').annotate(Count('source')).order_by('-source__count')
    serializer_class = NewsItemSourceFacetSerializer
    pagination_class = None

# date facets
# select date(publish_date), count(publish_date)
# from nagg_newsitem
# GROUP BY date(publish_date)
# ORDER BY count(publish_date) DESC
# ;

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'newsitems', NewsItemViewSet)
router.register(r'facet/newsitems/source', NewsItemSourceFacet)

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include('mainpage.urls')),
]
