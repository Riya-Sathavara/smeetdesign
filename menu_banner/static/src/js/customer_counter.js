odoo.define('menu_banner.customer_counter', function (require) {
"use strict";

var core = require('web.core');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var customer_manager = require('menu_banner.customer_manager');
/**
 * Menu item appended in the systray part of the navbar, redirects to the Inbox in Discuss
 * Also displays the needaction counter (= Inbox counter)
 */
var InboxItem1 = Widget.extend({
    template:'menu_banner.InboxItem1',
    events: {
    	"click": "on_click",
    },
    
    start: function () {
        this.$needaction_counter = this.$('.o_notification_counter');
        // customer_manager.bus.on("", this, this.update_counter);
        customer_manager.is_ready.then(this.update_counter.bind(this));
        // return this._super();
    },
    update_counter: function () {
        var counter = customer_manager.get_needaction_counter();
        this.$needaction_counter.text(counter);
        this.$el.toggleClass('o_no_notification', !counter);
    },
    
   on_click: function (event) {
        event.preventDefault();
       	customer_manager.is_ready.then(this.discuss_redirect.bind(this));
    },
    discuss_redirect: _.debounce(function () {
        var self = this;
        var discuss_ids = customer_manager.get_discuss_ids();
        this.do_action(discuss_ids.action_id, {clear_breadcrumbs: true}).then(function () {
            self.trigger_up('hide_app_switcher');
            core.bus.trigger('change_menu_section', discuss_ids.menu_id);
        });
    }, 1000, true),
   
});
SystrayMenu.Items.push(InboxItem1);
});