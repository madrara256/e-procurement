# -*- coding: utf-8 -*-

from odoo import models, fields, api,_,tools,SUPERUSER_ID
from datetime import datetime,timedelta,date
from odoo.exceptions import UserError, AccessError, ValidationError
import math
from odoo.http import request
from werkzeug import url_encode

AVAILABLE_RATINGS = [
	('1', 'Poor'),
	('2', 'Fair'),
	('3', 'Good'),
	('4', 'Very Good'),
	('5', 'Excellent'),
]
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CONTRACT_NOTIFY_THRESH = 90.0
DAYS_IN_A_YEAR = 365.0

receipients = []

class kolacontract(models.Model):
	_name = 'kola.contract'
	_description = 'Kola Contracts'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'mail.alias.mixin']
	_mail_post_access = 'read'
	_rec_name = 'contractor_id'

	#---------------------------------------------------------------------
	#Database
	#---------------------------------------------------------------------

	@api.depends('kolacontract_line_id.total_amount')
	def _compute_contract_total(self):
		for contract in self:
			subtotal_amount = 0.0
			for item in contract.kolacontract_line_id:
				subtotal_amount += item.total_amount
				contract.update(
								{
									'amount':subtotal_amount
								})
	def get_alias_model_name(self, vals):
		return vals.get('alias_model', 'kola.contract')

	state = fields.Selection([
		('draft', 'Draft'),
		('validate1', 'To Procurement'),
		('validate2', 'To Legal'),
		('validate3', 'To Sign Off'),
		('validate', 'Running Contracts'),
		('renew', 'Contract Due To Expire'),
		('evaluate', 'Evaluate Contracts'),
		('terminate', 'Terminated Contracts')]
		, string='Status', group_expand='_expand_states',
		track_visibility='onchange', help='Status of the contract',
		default='draft')

	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	name  = fields.Char(string='Contract Reference', default='New', required=True, track_visibility='onchange')
	product_id = fields.Many2one('product.product', string='Service', track_visibility='onchange')
	date_from = fields.Datetime(string='Period', track_visibility='onchange')
	date_to = fields.Datetime(string='End Date', track_visibility='onchange')
	duration = fields.Float(string='Duration of Contract', compute='_compute_duration', track_visibility='onchange',store=True)
	attachment_number = fields.Integer(compute='_get_attachment_number', string='Number Of Attachments')

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

	amount = fields.Float(string='Amount', compute='_compute_contract_total', store=True,)
	number_of_days_due = fields.Float(string='Number of Days Left', track_visibility='onchange')


	#attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'kola.contract')], string='Attachments')
	contract_doc = fields.Many2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'kola.contract')], string='Attachments')
	contract_file_name = fields.Char(string='Contract file')
	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,
		default=lambda self: self.env.user.company_id.currency_id.id)

	email_from = fields.Char(string='Email', help='These people will receive email', index=True)
	email_cc = fields.Char(string='Watchers Emails', help='These people will be copied in the Email', index=True)

	partner_id = fields.Many2one('res.users', string='Vendors')
	approver_id = fields.Many2one('res.users', string='Approver')

	color = fields.Integer('Color Index', default=0)
	active = fields.Boolean(string='Active', default='True')
	contractor_id = fields.Many2one('res.partner', string='Supplier', domain=[('is_company', '=', True),('supplier', '=', True)])
	alias_id = fields.Many2one('mail.alias', string='Alias', ondelete='restrict', required=True)

	past_deadline = fields.Boolean(string='Past Deadline', default=False, track_visibility='onchange', compute='_check_past_deadline', store=True)
	kolacontract_line_id = fields.One2many('kola.contract.line', 'kolacontract_id', string='Contract line')
	contract_evaluate_id = fields.One2many('kolacontract.evaluate', 'contract_id', string='Contract Evaluation')

	def department_of_loggedin(self):
		employee_id = self.env['hr.employee'].search([('active', '=', True), ('user_id', '=', self.env.uid)])
		if employee_id:
			return employee_id.department_id

	ratings = fields.Selection(AVAILABLE_RATINGS, string='Rating')
	privacy_visibility = fields.Selection([
		('followers', _('On invitation Only')),
		('employees', _('Visible by all employees')),
		('portal', _('Visible by following Customers'))
		],
		string='Privacy',
		default='employees',
		help='')
	image_medium = fields.Binary(
		'Photo',attachment=True,
		help="Small-sized photo of the contracttor/supplier/customer/partner. It is automatically"
		"resized as a 64x64px image, with aspect ratio preserved."
		"Use this field anywhere a small image is required.")

	company_id = fields.Many2one('res.company',
		default=lambda self: self.env['res.company']._company_default_get('kolacontract'))
	count_files = fields.Integer(compute='compute_count_files', string='Document(s)', attachment=True)

	department_id = fields.Many2one('hr.department', string='Department', default=department_of_loggedin)
	comments_admin = fields.Html(string='Comments')
	comments_user_department = fields.Html(string='Comments')
	procurement_minute_extracts = fields.Binary(string='Minute Extracts', attachment=True)
	reason_for_termination = fields.Html(string='Submit Reasons')



	@api.multi
	def terminate_reason_wizard(self, context=None):
		return {
			'name': ('Termination Initiation Reason'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'kolacontract.terminate.reason',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'target': 'new'
		}

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

	@api.onchange('user_id')
	def _onchange_user_id(self):
		self.email_from = self.user_id.email


	@api.onchange('date_from')
	def _onchange_date_from(self):
		for record in self:
			date_from = record.date_from
			date_to = record.date_to
			if date_from:
				record.date_to = ((record.date_from+timedelta(days=(DAYS_IN_A_YEAR))))

	@api.depends('date_from', 'date_to')
	def _compute_duration(self):
		for record in self:
			from_dt = fields.Datetime.from_string(record.date_from)
			to_dt = fields.Datetime.from_string(record.date_to)
			if from_dt and to_dt:
				timedelta = (to_dt - from_dt)
				timedelta = float(math.ceil(timedelta.days))
				record.duration = timedelta

	@api.onchange('duration','date_to')
	def _compute_days_left_to_expire(self):
		for record in self:
			if record.state == 'validate':
				today_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
				todays = fields.Datetime.from_string(today_date)
				to_dt = fields.Datetime.from_string(record.date_to)
				timedelta = (to_dt-todays)
				timedelta = float(math.ceil(timedelta.days))
				record.number_of_days_due = (timedelta-CONTRACT_NOTIFY_THRESH)

	@api.depends('number_of_days_due')
	def _check_past_deadline(self):
		for record in self:
			if record.state == 'validate':
				if record.number_of_days_due > CONTRACT_NOTIFY_THRESH:
					record.past_deadline = False
				else:
					record.past_deadline = True


	@api.onchange('duration')
	def _compute_thresh_hold_for_notification(self):
		for record in self:
			if record.state == 'validate' and record.duration <= CONTRACT_NOTIFY_THRESH:
				return True

	#---------------------------------------------------------------
	#Override ORM methods
	#---------------------------------------------------------------

	# def compute_the_legal_team(self):
	# 	legal_team = self.env['hr.employee'].search([('active', '=', True), ('department_id.name', 'like', 'Legal')])
	# 	for record in legal_team:
	# 		receipients.append(record.work_email)

	@api.model
	def get_email_to(self):
		for record in self:
			if record.state == 'draft':
				user_group = self.env.ref('kolacontract.kola_contract_administration')
				email_list = [
					user.partner_id.email for user in user_group.users if user.partner_id.email 
				]
				return ",".join(email_list)
			#procurement
			elif record.state == 'validate1':
				user_group = self.env.ref('kolacontract.kola_contract_procurement')
				email_list = [
					user.partner_id.email for user in user_group if user.partner_id.email
				]
				return ",".join(email_list)
			#legal
			elif record.state == 'validate2' or record.state == 'validate':
				user_group = self.env.ref('kolacontract.kola_contract_legal') and self.env.ref('kolacontract.kola_contract_administration')
				email_list = [
					user.partner_id.email for user in user_group if user.partner_id.email
				]
				return ",".join(email_list)

			elif record.state == 'validate' or record.state == 'renew' or record.state == 'terminate':
				user_group = self.env.ref('kolacontract.kola_contract_administration') and self.env.ref('kolacontract.kola_contract_legal') and self.env.ref('kolacontract.kola_contract_user')
				email_list = [
					user.partner_id.email for user in user_group if user.partner_id.email
				]
				return ",".join(email_list)
			elif record.state == 'evaluate':
				user_group = self.env.ref('kolacontract.')
				email_list = [

				]
				return ",".join(email_list)

	def send_email_notification(self, obj):
		for record in self:
			if record.state == 'draft':
				template_id = self.env.ref('kolacontract.contract_draft_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate1':
				template_id = self.env.ref('kolacontract.contract_proc_review_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate2':
				template_id = self.env.ref('kolacontract.contract_legal_review_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate3':
				template_id = self.env.ref('kolacontract.contract_signoff_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate':
				template_id = self.env.ref('kolacontract.contract_signed_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'renew':
				template_id = self.env.ref('kolacontract.contract_renew_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'evaluate':
				template_id = self.env.ref('kolacontract.contract_evaluate_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'terminate':
				template_id = self.env.ref('kolacontract.contract_terminate_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

	def _compute_access_url(self):
		super(kolacontract, self)._compute_access_url()
		for contract in self:
			contract.access_url = '/contracts/expire/%s' %(contract.id)

	def _check_state_access_right(self, vals):
		if vals.get('state') and vals['state'] not in ['draft', 'new', 'running', 'finished', 'cancelled'] and not self.env['res.users'].has_group('kolacontract.kola_contract_administration'):
			return False
		return True

	@api.multi
	def add_follower(self, user_id):
		user = self.env['res.users'].browse(user_id)
		if user.user_id:
			self.message_subscribe_users(user_ids=user.user_id.ids)

	@api.model
	def create(self, values):
		user_id = values.get('user_id', False)
		# if not self._check_state_access_right(values):
		# 	raise AccessError(_('You do not have rights!'))
		if values.get('name', 'New') == 'New':
			values['name'] = self.env['ir.sequence'].next_by_code('contract.sequence') or 'New'
		if not values.get('kolacontract_line_id'):
			raise ValidationError(_('Please Specify the service for the Contract Draft'))
			
		if len(values.get('kolacontract_line_id')) > 1:
			raise ValidationError(_('Record limit Exceeded!'))
		contract = super(kolacontract, self).create(values)
		return contract

	@api.multi
	def write(self, values):
		user_id = values.get('user_id', False)
		if 'state' in values:
			previous_state = self.state
			new_state = values.get('state')
			if (new_state in ['draft']) and (not self.env.user.has_group('kolacontract.kola_contract_ict_admin')):
				raise ValidationError(_('You don\'t have the rights to perform this actions \n'
					'Please contact system administrator'))
		for record in self:
			if len(record.kolacontract_line_id) > 1:
				raise ValidationError(_('Record limit Exceeded!'))
		if values.get('procurement_minute_extracts'):
			#trigger email notification ---chair procurement committee
			template_id = self.env.ref('kolacontract.mail_template_for_minute_signup')
			if template_id:
				template_id.send_mail(self.id, force_send=True)
		result = super(kolacontract, self).write(values)
		return result

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('A Contract cannot be duplicated'))

	@api.multi
	def unlink(self):
		return super(kolacontract,self).unlink()

	#--------------------------------------------------------------------
	#Messaging methods
	#--------------------------------------------------------------------

	@api.multi
	def _track_subtype(self, init_values):
		if 'state' in init_values and self.state == 'draft':
			return 'kolacontract.mt_request_drafted'
		if 'state' in init_values and self.state == 'validate1':
			return 'kolacontract.mt_request_validate1'
		if 'state' in init_values and self.state == 'validate':
			return 'kolacontract.mt_request_validate'
		if 'state' in init_values and self.state == 'evaluate':
			return 'kolacontract.mt_request_evaluate'
		if 'state' in init_values and self.state == 'renew':
			return 'kolacontract.mt_request_renew'
		if 'state' in init_values and self.state == 'terminate':
			return 'kolacontract.mt_request_terminated'
		return super(kolacontract, self)._track_subtype(init_values)


	@api.multi
	def _notification_recipients(self, message, groups):
		groups = super(kolacontract, self)._notification_recipients(message, groups)

		self.ensure_one()
		contract_actions = []
		if self.state == 'draft':
			app_action = self._notification_link_helper('controller', controller='/kolacontract/approve')
			contract_actions +=[{'url': app_action, 'title':_('Approve')}]
		if self.state in ['new','finished', 'cancelled']:
			ref_action = self._notification_link_helper('controller', controller='/kolacontract/evaluate')
			contract_actions += [{'url': ref_action, 'title': _('Reject')}]

		if self.state == 'running':
			can_actionc = self._notification_link_helper('controller', controller='/kolacontract/terminate')
			contract_actions += [{'url':can_action, 'title':_('Terminate Contract')}]

		new_group = (
			'kola_contract_user', lambda partner: bool(partner.user_id) and any(user.has_group('kolacontract.kola_contract_user')for user in partner.user_ids),{
				'actions':contract_actions,
			})
		return [new_group] + groups


	@api.multi
	def _message_notification_recipients(self, message, recipients):
		result = super(kolacontract, self)._message_notification_recipients(message, recipients)
		title = _('See Contract Draft') if self.state == 'draft' else _('See Contract')
		for res in result:
			if result[res].get('button_access'):
				result[res]['button_access']['title'] = title
		return result

	#---------------------------------------------------------------------
	#Business methods
	#---------------------------------------------------------------------


	@api.multi
	def _get_attachment_number(self):
		read_group_res = self.env['ir.attachment'].read_group(
			[('res_model', '=', 'kola.contract'), ('res_id', 'in', self.ids)],
			['res_id'], ['res_id'])
		attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
		for record in self:
			record.attachment_number = attach_data.get(record.id, 0)


	@api.multi
	def action_get_attachment_tree_view(self):
		attachment_action = self.env.ref('base.action_attachment')
		action = attachment_action.read()[0]
		action['context'] = {'default_res_model': self._name, 'default_res_id': self.ids[0]}
		action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', self.ids)])
		action['search_view_id'] = (self.env.ref('kolacontract.ir_attachment_view_search_inherit_kola_contract').id, )
		return action


	@api.multi
	def contract_review_by_procurement(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'draft' for contract  in self):
			raise ValidationError(_('Contract must be Reviewed by Administration'))
		self.write({
			'state':'validate1'
			})
		self.send_email_notification(self)
		return reload

	@api.multi
	def contract_share(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('kolacontract', 'contract_share_mail_template')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = {
			'default_model':'kola.contract',
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
	def contract_review_by_legal(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'validate1' for contract in self):
			raise ValidationError(_('Contract must be Reviewed by Procure before Legal Reviews'))
		else:
			self.write({'state': 'validate2'})
			self.send_email_notification(self)
		return reload

	#this sign off is either by the MD/ED with the rights
	@api.multi
	def contract_signoff(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'validate2' for contract in self):
			raise ValidationError(_('Contract must be Reviewed by Legal before Sign Off'))
		else:
			self.write({'state': 'validate3'})
			self.send_email_notification(self)
		return reload

	@api.multi
	def contract_validattion(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'validate3' for contract in self):
			raise ValidationError(_('Contract must signed off before it is set to Running'))
		else:
			self.write({'state':'validate'})
			self.send_email_notification(self)
		return reload


	@api.multi
	def contract_evaluate(self):
		reload = {'type': 'ir.actions.client', 'tag': 'reload'}
		if any(contract.state != 'renew' for contract in self):
			raise ValidationError(_('Contract must be due to expire before it can be moved to evaluation'))
		else:
			self.write({'state': 'evaluate'})
		return reload


	@api.multi
	def contract_termination(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state not in  ['renew'] for contract in self):
			raise ValidationError(_('Contract must be running before it can be terminated'))
		contract_lines = self.env['kola.contract.line'].search([('kolacontract_id.id', '=',self.id)])
		for contract_line in contract_lines:
			rec = self.env['kolacontract.terminate'].sudo().create({
				'contract_id':self.id,
				'date_from':self.date_from,
				'date_to':self.date_to,
				'department_manager': self.department_manager.id,
				'department_id': self.department_id.id,
				'state': 'draft',
			})
			self.env['kolacontract.terminate.line'].sudo().create({
				'kolacontract_terminate_id':rec['id'],
				'product_id':contract_line.product_id.id
			})
		self.write({'active':False})
		self.send_email_notification(self)
		return reload


	@api.multi
	def contract_renewal(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		if any(contract.state not in ['validate',] for contract in self):
			raise ValidationError(_('Contract must be either running or terminated before it can be renewed'))
		self.write({
			'state':'renew'
			})
		self.send_email_notification(self)
		return reload

	@api.multi
	def reset_to_draft(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		self.write({
				'state':'draft'
				})
		self.send_email_notification(self)
		return reload

	@api.multi
	def auto_manage_contract_status(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		contracts = self.env['kola.contract'].search([])
		for contract in contracts:
			if contract.state == 'validate' and contract.number_of_days_due < CONTRACT_NOTIFY_THRESH:
				contract.sudo().write({'state':'renew'})
		self.send_email_notification(self)
		return reload

	@api.multi
	def send_contract_back_astep(self):
		for record in self:
			if record.state == 'validate1':
				record.write({'state': 'draft'})
				self.send_email_notification(record)
			elif record.state == 'validate2':
				record.write({'state': 'validate1'})
				self.send_email_notification(record)
			elif record.state == 'validate3':
				record.write({'state':'validate2'})
				self.send_email_notification(record)

class KolaContractLine(models.Model):
	_name = 'kola.contract.line'
	_description = 'Contract line products'

	#-------------------------------------------
	#DATABASE
	#-------------------------------------------
	name = fields.Char(string='Product Reference')
	kolacontract_id = fields.Many2one('kola.contract', string='Contract Reference', ondelete='cascade')
	currency_id = fields.Many2one(related='kolacontract_id.currency_id', string='Currency', store=True, track_visibility='onchange')
	date_from = fields.Datetime(string='Start Date')
	date_to = fields.Datetime(string='End Date')
	total_qnty = fields.Float(string='Quantity', track_visibility='onchange', store=True)
	unit_cost = fields.Float(string='Unit Cost', track_visibility='onchange')
	total_amount = fields.Float(string='Subtotal Amount', track_visibility='onchange', compute='_compute_total_amount')
	product_id = fields.Many2one('product.product', string='Product')
	product_category = fields.Many2one('product.category', string='Product Category', track_visibility='onchange', store=True)
	description = fields.Char(string='Specifications')


	@api.onchange('unit_cost', 'total_qnty')
	def _compute_total_amount(self):
		self.total_amount = self.total_qnty * self.unit_cost

	#------------------------------------------
	#Override ORM
	#------------------------------------------
	@api.model
	def create(self,values):
		record = super(KolaContractLine, self).create(values)
		return record

	@api.multi
	def write(self,values):
		record = super(KolaContractLine, self).write(values)
		return record

	@api.multi
	def unlink(self):
		record = super(KolaContractLine,self).unlink()

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('Contract line can not be duplicated...!'))


	#------------------------------------------
	#Business  logic
	#------------------------------------------

	@api.onchange('product_id')
	def _onchange_product_id(self):
		all_products = self.env['product.template'].browse(self.product_id.id)
		for product in all_products:
			if self.product_id.id == product.id:
				self.product_category = product.categ_id























