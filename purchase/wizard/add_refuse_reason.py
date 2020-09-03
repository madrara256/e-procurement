# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class CancelPurchaseOrder(models.TransientModel):
	_name = 'purchase.order.cancel.reason'

	cancel_reason = fields.Html(string='Cancel Reason', required=True,)

	def cancel_reason_wizard(self):
		if self.env.context.get('active_model') == 'purchase.order':
			active_model_id = self.env.context.get('active_id')
			purchase_order_obj = self.env['purchase.order'].search([('id', '=', active_model_id)])
			if purchase_order_obj:
				purchase_order_obj.write({'cancel_reason':self.cancel_reason})
				purchase_order_obj.button_cancel()

