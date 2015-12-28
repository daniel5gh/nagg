define([
    'jquery',
    'underscore',
    'backbone',
    'mainpage/models/newsitem'
], function($, _, Backbone, NewsItem) {
    var QueryParamModel = Backbone.Model.extend({
        defaults: {
            page: 1,
            page_size: 10,
            _total: 0,
            _max_page: 1,
        },
        set: function (key, value) {
            if (key === '_total') {
                this.set('_max_page', Math.ceil(value / this.get('page_size')));
            }
            Backbone.Model.prototype.set.apply(this, [key, value]);
            return this;
        },
        getNextPageNr: function () {
            return Math.min(this.get('page') + 1, this.get('_max_page'));
        },
        goNextPage: function () {
            this.set('page', this.getNextPageNr());
            return this;
        },
        getPrevPageNr: function () {
            return Math.max(this.get('page') - 1, 1);
        },
        goPrevPage: function () {
            this.set('page', this.getPrevPageNr());
            return this;
        },
    });
    return Backbone.Collection.extend({
        model: NewsItem,
        url: 'api/v1/newsitems/',
        initialize: function () {
            var self = this;
            this.queryParamsModel = new QueryParamModel();
            this.queryParamsModel.on('change:page', function() {
                self.fetch();
            }, this);
            this.queryParamsModel.on('change:q', function() {
                self.fetch();
            }, this);
            this.fetch();
            return this;
        },
        // Django Rest Framework API returns items under "results".
        parse: function(response) {
            this.queryParamsModel.set('_total', +response.count);
            return response.results;
        },
        updatePagingState: function (response) {
        },
        fetch: function(options) {
            var self = this;
            options || (options = {});
            options.data || (options.data = {});
            options.error = function () {
                self.queryParamsModel.set('_total', 0);
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