define([
    'jquery',
    'd3',
    'mainpage/views/newsitemviews',
    'mainpage/collections/newsitems',
    'mainpage/models/newsitem'
], function ($, d3, NewsItemViews, NewsItems, NewsItem) {
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

    var newsItemCollection = new NewsItems();
    var tv = new NewsItemViews.NewsItemsTable({
        el: '#main-table>tbody',
        collection: newsItemCollection,
    });
    newsItemCollection.fetch();

    window.nic = newsItemCollection;
    window.tv = tv;
});