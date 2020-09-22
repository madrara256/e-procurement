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
		string='Period',
		related='contract_id.date_from', readonly=True, store=True,)
	date_to = fields.Datetime(
		string='End Date',related='contract_id.date_to',readonly=True, store=True,)
	amount = fields.Float(
		string='Amount',
		related='contract_id.amount', readonly=True, store=True,)
	ratings = fields.Selection('Rating', related='contract_id.ratings', readonly=True, store=True,)
	image_medium = fields.Binary(string='Photo', related='contract_id.image_medium', readonly=True, store=True,)
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,
		default=lambda self: self.env.user.company_id.currency_id.id)
	state = fields.Selection(
		[
			('draft', 'Draft'),
			('confirm', 'To Admin'),
			('validate1', 'To Procurement'),
			('validate2', 'To Legal'),
			('validate3', 'To Sign Off'),
			('validate', 'Signed'),
			('reject', 'Rejected')
		],string='States',group_expand='_expand_states', track_visibility='onchange',help='Help track contract termination process',
			default='draft')
	kolacontract_line_terminate_id = fields.One2many('kolacontract.terminate.line',
		'kolacontract_terminate_id',
		string='Contract Terminate line')
	user_id = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
	def default_employee(self):
		employee = self.env['hr.employee'].search([('active', '=', True), ('user_id', '=', self.env.uid)], limit=1)
		for empid in employee:
			return empid.id

	def _department_manager(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if employee_id:
			manager_id = employee_id.department_id.manager_id.id
			related_user_id = self.env['hr.employee'].search([('user_id', '=', manager_id)], limit=1)
			for user in related_user_id:
				return user.user_id


	department_manager = fields.Many2one('hr.employee', string='Department Manager', 
		default=_department_manager)

	employee_id = fields.Many2one('hr.employee', string='Employee', default=default_employee)

	def department_of_loggedin(self):
		employee_id = self.env['hr.employee'].search([('active', '=', True), ('user_id', '=', self.env.uid)])
		if employee_id:
			return employee_id.department_id

	department_id = fields.Many2one('hr.department', string='Department')

	active = fields.Boolean(string='Active', default=True)
	contract_doc = fields.Many2many('ir.attachment',string='Attach a file(s)')
	count_files = fields.Integer(compute='compute_count_files', string='Document(s)', attachment=True)

	comments_admin = fields.Html(string='Comments')
	comments_user_department = fields.Html(string='Comments')
	procurement_minute_extracts = fields.Binary(string='Minute Extracts', attachment=True)


	def _compute_access_url(self):
		action = self.env.ref('kolacontract.kolacontract_action').id
		form_view_id = self.env.ref('kolacontract.kolacontract_form').id
		for record in self:
			url_params = {
				'view_type': 'form',
				'model':'kolacontract.kola_contract',
				'id':record.id,
				'active_id':record.id,
				'view_id': form_view_id,
				'action': action
			}
			url = '/web?#%s' %url_encode(url_params)
			record.contract_url = url
	contract_url = fields.Char(string='Contract Url', compute='_compute_access_url')
	digital_signature = fields.Binary(string='Signature',oldname="signature_image",
						attachment=True)


	@api.depends('contract_doc')
	def compute_count_files(self):
		for record in self:
			record.count_files = len(record.contract_doc)


	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	def notification_reciepients(self):
		#check the department raising the request,legal & administration head/supervisor
		pass

	def send_email_notification(self, obj):
		for record in self:
			if record.state == 'draft':
				template_id = self.env.ref('kolacontract.con_terminate_draft')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'confirm':
				template_id = self.env.ref('kolacontract.con_terminate_confirm')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate1':
				template_id = self.env.ref('kolacontract.con_terminate_proc_review')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate2':
				template_id = self.env.ref('kolacontract.con_terminate_legal_review')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate3':
				template_id = self.env.ref('kolacontract.con_terminate_signoff')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate':
				template_id = self.env.ref('kolacontract.con_terminate_signoff_confirm')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)
			elif record.state == 'reject':
				template_id = self.env.ref('kolacontract.con_terminate_signoff_rejected')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

	#--------------------------------------------------------
	#Override CRUD
	#---------------------------------------------------------
	@api.model
	def create(self, values):
		# if len(values.get('kolacontract_line_terminate_id')) > 1:
		# 	raise ValidationError(_('Record limit Exceeded!'))
		# if not values.get('kolacontract_line_id'):
		# 	raise ValidationError(_('Please Specify the service for the Contract Draft'))
		# if len(values.get('kolacontract_line_id')) > 1:
		# 	raise ValidationError(_('Record limit Exceeded!'))
		rec = super(KolaContractTerminate, self).create(values)
		return rec

	@api.multi
	def write(self, values):
		for record in self:
			if len(record.kolacontract_line_terminate_id) > 1:
				raise ValidationError(_('Record limit Exceeded!'))
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
	def contract_termination_share(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('kolacontract', 'contract_terminate_share_mail_template')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = {
			'default_model':'kolacontract.terminate',
			'default_res_id':self.ids[0],
			'default_use_template':bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent':True,
			'force_email': True
		}
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views':[(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

	@api.multi
	def confirm_terminate(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'draft' for contract in self):
			raise ValidationError('Contract termination draft must be raised by user department \n'+
			'Please Contact your System Administrator')
		self.write({'state':'confirm'})
		return reload

	@api.multi
	def review_by_procurement(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'confirm' for contract in self):
			raise ValidationError(_('Contract must be Reviewed by Procurement before Legal \n'+
			'Please Contact your System Administrator'))
		self.write({'state': 'validate1'})
		return reload

	@api.multi
	def review_by_legal(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'validate1' for contract in self):
			raise ValidationError(_('Contract must be Reviewed by Procurement before Legal Review \n'+
			'Please Contact your System Administrator'))
		self.write({'state':'validate2'})
		return reload


	@api.multi
	def send_for_termination(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'validate2' for contract in self):
			raise ValidationError('Contract termnation must be drafted first before it can be Reviewed by Administration \n'+
			'Please contact your System Administrator')
		self.write({'state':'validate3'})
		return reload


	@api.multi
	def approve_termination(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'validate3' for contract in self):
			raise ValidationError(_('Contract termination must be drafted by Legal before it can be Signed Off \n'+
			'Please Contact Your System Administrator'))
		self.write({'state':'validate'})
		return reload


	@api.multi
	def reject_terminate(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		self.write({'state': 'reject'})
		contracts = self.env['kola.contract'].browse(self.contract_id)
		for contract in contracts:
			contract.sudo().write({'active':True})
		return reloadS

	@api.multi
	def send_contract_back_astep(self):
		for record in self:
			if record.state == 'confirm':
				record.write({'state': 'draft'})
			if record.state == 'validate1':
				record.write({'state': 'confirm'})
			elif record.state == 'validate2':
				record.write({'state': 'validate1'})
			elif record.state == 'validate3':
				record.write({'state':'validate2'})
			elif record.state == 'validate':
				record.write({'state': 'validate3'})

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
	currency_id = fields.Many2one(related='kolacontract_terminate_id.currency_id', string='Currency', store=True, track_visibility='onchange')
	date_from = fields.Datetime(string='Start Date')
	date_to = fields.Datetime(string='End Date')
	total_qnty = fields.Float(string='Quantity', track_visibility='onchange', store=True)
	unit_cost = fields.Float(string='Unit Cost', track_visibility='onchange')
	total_amount = fields.Float(string='Subtotal Amount', track_visibility='onchange', compute='_compute_total_amount')
	product_category = fields.Many2one('product.category', string='Product Category', track_visibility='onchange', store=True)
	description = fields.Char(string='Specifications')

	@api.onchange('unit_cost', 'total_qnty')
	def _compute_total_amount(self):
		self.total_amount = self.total_qnty * self.unit_cost


	@api.model
	def create(self,values):
		user_id = values.get('user_id', False)
		rec = super(KolacontractTerminateLine, self).create(values)
		return rec

	@api.multi
	def write(self,values):
		user_id = values.get('user_id', False)
		if values.get('procurement_minute_extracts'):
			#trigger email notification ---chair procurement committee
			template_id = self.env.ref('kolacontract.mail_template_for_minute_signup')
			if template_id:
				template_id.send_mail(self.id, force_send=True)
		rec = super(KolacontractTerminateLine, self).create(values)
		return rec

	@api.multi
	def unlink(self):
		return super(KolacontractTerminateLine, self).unlink()

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('A Contract line cannot be duplicated'))



