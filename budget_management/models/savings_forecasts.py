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
		if values.get('name', 'New') == 'New':
			values['name'] = self.env['ir.sequence'].next_by_code('savings.sequence.code') or 'New'
		forecasts = super(LoanForecasts, self).create(values)
		return forecasts

	@api.multi
	def write(self,values):
		forecasts = super(LoanLoanForecastsForecastLine, self).write(values)
		return forecasts


	@api.multi
	def unlink(self):
		forecasts = super(LoanForecasts).unlink()
		return forecasts

	def copy_data(self, default=None):
		raise UserError(_(' Forecast line can not be duplicated...'))

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
		forecasts = super(SavingsForecasts).unlink()
		return forecasts

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('Forecasts can not br duplicated...'))


class SavingsProjectionPeriod(models.Model):
		_name = 'savings.projection.period'
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

		savings_projection_id = fields.Many2one('savings.forecasts', string='Projection Reference')

		#staffing projections
		year = fields.Date(string='Year/Month')
		#loans
		forecasts_volume = fields.Float(string='Forecast Volume')
		forecast_cases = fields.Integer(string='Forecast Cases')
		actual_volume = fields.Float(string='Actual Volume')
		actual_cases = fields.Integer(string='Actual Cases')

