# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api,_,tools
from datetime import datetime,timedelta,date
from odoo.exceptions import UserError, AccessError, ValidationError



class KolaContractTerminate(models.Model):
	_name = 'kolacontract.terminate'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Contract termination'
	_rec_name = 'contract_id'

	#----------------------------------------------------------
	#DATABASE helper
	#----------------------------------------------------------

	contract_id = fields.Many2one(
									'kola.contract',
									string='Contract', domain=[('state', 'in', ('validate', 'renew'))])
	date_from = fields.Datetime(
								string='Start Date',
								related='contract_id.date_from',
								readonly=True, store=True,)
	date_to = fields.Datetime(
								string='End Date',
								related='contract_id.date_to',
								readonly=True, store=True,)
	amount = fields.Float(
							string='Amount',
							related='contract_id.amount', readonly=True, store=True,)
	ratings = fields.Selection('Rating', related='contract_id.ratings', readonly=True, store=True,)
	image_medium = fields.Binary(string='Photo', related='contract_id.image_medium', readonly=True, store=True,)
	state = fields.Selection(
								[
									('draft', 'Draft'),
									('confirm', 'Review By Admin'),
									('validate1', 'Review By Procurement'),
									('validate2', 'Legal'),
									('validate3', 'Sign Off'),
									('validate', 'Signed'),
									('reject', 'Rejected')
								],
								string='States',
								group_expand='_expand_states',
								track_visibility='onchange',
								help='Help track contract termination process',
								default='draft')
	kolacontract_line_terminate_id = fields.One2many(
														'kolacontract.terminate.line',
														'kolacontract_terminate_id',
														string='Contract Terminate line')
	active = fields.Boolean(string='Active', default=True)
	department_id = fields.Many2one('hr.department', string='Department')

	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	def notification_reciepients(self):
		#check the department raising the request,legal & administration head/supervisor
		pass


	@api.multi
	def send_by_email(self):
		pass


	#--------------------------------------------------------
	#Override CRUD
	#---------------------------------------------------------
	@api.model
	def create(self, values):
		rec = super(KolaContractTerminate, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(values)
		return rec

	@api.multi
	def write(self, values):
		rec = super(KolaContractTerminate, self).write(values)
		return rec

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('A Contract cannot be duplicated'))

	@api.multi
	def unlink(self):
		return super(KolaContractTerminate,self).unlink()

	#--------------------------------------------------------
	#Business logic
	#--------------------------------------------------------

	@api.multi
	def confirm_terminate(self):
		if any(contract.state != 'draft' for contract in self):
			raise ValidationError('Contract must be raised by user department before it can be reviewed by Administration \n'+
			'Please Contact your System Administrator')
		self.write({'state':'confirm'})

	@api.multi
	def review_termination_by_admin(self):
		if any(contract.state != 'confirm' for contract in self):
			raise ValidationError('Contract must be reviewed by Administration before it can be reviewed by Procurement \n'+
			'Please contact your System Administrator')
		self.write({'state':'validate1'})

	@api.multi
	def review_by_procurement(self):
		if any(contract.state != 'validate1' for contract in self):
			raise ValidationError('Contract must be Reviewed by Procurement before Legal \n'+
			'Please Contact your System Administrator')
		self.write({'state': 'validate2'})

	@api.multi
	def validate_terminate(self):
		if any(contract.state != 'validate2' for contract in self):
			raise ValidationError('Contract must be Reviewed by Legal before it can be Signed Off \n'+
			'Please Contact your System Administrator')
		self.write({'state':'validate3'})

	@api.multi
	def sign_off_termination(self):
		if any(contract.state != 'validate2' for contract in self):
			raise ValidationError('Contract termination must be drafted by Legal before it can be Signed Off \n'+
			'Please Contact Your System Administrator')
		self.write({'state':'validate'})

	@api.multi
	def reject_terminate(self):
		self.write({'state': 'reject'})
		contracts = self.env['kola.contract'].browse(self.contract_id)
		for contract in contracts:
			contract.sudo().write({'active':True})

	#---------------------------------------------------------
	#Messaging methods
	#---------------------------------------------------------

	@api.multi
	def _track_subtype(self, init_values):
		if 'state' in init_values and self.state == 'draft':
			return 'kolacontract.mt_terminate_draft'
		if 'state' in init_values and self.state == 'confirm':
			return 'kolacontract.mt_terminate_confirm'
		if 'state' in init_values and self.state == 'validate':
			return 'kolacontract.mt_terminate_validate'
		if 'state' in init_values and self.state == 'confirm':
			return 'kolacontract.mt_terminate_reject'
		return super(KolaContractTerminate,self)._track_subtype(init_values)


class KolacontractTerminateLine(models.Model):
	_name = 'kolacontract.terminate.line'
	_description = 'Contract termination line'

	name = fields.Char(string='Reference')
	product_id = fields.Many2one('product.product', string='Product')
	kolacontract_terminate_id = fields.Many2one('kolacontract.terminate', string="Contract Reference", ondelete='cascade')

	@api.model
	def create(self,values):
		rec = super(KolacontractTerminateLine, self).create(values)
		return rec

	@api.multi
	def write(self,values):
		rec = super(KolacontractTerminateLine, self).create(values)
		return rec

	@api.multi
	def unlink(self):
		return super(KolacontractTerminateLine, self).unlink()

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('A Contract line cannot be duplicated'))



