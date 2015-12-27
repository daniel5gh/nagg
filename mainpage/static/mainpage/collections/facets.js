define([
    'jquery',
    'underscore',
    'backbone',
    'mainpage/models/facet'
], function ($, _, Backbone, FacetModels) {
    return {
        SourceFacetCollection: Backbone.Collection.extend({
                model: FacetModels.SourceFacet,
                url: 'api/v1/facet/newsitems/source/',
            }
        )
    }
});