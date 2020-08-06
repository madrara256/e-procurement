from odoo import models, fields, api
from datetime import datetime,timedelta,date

class kolarating(models.Model):
	_name = 'kola.rating'
	_description = 'Kola Ratings Based On Service Delivery'
	_rec_name = 'contract_id'

	contract_id = fields.Many2one('kola.contract', string='Contract')
	vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('is_company', '=', True), ('supplier', '=', True)])
	date_from = fields.Datetime(related='contract_id.date_from', string='Start Date')
	date_to = fields.Datetime(related='contract_id.date_to', string='End Date')

	total_score = fields.Float(string='Service Delivery Score', compute='_compute_average_score')


	@api.multi
	def _compute_average_score(self):
		pass