# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models,_

class POConfirmReason(models.TransientModel):
	_name = 'po.confirm.reason'

	po_confirm_comment = fields.Char(string='Check Comments', required=True,)

	def confirm_reason(self):
		if self.env.context.get('active_model') == 'purchase.order':
			active_model_id = self.env.context.get('active_id')
			po_obj = self.env['purchase.order'].search([('id', '=', active_model_id)])
			if po_obj:
				po_obj.write(
								{
								'po_confirm_comment':self.po_confirm_comment,
								}
							 )
				po_obj.action_confirm_purchase_order()
