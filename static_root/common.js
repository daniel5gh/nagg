requirejs.config({
    baseUrl: 'static/',
    paths: {
        mainpage: 'mainpage',
        jquery: 'node_modules/jquery/dist/jquery.min',
        d3: 'node_modules/d3/d3.min',
        backbone: 'node_modules/backbone/backbone-min',
        underscore: 'node_modules/underscore/underscore-min',
        bootstrap: 'node_modules/bootstrap/dist/js/bootstrap',
    }
});

// load bootstrap jQuery plugins
require(['jquery'], function ($) {
    require(['bootstrap']);
});
