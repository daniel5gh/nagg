define([
    'jquery',
    'd3',
    'backbone',
    'mainpage/views/newsitemviews',
    'mainpage/collections/newsitems',
    'mainpage/views/facetviews',
    'mainpage/collections/facets',
], function ($, d3, BackBone, NewsItemViews, NewsItems, FacetViews, Facets) {
    var MainPageRouter = Backbone.Router.extend({
        routes: {
            "page/:page": "page",  // #page/12
            "*actions": "defaultRoute",  // matches http://example.com/#anything-here
        },
    });

    var sourceFacetCollection = new Facets.SourceFacetCollection();
    var sourceFacetView = new FacetViews.SourceFacetView({
        el: '#facets',
        collection: sourceFacetCollection,
    });

    var newsItemCollection = new NewsItems();
    var tv = new NewsItemViews.NewsItemsTable({
        el: '#main-table',
        collection: newsItemCollection,
    });

    var mpr = new MainPageRouter();

    mpr.on('route:defaultRoute', function (actions) {
        console.log('default route actions: ' + actions);
        newsItemCollection.queryParams.page = 1;
        newsItemCollection.fetch();
    });

    mpr.on('route:page', function (pageNr) {
        newsItemCollection.queryParams.page = pageNr;
        newsItemCollection.fetch();
    });

    sourceFacetCollection.fetch();
    BackBone.history.start();

    //handy access during development
    window.nic = newsItemCollection;
    window.tv = tv;
    window.fc = sourceFacetCollection;
});