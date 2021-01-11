# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api,fields,models,_

class KolaContractRefuse(models.TransientModel):
	_name = "kolacontract.terminate.reason"

	reason_for_termination = fields.Html(string='Refuse Reason', required=True,)

	def terminate_reason(self):
		if self.env.context.get('active_model') =='kola.contract':
			active_model_id = self.env.context.get('active_id')
			kolarequest_obj = self.env['kola.contract'].search([('id', '=', active_model_id)])
			if kolarequest_obj:
				kolarequest_obj.write({'reason_for_termination':self.reason_for_termination})
				kolarequest_obj.contract_termination()
