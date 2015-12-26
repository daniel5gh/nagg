define([
    'jquery',
    'underscore',
    'backbone',
], function ($, _, Backbone) {
    return Backbone.Model.extend({
        urlRoot: 'api/v1/newsitems/',
        defaults: {
            source: '',
            url: '',
            text: '',
            publish_date: '',
            retrieval_date: '',
            _expanded: false,
        },
        parse: function (response) {
            response.publish_date = new Date(response.publish_date).toLocaleString();
            response.retrieval_date = new Date(response.retrieval_date).toLocaleString();
            return response;
        }
    });
});