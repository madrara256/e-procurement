# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models,api,_
from datetime import datetime
from odoo import exceptions
from odoo.exceptions import UserError, AccessError,ValidationError


class SavingsForecasts(models.Model):
	_name = 'savings.forecasts'
	_description = 'savings forecasts'
	_rec_name = 'team_id'
	_inherit = ['mail.thread', 'mail.activity.mixin']


	team_id = fields.Many2one(
							'budget.team',string='Branch',track_visibility='onchange',
							required=True,)
	budget_id = fields.Many2one('budget.management', string='Budget',track_visibility='onchange')
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
								('dec', 'December')],string='Months',group_expand='_expand_months',
								track_visibility='onchange', default='jan', help='Shows forecasts on monthly basis',
								required=True,)

	def _expand_months(self, months, domain, order):
		return [key for key, val in type(self).months.selection]

	forecast_volume = fields.Float(string='Forecast Volume',track_visibility='onchange')
	forecast_cases = fields.Integer(string='Forecast Cases',track_visibility='onchange')
	actual_volume = fields.Float(string='Actual Volume',track_visibility='onchange')
	actual_cases = fields.Float(string='Actual Cases',track_visibility='onchange')
	active = fields.Boolean('Active', default=True)
	color = fields.Integer('Index', default=0)

	image_small = fields.Binary(
		'Photo',attachment=True,
		help="Small-sized photo of the contracttor/supplier/customer/partner. It is automatically"
		"resized as a 64x64px image, with aspect ratio preserved."
		"Use this field anywhere a small image is required.")

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



