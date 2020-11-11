from odoo import api, fields, models, _

class BudgetHistory(models.TransientModel):
	_name = 'budget.history'
	_description = 'Consolidated Budget'


	date = fields.Datetime(string='Date', help='Choose a date to get requests from that date', default=fields.Datetime.now)

	def open_table(self):
		self.ensure_one()

		tree_view_id = self.env.ref('budget_management.view_budget_line_tree').id
		form_view_id = self.env.ref('budget_management.view_budget_line_form').id

		action = {
			'type': 'ir.actions.act_window',
			'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
			'view_mode': 'tree,form',
			'name': _('Consolidated Budget'),
			'res_model': 'bm.budget.lines',
			'domain': "[]",
			'context': dict(self.env.context, create_date=self.date),
		}
		return action