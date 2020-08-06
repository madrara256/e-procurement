# -*- coding: utf-8 -*-

from odoo import models, fields, api

class kolaproduct(models.Model):
	_inherit = 'product.template'

	product_budget_category = fields.Selection(
										[('ICT', 'ICT'),
										('Business Development', 'Business Development'),
										('Finance', 'Finance'),
										('Audit', 'Audit'),
										('Credit', 'Credit'),
										('Human Resource', 'Human Resource'),
										('Legal', 'Legal'),
										('Risk', 'Risk'),
										('Operations', 'Operations'),
										('administration', 'Administration'),
										('Compliance', 'Compliance')])



