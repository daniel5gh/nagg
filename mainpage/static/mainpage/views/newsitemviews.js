define([
    'jquery',
    'underscore',
    'backbone',
    'mainpage/views/listviews'
], function ($, _, Backbone, ListViews) {
    var NewsItemRow = ListViews.ListItem.extend({
        template: _.template($('#newsitem-row-template').html()),
    });


    var NewsItemsTable = ListViews.ListView.extend({
        itemView: NewsItemRow,
    });

    return {
        NewsItemRow: NewsItemRow,
        NewsItemsTable: NewsItemsTable,
    }
});
