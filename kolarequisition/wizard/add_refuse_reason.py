# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api,fields,models,_

class kolarequestRefuseReason(models.TransientModel):
	_name = "kolarequest.refuse.reason"

	request_refuse_reason = fields.Html(string='Refuse Reason', required=True,)

	def refuse_reason(self):
		if self.env.context.get('active_model') =='kola.requisition':
			active_model_id = self.env.context.get('active_id')
			kolarequest_obj = self.env['kola.requisition'].search([('id', '=', active_model_id)])
			if kolarequest_obj:
				kolarequest_obj.write({'request_refuse_reason':self.request_refuse_reason})
				kolarequest_obj.reject_request()
