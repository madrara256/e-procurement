import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SendToProcurement(models.TransientModel):
	_name = 'procurement.stage'
	_description = 'Send to Procurement Committee'

	state = fields.Selection(
		[
			('draft', 'Draft'),
			('procurement', 'Procurement'),
			('sent', 'Sent RFQ'),
		], string='States', default='sent', required=True)

	@api.multi
	def move_records_to_procurement(self):
		requests = self.env['purchase.order'].search([('state', '=','sent')])
		for record in requests:
			#print('purchase orders '+str(record.name))
			record.write({'state':'procurement'})


	@api.multi
	def print_report(self):
		#self.ensure_one()
		[data] = self.read()

		sent_rfqs = self.env['purchase.order'].search([('state', '=', 'sent')])
		datas = {
			'ids': []
		}
		return self.env.ref('purchase.action_report_rfq_summary').with_context(from_transient_model=True).report_action(sent_rfqs,data=datas)

