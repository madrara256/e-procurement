# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class BoardApproval(models.TransientModel):
	_name = 'board.approval'
	_description = 'describes path for board legalities'


	def board_approval_path(self):
		if self.env.context.get('active_model') == 'purchase.order':
			active_model_id = self.env.context.get('active_id')
			purchase_order_obj = self.env['purchase.order'].search([('id', '=', active_model_id)])
			if purchase_order_obj:
				purchase_order_obj.action_send_for_board()


