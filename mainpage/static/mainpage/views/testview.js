define([
    'jquery',
    'underscore',
    'backbone',
], function($, _, Backbone){
    // Our module now returns our view
    return Backbone.View.extend({
        el: $("body"),
        events: {
            "click #add-friend": "showPrompt",
        },
        showPrompt: function () {
            var friend_name = prompt("Who is your friend?");
        }
    });
});