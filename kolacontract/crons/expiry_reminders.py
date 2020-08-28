# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models,api,_,tools,SUPERUSER_ID

class ExpiryReminders(models.Model):
	_inherit = 'kola.contract'
	_description = 'Contracts Management'


	@api.model
	def reminders_for_expiry_notification(self):
		all_contracts  = self.env['kola.contract'].search([])
		for record in all_contracts:
			if record.state == 'renew':
				template_id = self.env.ref('kolacontract.expiry_mail_template')
				if template_id:
					template_id.send_mail(record.id, force_send=True)


