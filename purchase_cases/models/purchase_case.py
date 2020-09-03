# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_cases(models.Model):
	_name = 'purchase.case'
	_inherit = ['mail.thread']

	name = fields.Char(string='Name')
	case_value_upper = fields.Float(string='Case Value Upper')
	case_value_lower = fields.Float(string='Case Value Lower')
	description = fields.Html(string='Description')
	code  = fields.Char(string='Code')
	active = fields.Boolean(string='Active', default=True)


