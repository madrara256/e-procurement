from odoo import models,api,fields,_
from datetime import datetime
from odoo import exceptions
from odoo.exceptions import UserError, AccessError,ValidationError


class LoanForecasts(models.Model):
	_name = 'loan.forecasts'
	_description = 'loan forecasts'
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
			values['name'] = self.env['ir.sequence'].next_by_code('loan.forecast.code') or 'New'
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


	class LoanProjectionPeriod(models.Model):
		_name = 'loan.projection.period'
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
		loan_projection_id = fields.Many2one('loan.forecasts', string='Projection Reference')

		#staffing projections
		year = fields.Date(string='Year/Month')
		#loans
		forecasts_volume = fields.Float(string='Forecast Volume')
		forecast_cases = fields.Integer(string='Forecast Cases')
		actual_volume = fields.Float(string='Actual Volume')
		actual_cases = fields.Integer(string='Actual Cases')




