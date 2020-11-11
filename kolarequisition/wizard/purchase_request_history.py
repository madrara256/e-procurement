from odoo import api, fields, models, _

class PurchaseRequestHistory(models.TransientModel):
	_name = 'purchase.request.history'
	_description = 'Purchase Request History'


	date = fields.Datetime(string='From(Request Date)', help='Choose a date to get requests from that date', default=fields.Datetime.now)

	def open_table(self):
		self.ensure_one()

		tree_view_id = self.env.ref('kolarequisition.requisition_line_view_tree').id
		form_view_id = self.env.ref('kolarequisition.requisition_line_form').id
		#we pass 'to_date' in the context so that the requests will be computed accross 
		#till the to date and the state be checked as well

		action = {
			'type': 'ir.actions.act_window',
			'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
			'view_mode': 'tree,form',
			'name': _('Request lines'),
			'res_model': 'kola.requisition.lines',
			'domain': "[('status', 'in', ['validate'])]",
			'context': dict(self.env.context, create_date=self.date),
		}
		return action
		


