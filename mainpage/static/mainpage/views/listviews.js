define([
    'jquery',
    'underscore',
    'backbone',
], function ($, _, Backbone) {
    /**
     * Inheritors must set template
     */
    var ListItem = Backbone.View.extend({
        tagName: 'div',
        className: 'list-group-item',
        events: {
            'click': function () {
                this.toggleExpand();
            }
        },
        initialize: function () {
            var self = this;

            if (!this.template) {
                console.error('ListItem (', self, ') Please add template to this view.');
            }

            this.model.on('change', this.render, this);
            this.model.on('remove', function () {
                //self.$el.fadeOut(160, function() { $(this).remove(); });
                self.$el.remove();
            });
            // not rendered yet
            //this.$expand_button = this.$('.expand-button');
        },
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
    /**
     * Inheritors must set ItemView to a view
     */
    var ListView = Backbone.View.extend({
        initialize: function () {
            var self = this;

            if (!this.itemView) {
                console.error('ListView (', self, ') Please add itemView to this view.');
            }

            this.$list = this.$('.list-group');
            this.$aPrev = this.$('.link-prev');
            this.$aNext = this.$('.link-next');
            this.$searchBox = this.$('.search-box');
            this.$nrHits = this.$('.nr-hits');
            this.$pageNumber = this.$('.page-number');
            this.$pageMax = this.$('.page-max');

            // we assume all elements to be available in the html, lets check and warn
            // for missing
            $.each([this.$list, this.$aPrev, this.$aNext, this.$searchBox,
                this.$nrHits, this.$pageNumber, this.$pageMax], function () {
                if (this.length === 0) {
                    console.error('ListView (', self, ') missing element: ', this.selector)
                }
            });

            // when sync is done, we know we have new values for next/prev
            this.collection.on('reset', this.render, this);
            this.collection.on('add', this.addListItem, this);

            this.collection.queryParamsModel.on('change:_total', function (model, value) {
                self.$nrHits.text(value);
            });
            this.collection.queryParamsModel.on('change:_max_page', function (model, value) {
                self.$pageMax.text(value);
            });
            this.collection.queryParamsModel.on('change:page', function (model, value) {
                self.$pageNumber.text(value);
            });
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
            'click .link-prev': function () {
                this.collection.queryParamsModel.goPrevPage();
            },
            'click .link-next': function () {
                this.collection.queryParamsModel.goNextPage();
            },
        },
        handleSearchInputChange: function () {
            var self = this;
            clearTimeout(self.searchTimer);
            this.searchTimer = setTimeout(function () {
                self.collection.queryParamsModel.set('q', self.$searchBox.val());
            }, 250);
        },
        addListItem: function (model) {
            var view = new this.itemView({model: model});
            view.render().$el
                .hide()
                .appendTo(this.$list.show())
                .fadeIn(160);

            return view;
        },
        render: function () {
            var self = this;
            this.$list.fadeOut(300, function () {
                self.$list.html('');
            });

            this.collection.each(function (item) {
                self.addListItem(item);
            });

            return this;
        },
    });

    return {
        ListItem: ListItem,
        ListView: ListView,
    };
});