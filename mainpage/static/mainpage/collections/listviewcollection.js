define([
    'jquery',
    'underscore',
    'backbone',
], function($, _, Backbone) {
    /**
     * Tailored for django rest framework with a FilterBackend that understands 'q'
     * and the StandardResultsSetPagination paginator that uses 'page' and 'page_size'
     */
    var QueryParamModel = Backbone.Model.extend({
        defaults: {
            page: 1,
            page_size: 10,
            _total: 0,
            _max_page: 1,
        },
        set: function (key, value, options) {
            if (key === '_total') {
                var max = Math.ceil(value / this.get('page_size'));
                this.set('_max_page', max);
            }
            if (key === 'page') {
                window.app.navigate('page/' + value + '/' + this.get('page_size'));
                value = Math.max(1, value);
            }
            Backbone.Model.prototype.set.apply(this, [key, value, options]);
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
                } else if (key === 'q' && params[key] === '') {
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
        goPage: function(page, pageSize) {
            if (pageSize) {
                this.set('page_size', pageSize, {silent: true});
            }
            this.set('page', page);
        }
    });

    /**
     * Generic collection that can work with Django Rest Framework
     */
    return Backbone.Collection.extend({
        initialize: function () {
            var self = this;

            if (!this.model) {
                console.error('ListViewCollection (', self, ') Please add model to this collection.');
            }
            if (!this.url) {
                console.error('ListViewCollection (', self, ') Please add url to this collection.');
            }

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

            //this.fetch();
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
            options.error = function (c, response) {
                if (/Invalid page/.test(response['responseText'])) {
                    self.queryParamsModel.set('page', 1);
                } else {
                    this.reset();
                }
            };
            $.extend(options.data, this.queryParamsModel.getQueryParams());
            console.log('fetch', this.url, options.data);
            return Backbone.Collection.prototype.fetch.apply(this, [options]);
        },
    });
});