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
            this.$tbody = this.$('tbody');
            this.$aPrev = this.$('.link-prev');
            this.$aNext = this.$('.link-next');

            this.collection.on('change reset add remove', function () {
                self.$tbody.empty();
                self.render(self);
            });
        },
        //events: {
        //    "click #add-friend": "showPrompt",
        //},
        render: function () {
            var self = this;
            this.collection.each(function (newsItem) {
                var newsItemView = new NewsItemRow({model: newsItem});
                self.$tbody.append(newsItemView.render().$el);
            });

            // string.split('=')[1] is undefined when no = in string (this happens when it points to
            // first page) we can || 1. When we have no url at all (on first and last page), make it false
            // and remove the href.
            this.collection.urlPrevious ?
                this.$aPrev.attr('href', '#page/' + (this.collection.urlPrevious.split('=')[1] || 1)) :
                this.$aPrev.removeAttr('href');

            this.collection.urlNext ?
                this.$aNext.attr('href', '#page/' + (this.collection.urlNext.split('=')[1] || 1)) :
                this.$aNext.removeAttr('href');
        }
    });

    return {
        NewsItemRow: NewsItemRow,
        NewsItemsTable: NewsItemsTable,
    }
});
