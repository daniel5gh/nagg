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
                //self.$el.fadeOut(160, function() { $(this).remove(); });
                self.$el.remove();
            });
            // not rendered yet
            //this.$expand_button = this.$('.expand-button');
        },
        template: _.template($('#newsitem-row-template').html()),
        render: function () {
            this.$el
                .html(this.template(this.model.toJSON()));
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
            this.$searchBox = this.$('.search-box');
            this.$nrHits = this.$('.nr-hits');

            // when sync is done, we know we have new values for next/prev
            this.collection.on('sync', this.updatePrevNext, this);
            this.collection.on('reset', this.render, this);
            this.collection.on('add', this.addRowView, this);

            return this;
        },
        events: {
            'input .search-box': function () {
                this.handleSearchInputChange();
            },
            'click .search-box-clear-button': function () {
                this.$searchBox.val('');
                this.handleSearchInputChange();
            },
        },
        handleSearchInputChange: function () {
            var self = this;
            clearTimeout(self.searchTimer);
            this.searchTimer = setTimeout(function () {
                self.collection.queryParams.q = self.$searchBox.val();
                self.collection.fetch();
            }, 100);
        },
        addRowView: function (model) {
            var newsItemView = new NewsItemRow({model: model});
            newsItemView.render().$el
                .hide()
                .appendTo(this.$list.show())
                .fadeIn(160);

            return newsItemView;
        },
        render: function () {
            var self = this;
            this.$list.fadeOut(300, function () {
                self.$list.html('');
            });

            this.collection.each(function (newsItem) {
                self.addRowView(newsItem);
            });
            this.updatePrevNext();

            return this;
        },
        updatePrevNext: function () {
            // string.split('=')[1] is undefined when no = in string (this happens when it points to
            // first page) we can || 1. When we have no url at all (on first and last page), make it false
            // and remove the href.
            this.collection.urlPrevious ?
                this.$aPrev.attr('href',
                    '#page/' + (this.collection.queryParams.page - 1) +
                    '/' + this.collection.queryParams.page_size) :
                this.$aPrev.removeAttr('href');

            this.collection.urlNext ?
                // + to coerce to int
                this.$aNext.attr('href', '#page/' + (+this.collection.queryParams.page + 1) +
                    '/' + this.collection.queryParams.page_size) :
                this.$aNext.removeAttr('href');

            this.$nrHits.text(this.collection.totalRecords);

            return this;
        }
    });

    return {
        NewsItemRow: NewsItemRow,
        NewsItemsTable: NewsItemsTable,
    }
});
