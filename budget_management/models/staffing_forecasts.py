# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models,api,_
from datetime import datetime
from odoo import exceptions
from odoo.exceptions import UserError, AccessError,ValidationError

class StaffForecasts(models.Model):
	_name = 'staff.forecasts'
	_description = 'Staffing Forecasts'
	_rec_name = 'department_id'
	_inherit = ['mail.thread', 'mail.activity.mixin']

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
								('dec', 'December')],string='Months',)
	department_id = fields.Many2one('hr.department', string='Department')
	job_id = fields.Many2one('hr.job', string='Position')
	current_number = fields.Integer(string='Current No.')
	proposed_number = fields.Integer(string='Proposed')
	difference = fields.Integer(string='Variance')


	@api.model
	def create(self, values):
		staffing = super(StaffForecasts, self).create(values)
		return staffing

	@api.multi
	def write(self, values):
		staffing = super(StaffForecasts, self).write(values)
		return staffing

	@api.multi
	def unlink(self):
		staffing = super(StaffForecasts,self).unlink()
		return staffing

	def copy_data(self, context=None):
		raise UserError(_('Staffing projection can not be duplicated...t'))


