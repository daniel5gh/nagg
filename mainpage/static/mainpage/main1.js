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
            "page/:page(/:page_size)": "page",  // #page/12/10
            "*actions": "defaultRoute",  // matches http://example.com/#anything-here
        },
    });
    window.app = new MainPageRouter();

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


    window.app.on('route:defaultRoute', function (actions) {
        console.log('default route actions: ' + actions);
        newsItemCollection.fetch();
    });
    window.app.on('route:page', function (page, pageSize) {
        console.log('page: ', arguments);
        newsItemCollection.queryParamsModel.goPage(page, pageSize);
    });

    sourceFacetCollection.fetch();
    BackBone.history.start();

    //handy access during development
    window.nic = newsItemCollection;
    window.tv = tv;
    window.fc = sourceFacetCollection;
});