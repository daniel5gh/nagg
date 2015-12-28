define([
    'jquery',
    'underscore',
    'backbone',
    'mainpage/models/newsitem'
], function($, _, Backbone, NewsItem) {
    return Backbone.Collection.extend({
        model: NewsItem,
        url: 'api/v1/newsitems/',
        initialize: function () {
            var self = this;
            this.queryParamsModel = new Backbone.Model({
                page: 1,
                page_size: 10,
            });
            this.queryParamsModel.on('change:page', function() {
                self.fetch();
            }, this);
            this.queryParamsModel.on('change:q', function() {
                self.fetch();
            }, this);
            this.fetch();
        },
        // Django Rest Framework API returns items under "results".
        parse: function(response) {
            this.updatePagingState(response);
            return response.results;
        },
        updatePagingState: function (response) {
            this.queryParamsModel.set('_total', +response.count);
            this.queryParamsModel.set('_url_next', response.next);
            this.queryParamsModel.set('_url_previous', response.previous);
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
            var params = this.queryParamsModel.toJSON();
            $.each(params, function (key) {
                if (key[0] === '_') {
                    delete params[key];
                }
            });
            $.extend(options.data, params);
            return this.constructor.__super__.fetch.apply(this, [options]);
        },
    });
});