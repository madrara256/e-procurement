odoo.define('budget_management', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var config = require('web.config');
var core = require('web.core');
var framework = require('web.framework');
var session = require('web.session');
var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

var DemoDashboard = AbstractAction.extend({
	template: 'DemoDashboardMain',

	init: function(){
		this.all_dashboards = ['apps', 'invitations', 'share'];
		return this._super.apply(this, arguments);
	},

	start: function(){
		return this.load(this.all_dashboards);
	},

	load: function(dashboards){
		var self = this;
		var loading_done = new $.Deferred();
		this._rpc({route: '/budget_web_settings_dashboard/data'})
			.then(function (data) {
				// Load each dashboard
				var all_dashboards_defs = [];
				_.each(dashboards, function(dashboard) {
					var dashboard_def = self['load_' + dashboard](data);
					if (dashboard_def) {
						all_dashboards_defs.push(dashboard_def);
					}
				});

				// Resolve loading_done when all dashboards defs are resolved
				$.when.apply($, all_dashboards_defs).then(function() {
					loading_done.resolve();
				});
			});
		return loading_done;
	},

	load_apps: function(data){
		return  new DemoDashboardApps(this, data.apps).replace(this.$('.o_web_settings_dashboard_apps'));
	},

	load_share: function(data){
		return new DemoDashboardShare(this, data.share).replace(this.$('.o_web_settings_dashboard_share'));
	},

	load_invitations: function(data){
		return new DemoDashboardInvitations(this, data.users_info).replace(this.$('.o_web_settings_dashboard_invitations'));
	},
});

var DemoDashboardInvitations = Widget.extend({
	template: 'DemoDashboardInvitations',

	init: function(parent, data) {
		this.data = data;
		this.parent = parent;
		this.emails = [];
		return this._super.apply(this, arguments);
	},

	//--------------------------------------------------------------------------
	// Private
	//--------------------------------------------------------------------------


	reload:function(){
		return this.parent.load(['invitations']);
	},

	//--------------------------------------------------------------------------
	// Handlers
	//--------------------------------------------------------------------------


});

var DemoDashboardApps = Widget.extend({

	template: 'DemoDashboardApps',

	init: function (parent, data) {
		this.data = data;
		this.parent = parent;
		return this._super.apply(this, arguments);
	},

	reload: function () {
		return this.parent.load(['apps']);
	}
});

var DemoDashboardShare = Widget.extend({
	template: 'DemoDashboardShare',

	init: function (parent, data) {
		this.data = data;
		this.parent = parent;
		return this._super.apply(this, arguments);
	},

	//--------------------------------------------------------------------------
	// Handlers
	//--------------------------------------------------------------------------

	reload: function () {
		return this.parent.load(['share']);
	}
});




core.action_registry.add('budget_settings_dashboard.main', DemoDashboard);

return {
	DemoDashboard: DemoDashboard,
	DemoDashboardApps: DemoDashboardApps,

	DemoDashboardInvitations: DemoDashboardInvitations
	};

});
