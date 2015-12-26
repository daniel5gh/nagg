define([
    'jquery',
    'underscore',
    'backbone',
], function ($, _, Backbone) {
    var NewsItemRow = Backbone.View.extend({
        tagName: 'tr',
        //events: {
        //    "click #add-friend": "showPrompt",
        //},
        template: _.template($('#newsitem-row-template').html()),
        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });
    var NewsItemsTable = Backbone.View.extend({
        initialize: function () {
            var self = this;
            this.collection.on('change reset add remove', function () {
                self.$el.empty();
                self.render(self);
            })
        },
        //events: {
        //    "click #add-friend": "showPrompt",
        //},
        render: function () {
            var self = this;
            this.collection.each(function (newsItem) {
                var newsItemView = new NewsItemRow({model: newsItem});
                self.$el.append(newsItemView.render().$el);
            });

            return this;
        }
    });

    return {
        NewsItemRow: NewsItemRow,
        NewsItemsTable: NewsItemsTable,
    }
});
