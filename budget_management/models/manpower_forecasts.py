# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models,api,_
from datetime import datetime
from odoo import exceptions
from odoo.exceptions import UserError, AccessError,ValidationError


class ManPowerPlan(models.Model):
	_name = 'manpower.forecasts'
	_description = 'manpower forecasts'
	_rec_name='team_id'

	team_id = fields.Many2one('budget.team',string='Branch',)
	months = fields.Selection([
								('jan', 'January'),
								('feb', 'February'),
								('mar', 'March'),
								('apr','April'),
								('may', 'May'),
								('jun', 'June'),
								('jul', 'July'),
								('aug', 'August'),
								('sep','September'),
								('oct','October'),
								('nov', 'November'),
								('dec', 'December')],string='Months',
								group_expand='_expand_states',)
	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).months.selection]

	job_id = fields.Many2one('hr.job', string='Position')
	current_number = fields.Integer(string='Current No.')
	proposed_number = fields.Integer(string='Proposed')
	difference = fields.Integer(string='Variance')
	color = fields.Integer(string='Index')

	@api.model
	def create(self,values):
		rec = super(ManPowerPlan, self).create(values)
		return rec


	@api.multi
	def write(self, values):
		rec = super(ManPowerPlan, self).write(values)
		return rec

	@api.multi
	def unlink(self):
		rec = super(ManPowerPlan, self).unlink()

	def copy_data(self, context=None):
		raise UserError(_('Plan can not be duplicated, please contact system Administrator'))




