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
        queryParams: {
            page: 1,
        },
        fetch: function(options) {
            options || (options = {});
            options.data || (options.data = {});
            $.extend(options.data, this.queryParams);
            console.log('fetch', options);
            return this.constructor.__super__.fetch.apply(this, [options]);
        },
    });
});