define([
    'jquery',
    'underscore',
    'backbone',
    'mainpage/models/newsitem',
    'mainpage/collections/listviewcollection',
], function($, _, Backbone, NewsItem, ListViewCollection) {
    return ListViewCollection.extend({
        model: NewsItem,
        url: 'api/v1/newsitems/',
    });
});