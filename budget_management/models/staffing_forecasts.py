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

	@api.depends('projection_period_id.current_number')
	def _compute_current_number(self):
		for record in self:
			current_total = 0.0
			for item in record.projection_period_id:
				current_total += item.current_number
				record.update({'current_total_number':current_total})

	@api.depends('projection_period_id.proposed_number')
	def _compute_proposed_number(self):
		for record in self:
			proposed_total = 0
			for item in record.projection_period_id:
				proposed_total += item.proposed_number
				record.update({'propose_total_number':proposed_total})


	name = fields.Char(string='Reference', default='New', required=True)
	team_id = fields.Many2one('budget.team',string='Branch',)
	projection_period_id = fields.One2many('staffing.projection.period', 'staffing_projection_id', 
		'Projections Parameters', track_visibility='onchange')
	active = fields.Boolean(string='Active', default=True)
	color = fields.Integer(string='Index')
	date_from = fields.Date(string='Period')
	date_to = fields.Date(string='End Date')
	current_total_number = fields.Float(string='Current Total', compute='_compute_current_number',)
	propose_total_number = fields.Float(string='Proposed Total', compute='_compute_proposed_number',)

	staffing_variance = fields.Float(string='Variance', compute='_compute_staffing_variance')

	@api.depends('current_total_number', 'propose_total_number')
	def _compute_staffing_variance(self):
		for record in self:
			if record.propose_total_number > 0:
				mean = (record.propose_total_number+record.current_total_number)/2
				mean_difference_current = (record.current_total_number - mean)**2
				mean_difference_propose = (record.propose_total_number - mean)**2
				record.staffing_variance = (mean_difference_current - mean_difference_propose)/2
				return record.staffing_variance

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
		staffing = super(StaffForecasts, self).unlink()
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
		difference = fields.Integer(string='Variance', compute='_compute_difference')

		@api.onchange('current_number', 'proposed_number')
		def _compute_difference(self):
			for record in self:
				record.difference = (self.proposed_number - self.current_number)
				return record.difference


