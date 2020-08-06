odoo.define('budget_management.gantt_controller', function(require){
	"use strict"

	var AbastractController = require('web.AbastractController');
	var core = require('web.core');
	var config = require('web.config');
	var Dialog = require('web.Dialog');
	var dialogs = require('web.view_dialogs');
	var time = require('web.time')

	var _t = core._t;
	var qweb = core.qweb;

		var gantt_controller = AbastractController.extend({
			init: function(parent, model, renderer, params){
				this._super.apply(this, arguments)
			}
		});

		return gantt_controller;
});