from odoo import api,fields,models,_

class BudgetRefuseReason(models.TransientModel):
	_name = 'budget.refuse.reason'

	budget_refuse_reason = fields.Html(string='Refuse Reason', required = True)

	def refuse_reason(self):
		if self.env.context.get('active_model') =='budget_management':
			active_model_id = self.env.context.get('active_id')
			kolarequest_obj = self.env['budget.management'].search([('id', '=', active_model_id)])
			if kolarequest_obj:
				kolarequest_obj.write({'budget_refuse_reason':self.budget_refuse_reason})
				kolarequest_obj.action_reject_proposal()

