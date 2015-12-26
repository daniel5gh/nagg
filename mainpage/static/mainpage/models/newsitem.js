define([
    'jquery',
    'underscore',
    'backbone',
], function($, _, Backbone) {
    return Backbone.Model.extend({
        urlRoot: 'api/v1/newsitems/',
        defaults: {
            source: '',
            url: '',
            text: '',
            publish_date: '',
            retrieval_date: '',
            _expanded: false,
        }
    });
});