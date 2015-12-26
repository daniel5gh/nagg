define([
    'jquery',
    'd3',
    'backbone',
    'mainpage/views/newsitemviews',
    'mainpage/collections/newsitems',
], function ($, d3, BackBone, NewsItemViews, NewsItems) {
    var d3Bar = function () {
        var w = 500;
        var h = 100;
        var barPadding = 1;
        var svg = d3.select("body")
            .append("svg")
            .attr("width", w)
            .attr("height", h);

        var dataset2 = [5, 10, 13, 19, 21, 25, 22, 18, 15, 13,
            11, 12, 15, 20, 18, 17, 16, 18, 23, 25];

        var bars = svg.append('g').selectAll("rect")
            .data(dataset2);

        bars.exit().remove();

        bars.enter()
            .append("rect")
            .attr("width", w / dataset2.length - barPadding)
            .attr('height', 0)
            .attr('y', h)
            .attr("x", function (d, i) {
                return i * (w / dataset2.length);
            })
            .transition().duration(1000)
            .attr("height", function (d) {
                return d;  //Just the data value
            })
            .attr("y", function (d) {
                return h - d;  //Height minus data value
            });
    };

    var MainPageRouter = Backbone.Router.extend({
        routes: {
            "page/:page": "page",  // #page/12
            "*actions": "defaultRoute",  // matches http://example.com/#anything-here
        },
    });

    var newsItemCollection = new NewsItems();
    var tv = new NewsItemViews.NewsItemsTable({
        el: '#main-table',
        collection: newsItemCollection,
    });

    var mpr = new MainPageRouter();

    mpr.on('route:defaultRoute', function (actions) {
        console.log('default route actions: ' + actions);
        newsItemCollection.fetch();
    });

    mpr.on('route:page', function (pageNr) {
        newsItemCollection.fetch({
            data: {page: pageNr}
        });
    });

    BackBone.history.start();

    //handy access during development
    window.nic = newsItemCollection;
    window.tv = tv;
});