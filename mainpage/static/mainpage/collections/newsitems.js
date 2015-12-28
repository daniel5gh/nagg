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
            if (key === 'page') {
                value = Math.max(1, value);
            }
            Backbone.Model.prototype.set.apply(this, [key, value]);
            return this;
        },
        /**
         * All attr not starting with _ are query params
         * @returns {*}
         */
        getQueryParams: function () {
            var params = this.toJSON();
            return $.each(params, function (key) {
                if (key[0] === '_') {
                    delete params[key];
                }
            });
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
            });
            this.queryParamsModel.on('change:q', function() {
                self.fetch();
            });
            this.on('reset', function () {
                self.queryParamsModel.set('_total', 0);
            });

            this.fetch();
            return this;
        },
        // Django Rest Framework API returns items under "results".
        parse: function(response) {
            this.queryParamsModel.set('_total', +response.count);
            return response.results;
        },
        fetch: function(options) {
            var self = this;
            options || (options = {});
            options.data || (options.data = {});
            options.error = function () {
                self.reset();
            };
            $.extend(options.data, this.queryParamsModel.getQueryParams());
            return this.constructor.__super__.fetch.apply(this, [options]);
        },
    });
});