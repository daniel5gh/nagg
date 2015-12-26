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
            this.totalRecords = response.count;
            this.urlNext = response.next;
            this.urlPrevious = response.previous;
            return response.results;
        },
    });
});