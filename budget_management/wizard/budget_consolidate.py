from odoo import api, fields, models, tools
import time
import logging
import threading
from odoo.exceptions import UserError, AccessError,ValidationError

_logger = logging.getLogger(__name__)

class BudgetConsolidate(models.TransientModel):
	_name = 'budget.consolidate'
	_description = 'Generate Consolidated Budget'

	date_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
	depts = fields.Many2many('hr.department',string='Department(s)')

	budget_type = fields.Selection([
		('draft', 'To Submit'),
		('propose', 'Budget Proposal'),
		('review1', 'Budget Review'),
		('consolidate', 'Consolidation'),
		('review', 'Management Review'),
		('validate', 'Approved Budget'),
		('reject', 'Rejected Budget'),
		('reset', 'Reset To Draft')
		], string='Request Status', required=True, default='validate')


	@api.multi
	def print_consolidated_budget(self):
		self.ensure_one()
		[data] = self.read()
		if not data.get('depts'):
			raise UserError(_('You have to select at least one department. And try again'))
		departments = self.env['hr.department'].browse(data['depts'])
		datas = {
			'ids': [],
			'model': 'hr.department',
			'form': data
		}		
		return self.env.ref('budget_management.action_consolidated_budget_report').with_context(from_transition_model=True).report_action(departments, datas)