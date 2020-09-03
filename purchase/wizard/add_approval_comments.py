# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class ApproveComment(models.TransientModel):
	_name = 'purchase.order.approve.comment'

	approve_comment = fields.Html(string='Comments',required=True,)

	def approve_comment_wizard(self):
		if self.env.context.get('active_model') == 'purchase.order':
			active_model_id = self.env.context.get('active_model')
			purchase_order_obj = self.env['purchase.order'].search([('id', '=', active_model_id)])
			if purchase_order_obj:
				purchase_order_obj.write({'approve_comment':self.approve_comment})

