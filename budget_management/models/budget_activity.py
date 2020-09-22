from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _,exceptions
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError,ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp

from fuzzywuzzy import fuzz


class BudgetActivity(models.Model):
	_name = 'budget.activity'
	_description = 'Budget Activity'
	_rec_name = 'name'


	name = fields.Char(string='Budget Reference')
	budget_id = fields.Many2one('budget.management', string='Budget Name')
	department_id = fields.Many2one('hr.department', related='budget_id.department_id', string='Department')
	def department_manager(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if employee_id:
			manager_id = employee_id.department_id.manager_id.id
			related_user_id = self.env['hr.employee'].search([('user_id', '=', manager_id)], limit=1)
			for user in related_user_id:
				return user.user_id
				
	department_manager_id = fields.Many2one('hr.employee',default=department_manager, string='Manager')

	budget_amount = fields.Float(string='Amount', related='budget_id.total_budget_cost')

	color = fields.Integer(string='Color')
	active = fields.Boolean(string='Active', default=True)


	count_purchase_order = fields.Integer(string='Purchase Orders', compute='_compute_purchase_orders')

	def _compute_purchase_orders(self):
		pass

