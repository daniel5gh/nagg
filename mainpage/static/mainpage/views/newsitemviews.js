define([
    'jquery',
    'underscore',
    'backbone',
], function ($, _, Backbone) {
    var NewsItemRow = Backbone.View.extend({
        tagName: 'tr',
        events: {
            'click': function () {
                this.model.set('_expanded', !this.model.get('_expanded'))
            }
        },
        initialize: function () {
            var self = this;
            this.model.on('change', this.render, this);
            this.model.on('remove', function () {
                self.$el.remove();
            });
        },
        template: _.template($('#newsitem-row-template').html()),
        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });
    var NewsItemsTable = Backbone.View.extend({
        initialize: function () {
            this.$tbody = this.$('tbody');
            this.$aPrev = this.$('.link-prev');
            this.$aNext = this.$('.link-next');

            // when sync is done, we know we have new values for next/prev
            this.collection.on('sync', this.updatePrevNext, this);
            this.collection.on('add', this.addRowView, this);

            return this;
        },
        events: {},
        addRowView: function (model) {
            var newsItemView = new NewsItemRow({model: model});
            this.$tbody.append(newsItemView.render().$el);

            return newsItemView;
        },
        render: function () {
            var self = this;
            this.$tbody.empty();
            this.collection.each(function (newsItem) {
                self.addRowView(newsItem);
            });

            return this;
        },
        updatePrevNext: function () {
            // string.split('=')[1] is undefined when no = in string (this happens when it points to
            // first page) we can || 1. When we have no url at all (on first and last page), make it false
            // and remove the href.
            this.collection.urlPrevious ?
                this.$aPrev.attr('href', '#page/' + (this.collection.urlPrevious.split('=')[1] || 1)) :
                this.$aPrev.removeAttr('href');

            this.collection.urlNext ?
                this.$aNext.attr('href', '#page/' + (this.collection.urlNext.split('=')[1] || 1)) :
                this.$aNext.removeAttr('href');

            return this;
        }
    });

    return {
        NewsItemRow: NewsItemRow,
        NewsItemsTable: NewsItemsTable,
    }
});
