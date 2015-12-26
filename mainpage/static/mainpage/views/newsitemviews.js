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

            // reset the whole view on any sync
            this.collection.on('sync', function () {
                self.renderPrevNext();
                self.$tbody.empty();
                self.render(self);
            });

            // issue with these events is that we need to keep track of views
            //this.collection.on('change add remove', function (model) {
            //    var a = arguments;
            //    console.log('rest', a);
            //    //self.$tbody.empty();
            //    self.renderOne(model);
            //});
        },
        //events: {
        //    "click #add-friend": "showPrompt",
        //},
        renderOne: function(model) {
            var newsItemView = new NewsItemRow({model: model});
            this.$tbody.append(newsItemView.render().$el);

            return newsItemView;
        },
        render: function () {
            var self = this;
            this.collection.each(function (newsItem) {
                self.renderOne(newsItem);
            });

            return this;
        },
        renderPrevNext: function () {
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
