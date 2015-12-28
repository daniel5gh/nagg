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
            this.updatePagingState(response);
            return response.results;
        },
        updatePagingState: function (response) {
            this.totalRecords = response.count;
            this.urlNext = response.next;
            this.urlPrevious = response.previous;
        },
        queryParams: {
            page: 1,
            page_size: 10,
        },
        fetch: function(options) {
            var self = this;
            options || (options = {});
            options.data || (options.data = {});
            options.error = function () {
                self.updatePagingState({
                    count: 0,
                });
                self.reset();
            };
            $.extend(options.data, this.queryParams);
            return this.constructor.__super__.fetch.apply(this, [options]);
        },
    });
});