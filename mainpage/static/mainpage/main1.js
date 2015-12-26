define([
    'jquery',
    'd3'
], function ($, d3) {
    var w = 500;
    var h = 100;
    var barPadding = 1;
    var svg = d3.select("body")
        .append("svg")
        .attr("width", w)
        .attr("height", h);

    var dataset = [ 5, 10, 15, 20, 25 ];

    var circles = svg.append('g').selectAll("circle")
        .data(dataset)
        .enter()
        .append("circle");

    circles
        .attr("cx", function(d, i) {
            return (i * 50) + 25;
        })
        .attr("cy", h/2)
        .attr("r", function(d) {
            return d;
        })
        .attr("fill", "yellow")
        .attr("stroke", "orange")
        .attr("stroke-width", function(d) {
            return d/2;
        });

    var dataset2 = [ 5, 10, 13, 19, 21, 25, 22, 18, 15, 13,
        11, 12, 15, 20, 18, 17, 16, 18, 23, 25 ];

    var bars = svg.append('g').selectAll("rect")
        .data(dataset2);

    bars.exit().remove();

    bars.enter()
        .append("rect")
        .attr("width", w / dataset2.length - barPadding)
        .attr('height', 0)
        .attr('y', h)
        .attr("x", function(d, i) {
            return i * (w / dataset2.length);
        })
        .transition().duration(1000)
        .attr("height", function(d) {
            return d;  //Just the data value
        })
        .attr("y", function(d) {
            return h - d;  //Height minus data value
        });
});