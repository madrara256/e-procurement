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

	name = fields.Char(string='Reference', default='New', required=True)
	team_id = fields.Many2one('budget.team',string='Branch',)
	projection_period_id = fields.One2many('manpower.projection.period', 'man_projection_id', 
		'Projections Parameters', track_visibility='onchange')
	active = fields.Boolean(string='Active', default=True)
	color = fields.Integer(string='Index')
	date_from = fields.Date(string='Period')
	date_to = fields.Date(string='End Date')


	@api.model
	def create(self,values):
		if values.get('name', 'New') == 'New':
			values['name'] = self.env['ir.sequence'].next_by_code('manpower.sequence.code') or 'New'
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


class StaffingProjectionPeriod(models.Model):
		_name = 'manpower.projection.period'
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
		man_projection_id = fields.Many2one('manpower.forecasts', string='Projection Reference')

		department_id = fields.Many2one('hr.department', string='Department')
		job_id = fields.Many2one('hr.job', string='Position')
		current_number = fields.Integer(string='Current No.')
		proposed_number = fields.Integer(string='Proposed')
		difference = fields.Integer(string='Variance')

