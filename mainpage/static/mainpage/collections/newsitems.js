define([
    'jquery',
    'underscore',
    'backbone',
    'mainpage/models/newsitem'
], function($, _, Backbone, NewsItem) {
    return Backbone.Collection.extend({
        model: NewsItem,
        url: 'api/v1/newsitems/',
        // Django Rest Framework API returns items under "results".
        parse: function(response) {
            return response.results;
        },
    });
});