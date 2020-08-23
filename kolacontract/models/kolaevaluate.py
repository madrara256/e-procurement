# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api,_,tools,SUPERUSER_ID
from datetime import datetime,timedelta,date
from odoo.exceptions import UserError, AccessError, ValidationError
import math
from odoo.http import request
from werkzeug import url_encode

class KolaEvaluate(models.Model):
	_name = 'kolacontract.evaluate'
	_rec_name = 'contract_id'
	_description = 'Contract Evaluation'

	contract_id = fields.Many2one('kola.contract', string='Contract', track_visibility='onchange')
	evaluation_date = fields.Datetime(string='Date', default=datetime.today().now(), track_visibility='onchange')
	department_id = fields.Many2one('hr.department', related='contract_id.department_id', string='Department')

	def compute_access_url(self):
		action = self.env.ref('kolacontract.').id
		form_view_id = self.env.ref('kolacontract.').id
		for record in self:
			url_params = {
				'view_type': 'form',
				'model': 'kolacontract.kolacontract_evaluate',
				'id': record.id,
				'active_id':form_view_id,
				'action': action
			}
			url = '/web?#%s' %url_encode(url_params)

	evaluation_url = fields.Char(string='Evaluation form', compute='compute_access_url')

	state = fields.Selection([
		('draft', 'To Submit'),
		('confirm', 'To Approve'),
		('validate', 'Approved')],
		default='draft', string='Status',
		track_visibility='onchange', group_expand='_expand_states')

	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	def send_email_notification(self, obj):
		for record in self:
			if record.state == 'draft':
				template_id = self.env.ref('kolacontract.evaluate_draft_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)
			if record.state == 'confirm':
				template_id = self.env.ref('kolacontract.evaluate_confirm_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)
			if record.state == 'validate':
				template_id = self.env.ref('kolacontract.evaluate_validate_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

	#----------------------------------------------
	#Messaging methods
	#----------------------------------------------

	@api.multi
	def track_subtype(self, init_values):
		if 'state' in init_values and self.state == 'draft':
			return 'kolacontract.mt_evaluate_draft'
		if 'state' in init_values and self.state == 'confirm':
			return 'kolacontract.mt_evaluate_confirm'
		if 'state' in init_values and self.state == 'validate':
			return 'kolacontract.mt_evaluate_validate'

		return super(KolaEvaluate,self)._track_subtype(init_values)

	#-----------------------------------------------
	#Override ORM
	#-----------------------------------------------

	@api.model
	def create(self, values):
		evaluate = super(KolaEvaluate, self).create(values)
		return evaluate

	@api.multi
	def write(self, values):
		evaluate = super(KolaEvaluate, self).write(values)

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('Evaluation can not be duplicated'))

	@api.multi
	def unlink(self):
		return super(KolaEvaluate, self).unlink()







