# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models,api,_
from datetime import datetime
from odoo import exceptions
from odoo.exceptions import UserError, AccessError,ValidationError

class StaffForecasts(models.Model):
	_name = 'staff.forecasts'
	_description = 'Staffing Forecasts'
	_rec_name = 'team_id'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Reference', default='New', required=True)
	team_id = fields.Many2one('budget.team',string='Branch',)
	projection_period_id = fields.One2many('staffing.projection.period', 'staffing_projection_id', 
		'Projections Parameters', track_visibility='onchange')
	active = fields.Boolean(string='Active', default=True)
	color = fields.Integer(string='Index')
	date_from = fields.Date(string='Period')
	date_to = fields.Date(string='End Date')

	@api.model
	def create(self, values):
		if values.get('name', 'New') == 'New':
			values['name'] = self.env['ir.sequence'].next_by_code('staffing.sequence.code') or 'New'
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


class StaffingProjectionPeriod(models.Model):
		_name = 'staffing.projection.period'
		_description = 'Projection Period'

		name = fields.Selection(
			[
				('jan', 'January'),
				('feb', 'February'),
				('mar', 'March'),
				('apr', 'April'),
				('may', 'May'),
				('jun', 'June'),
				('jul', 'July'),
				('aug', 'August'),
				('sep', 'September'),
				('oct', 'October'),
				('nov', 'November'),
				('dec', 'December')
				],string='Period', default='jan')
		staffing_projection_id = fields.Many2one('staff.forecasts', string='Projection Reference')

		department_id = fields.Many2one('hr.department', string='Department')
		job_id = fields.Many2one('hr.job', string='Position')
		current_number = fields.Integer(string='Current No.')
		proposed_number = fields.Integer(string='Proposed')
		difference = fields.Integer(string='Variance')



