# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models,api,_
from datetime import datetime
from odoo import exceptions
from odoo.exceptions import UserError, AccessError,ValidationError


class SavingsForecasts(models.Model):
	_name = 'savings.forecasts'
	_description = 'savings forecasts'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(string='Reference', default='New', required=True)
	active = fields.Boolean(string='Active', default=True)
	year = fields.Date(string='Duration',)
	color = fields.Integer(string='Index')
	forecasts_volume = fields.Float(string='Forecast Volume')
	forecast_cases = fields.Integer(string='Forecast Cases')
	actual_volume = fields.Float(string='Actual Volume')
	actual_cases = fields.Integer(string='Actual Cases')

	volume_variance = fields.Float(string='Volume Variance', compute='_compute_volume_variance')
	case_variance = fields.Float(string='Case Variance', compute='_compute_case_variance')


	@api.depends('forecasts_volume', 'actual_volume')
	def _compute_volume_variance(self):
		for record in self:
			if record.forecasts_volume > 0:
				mean = (record.forecasts_volume + record.actual_volume)/2
				mean_difference_forecast = (record.forecasts_volume - mean)**2
				mean_difference_actual = (record.actual_volume - mean)**2

				record.volume_variance = (mean_difference_forecast+mean_difference_actual)/2
				return record.volume_variance


	@api.depends('forecast_cases', 'actual_cases')
	def _compute_case_variance(self):
		for record in self:
			if record.forecast_cases > 0:
				record.case_variance = (record.forecast_cases - record.actual_cases)
				return record.case_variance
	month = fields.Selection(
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
				],string='Period', default='jan', group_expand='_expand_states',)
	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).month.selection]


	@api.model
	def create(self, values):
		forecasts = super(SavingsForecasts, self).create(values)
		return forecasts

	@api.multi
	def write(self,values):
		forecasts = super(SavingsForecasts, self).write(values)
		return forecasts


	@api.multi
	def unlink(self):
		forecasts = super(SavingsForecasts, self).unlink()
		return forecasts

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('Forecasts can not br duplicated...'))


class SavingsProjectionPeriod(models.Model):
		_name = 'savings.projection.period'
		_description = 'Projection Period'

