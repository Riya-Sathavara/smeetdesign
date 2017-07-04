odoo.define('menu_banner.customer_manager', function (require) {
"use strict";

// var bus = require('bus.bus').bus;
var config = require('web.config');
var core = require('web.core');
var data = require('web.data');
var Model = require('web.Model');
var session = require('web.session');
var time = require('web.time');
var web_client = require('web.web_client');
var discuss_ids = {};
var needaction_counter = 0;


// Public interface
//----------------------------------------------------------------------------------
var customer_manager = {
		get_discuss_ids: function () {
        return discuss_ids;
    },
    
    get_needaction_counter: function () {
       	return needaction_counter;                      
	},

};


// Initialization
// ---------------------------------------------------------------------------------
function init () {

	var load_channels = session.rpc('/customer/client_action').then(function (result) {
        needaction_counter = result.needaction_inbox_counter;
    });

    
	var ir_model = new Model("ir.model.data");
    var load_menu_id = ir_model.call("xmlid_to_res_id", ["account.menu_account_customer"], {}, {shadow: true});
   	var load_action_id = ir_model.call("xmlid_to_res_id", ["base.action_partner_customer_form"], {}, {shadow: true});
	

    return $.when(load_menu_id, load_action_id, load_channels).then(function (menu_id, action_id) {
        discuss_ids = {
            menu_id: menu_id,
            action_id: action_id,
        };
       // bus.start_polling();
    });
    
}
customer_manager.is_ready = init();

return customer_manager;

});