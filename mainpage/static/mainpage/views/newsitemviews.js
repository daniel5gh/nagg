define([
    'jquery',
    'underscore',
    'backbone',
], function ($, _, Backbone) {
    var NewsItemRow = Backbone.View.extend({
        tagName: 'div',
        className: 'list-group-item',
        events: {
            'click': function () {
                this.toggleExpand();
            }
        },
        initialize: function () {
            var self = this;
            this.model.on('change', this.render, this);
            this.model.on('remove', function () {
                self.$el.remove();
            });
            // not rendered yet
            //this.$expand_button = this.$('.expand-button');
        },
        template: _.template($('#newsitem-row-template').html()),
        render: function () {
            this.$el.html(this.template(this.model.toJSON()));
            // now it is rendered
            this.$expand_button = this.$('.expand-button');
            this.$collapsible = this.$('.collapse');
            // initialize
            //this.$collapsible.collapse({
            //    toggle: false
            //});
            return this;
        },
        toggleExpand: function () {
            var newMode = !this.model.get('_expanded');
            this.model.set('_expanded', newMode);
            if (newMode) {
                this.$collapsible.collapse('show');
            } else {
                this.$collapsible.collapse('hide');
            }
        }
    });
    var NewsItemsTable = Backbone.View.extend({
        initialize: function () {
            this.$list = this.$('.list-group');
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
            this.$list.append(newsItemView.render().$el);

            return newsItemView;
        },
        render: function () {
            var self = this;
            this.$list.empty();
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
