# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
from odoo import models, api, fields
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
	_inherit = 'res.company'
	_description = 'Description'


	#--------------
	#.Database
	#--------------
	p2p_onboarding_state = fields.Selection(
		selection=[
			('not_done', "Not done"),
			('just_done', "Just done"),
			('done', "Done"),
			('closed', "Closed")
		],
		string="Procure2pay Onboarding State",
		default='not_done')

	p2p_onboarding_budget_state = fields.Selection(
		selection=[
			('not_done', "Not done"),
			('just_done', "Just done"),
			('done', "Done"),
			('closed', "Closed")
		],
		string="Procure2pay Onboarding Budget State",
		default='not_done')

	p2p_onboarding_requisition_state = fields.Selection(
		selection=[
			('not_done', "Not done"),
			('just_done', "Just done"),
			('done', "Done"),
			('closed', "Closed")
		],
		string="Procure2pay Onboarding Requisition State",
		default='not_done')

	p2p_onboarding_purchase_state = fields.Selection(
		selection=[
			('not_done', "Not done"),
			('just_done', "Just done"),
			('done', "Done"),
			('closed', "Closed")
		],
		string="Procure2pay Onboarding Purchase State",
		default='not_done')



	def get_and_update_p2p_onboarding_state(self):
		return self.get_and_update_onbarding_state(
				'p2p_onboarding_state',
				self.get_procure2pay_steps_states_names()
				)

	def get_procure2pay_steps_states_names(self):
		return [
			'p2p_onboarding_budget_state',
			'p2p_onboarding_requisition_state',
			'p2p_onboarding_purchase_state',
		]


	#----------
	# Actions
	#---------

	@api.model
	def action_open_p2p_onboarding_budgets(self):
		return self.env.ref('procure2pay.action_template_window').read()[0]

	@api.model
	def action_open_p2p_onboarding_requisition(self):
		budget = self.env['budget.management'].search([],order='create_date desc', limit=1)
		action = self.env.ref('procure2pay.kolapr_new_act_window').read()[0]
		action['context'] = {**self.env.context, **{}
		}
		return action
	@api.model
	def action_open_p2p_onboarding_purchase(self):
		requisition = self.env['kola.requisition'].search([], order='create_date desc', limit=1)
		action = self.env.ref('procure2pay.p2ppurchase_rfq').read()[0]
		action['context'] = {**self.env.context, **{}
		}
		return action
	@api.model
	def action_close_p2p_onboarding(self):
		self.env.user.company_id.p2p_onboarding_state == 'closed'
