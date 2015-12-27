define([
    'jquery',
    'underscore',
    'backbone',
], function ($, _, Backbone) {
    var d3Bar = function (selector, data) {
        var w = selector.width();
        var h = 600;
        var barPadding = 2;
        var barHeight = h / data.length - barPadding;

        var xAxis = d3.scale.linear()
            .range([0, w])
            .domain([0, d3.max(data, function (d) {
                return d.source__count;
            })]);

        var svg = d3.select(selector.selector)
            .append("svg")
            .attr("width", w)
            .attr("height", h);

        var bars = svg.selectAll('g')
            .data(data);

        bars.exit().remove();

        var barsEnter = bars.enter().append("g")
            .attr("transform", function (d, i) {
                return "translate(0," + i * (h / data.length) + ")";
            });


        barsEnter.append("rect")
            .style('fill', 'steelblue')
            .attr("width", 0)
            .attr('height', barHeight)
            .transition().duration(1000)
            .attr("width", function (d) {
                return xAxis(d.source__count);  //Just the data value
            });

        barsEnter.append("text")
            .attr("x", 10)
            .attr("y", barHeight / 2)
            .attr("dy", ".35em")
            .text(function (d) {
                return d.source;
            });

        $(window).resize(function () {
            w = selector.width();
            svg.attr("width", w);
            xAxis.range([0, w]);
            bars.selectAll('rect')
                .transition().duration(1000)
                .attr("width", function (d) {
                    return xAxis(d.source__count);  //Just the data value
                });
        });

        return svg;
    };

    var SourceFacetView = Backbone.View.extend({
        initialize: function () {
            this.$source_facets = this.$('.source-facets');

            this.collection.on('sync', this.render, this);

            return this;
        },
        events: {},
        render: function () {
            this.$source_facets.empty();
            var objects = $.map(this.collection.models, function (d) {
                return d.toJSON();
            });
            d3Bar(this.$source_facets, objects);

            return this;
        },
    });

    return {
        SourceFacetView: SourceFacetView,
    }
});
