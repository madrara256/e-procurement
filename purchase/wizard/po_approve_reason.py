# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models,_

class POApproveReason(models.TransientModel):
	_name = 'po.approve.reason'

	po_approve_comment = fields.Char(string='Approval Comments', required=True,)


	def approve_reason(self):
		if self.env.context.get('active_model') == 'purchase.order':
			active_model_id = self.env.context.get('active_id')
			po_obj = self.env['purchase.order'].search([('id', '=', active_model_id)])
			if po_obj:
				po_obj.write(
								{
								'po_approve_comment':self.po_approve_comment,
								}
							 )
				po_obj.action_approve_purchase_order()
