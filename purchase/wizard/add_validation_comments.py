# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class ValidateComment(models.TransientModel):
	_name = 'purchase.order.validate.comment'

	validate_comment = fields.Html(string='Comments', required=True,)

	def validate_comment_wizard(self):
		if self.env.context.get('active_model') == 'purchase.order':
			active_model_id = self.env.context.get('active_id')
			purchase_order_obj = self.env['purchase.order'].search([('id', '=', active_model_id)])
			if purchase_order_obj:
				purchase_order_obj.write({'validate_comment':self.validate_comment})
				purchase_order_obj.button_confirm()
