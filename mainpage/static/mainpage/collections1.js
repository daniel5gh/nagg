define([
    'jquery',
    'd3',
    'backbone',
    'mainpage/views/listviews',
    'mainpage/collections/listviewcollection',
], function ($, d3, BackBone, ListViews, ListViewCollection) {
    var MainPageRouter = Backbone.Router.extend({
        routes: {
            "page/:page(/:page_size)": "page",  // #page/12/10
            "*actions": "defaultRoute",  // matches http://example.com/#anything-here
        },
    });
    window.app = new MainPageRouter();

    // warning collection not to be confused with backbone collection
    // this is a collection of docs
    var CollectionModel = Backbone.Model.extend({
        urlRoot: 'api/v1/collections/',
        defaults: {
            name: '',
            metadata: '',
            doc_count: '',
            _expanded: false,
        },
        //parse: function (response) {
        //    return response;
        //}
    });

    var CollectionsBBCollection = ListViewCollection.extend({
        model: CollectionModel,
        url: 'api/v1/collections/',
    });

    var CollectionsItem = ListViews.ListItem.extend({
        template: _.template($('#collection-row-template').html()),
    });

    var CollectionsView = ListViews.ListView.extend({
        itemView: CollectionsItem,
    });


    var collectionsBBCollection = new CollectionsBBCollection();
    var tv = new CollectionsView({
        el: '#main-table',
        collection: collectionsBBCollection,
    });


    window.app.on('route:defaultRoute', function (actions) {
        console.log('default route actions: ' + actions);
        collectionsBBCollection.fetch();
    });
    window.app.on('route:page', function (page, pageSize) {
        console.log('page: ', arguments);
        collectionsBBCollection.queryParamsModel.goPage(page, pageSize);
    });

    collectionsBBCollection.fetch();
    BackBone.history.start();

    //handy access during development
    window.ic = collectionsBBCollection;
    window.tv = tv;
});