define([
    'jquery',
    'underscore',
    'backbone',
], function ($, _, Backbone) {
    return {
        SourceFacet: Backbone.Model.extend({
            defaults: {
                source: '',
                source__count: 0,
            },
        })
    }
});