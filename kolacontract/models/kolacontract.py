# -*- coding: utf-8 -*-

from odoo import models, fields, api,_,tools,SUPERUSER_ID
from datetime import datetime,timedelta,date
from odoo.exceptions import UserError, AccessError, ValidationError
import math
from odoo.http import request

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
		('validate1', 'Review By Admin'),
		('validate2', 'Review By Procurement'),
		('validate', 'Running Contracts'),
		('renew', 'Contract Due To Expire'),
		('reject', 'Rejected Contracts'),
		('terminate', 'Terminated Contracts')]
		, string='Status', group_expand='_expand_states',
		track_visibility='onchange', help='Status of the contract',
		default='draft')

	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	name  = fields.Char(string='Contract Reference', default='New', required=True, track_visibility='onchange')
	product_id = fields.Many2one('product.product', string='Service', track_visibility='onchange')
	date_from = fields.Datetime(string='Start Date', track_visibility='onchange')
	date_to = fields.Datetime(string='End Date', track_visibility='onchange')
	duration = fields.Float(string='Duration of Contract', compute='_compute_duration', track_visibility='onchange',store=True)
	user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user.id)
	amount = fields.Float(string='Amount', compute='_compute_contract_total')
	number_of_days_due = fields.Float(string='Number of Days Left', track_visibility='onchange', compute='_compute_days_left_to_expire', store=True,)

	contract_doc = fields.Many2many('ir.attachment',string='Attach a file(s)')
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
	department_id = fields.Many2one('hr.department', string='Department')


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

	@api.depends('duration','date_to')
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

	def compute_the_legal_team(self):
		legal_team = self.env['hr.employee'].search([('active', '=', True), ('department_id.name', 'like', 'Legal')])
		for record in legal_team:
			receipients.append(record.work_email)

	#check notification receipients
	def compute_notification_receipients(self):
		for record in self:
			if record.state == 'draft':
				administration = self.env['hr.department'].search([('name', 'like', 'Administration')])
				user_department = self.env['hr.department'].browse(record.department_id)
				for record in administration:
					receipients.append(record.manager_id.work_email)
				for record in user_department:
					receipients.append(record.manager_id.work_email)

			elif record.state == 'validate1':
				pass
			elif record.state == 'validate':
				pass
			elif record.state == 'renew':
				pass
			elif record.state == 'reject':
				pass
			elif record.state == 'terminate':
				pass

	def send_email_notification(self, obj):
		for record in self:
			if record.state == 'draft':
				template_id = self.env.ref('kolacontract.contract_draft_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate1':
				template_id = self.env.ref('kolacontract.contract_review_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate2':
				template_id = self.env.ref('kolacontract.contract_review_procurement_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'validate':
				template_id = self.env.ref('kolacontract.contract_running_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'renew':
				template_id = self.env.ref('kolacontract.contract_expire_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

			elif record.state == 'reject':
				template_id = self.env.ref('kolacontract.contract_expire_mail_template')
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
		contract = super(kolacontract, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(values)
		self.send_email_notification(contract)
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
		result = super(kolacontract, self).write(values)
		#self.add_follower(user_id)
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
		if 'state' in init_values and self.state == 'reject':
			return 'kolacontract.mt_request_reject'
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
			ref_action = self._notification_link_helper('controller', controller='/kolacontract/reject')
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
	def contract_expiry_notification(self):
		su_id = self.env['res.partner'].browse(SUPERUSER_ID)
		recipients = ['herbert.ichama@financetrust.co.ug']
		all_contracts = self.env['kola.contract'].search([])
		for record in all_contracts:
			if record.state == 'validate':
				if self._compute_thresh_hold_for_notification():
					template_obj = self.env['mail.mail']
					template_data = {
					'subject': 'Contracts Due to Expire '+ str(today_date),
					'body_html': """<p>Dear Team</p>
					<p>Contract by Company """+str(record.contractor_id.name)+"""</p>
					<p>has """+str(record.duration)+" days to Expire"+"""</p>
					<p>Best Regards</p>"""+"<p>Finance Trust Bank</p>",
					'email_from': su_id.email,
					'email_to': ", ".join(recipients)}
					template_id = template_obj.create(template_data)
					template_id.sudo().send()

	@api.multi
	def contract_review(self):
		if any(contract.state != 'draft' for contract  in self):
			raise ValidationError(_('Contract must be drafted first before Review & Evaluation'))
		self.write({
			'state':'validate1'
			})
		self.send_email_notification(self)

	@api.multi
	def contract_approval(self, stage_id):
		if any(contract.state != 'validate1' for contract in self):
			raise ValidationError(_('Contract must be Negotiated first before Approval is done'))
		self.write({
			'state':'validate'
			})
		self.send_email_notification(self)

	@api.multi
	def contract_termination(self):
		if any(contract.state != 'validate' for contract in self):
			raise ValidationError(_('Contract must be running before it can be terminated'))
		contract_lines = self.env['kola.contract.line'].search([('kolacontract_id.id', '=',self.id)])
		for contract_line in contract_lines:
			rec = self.env['kolacontract.terminate'].sudo().create({
															'contract_id':self.id,
															'date_from':self.date_from,
															'date_to':self.date_to,
															})
			self.env['kolacontract.terminate.line'].sudo().create({
																'kolacontract_terminate_id':rec['id'],
																'product_id':contract_line.product_id.id
																})
		self.write({
			'active':False
			})
		self.send_email_notification(self)


	@api.multi
	def contract_renewal(self):
		if any(contract.state not in ['running','terminate'] for contract in self):
			raise ValidationError(_('Contract must be either running or terminated before it can be renewed'))
		self.write({
			'state':'renew'
			})
		self.send_email_notification(self)

	@api.multi
	def contract_rejection(self):
		if any(contract.state not in ['draft', 'validate1'] for contract in self):
			raise ValidationError(_('Contract must be either drafted, Reviewed or Negotiated before it can be rejected'))
		self.write({
				'state':'reject'
				})
		self.send_email_notification(self)

	@api.multi
	def reset_to_draft(self):
		self.write({
				'state':'draft'
				})
		self.send_email_notification(self)

	@api.multi
	def auto_manage_contract_status(self):
		contracts = self.env['kola.contract'].search([])
		for contract in contracts:
			if contract.state == 'validate' and contract.number_of_days_due < CONTRACT_NOTIFY_THRESH:
				contract.sudo().write({'state':'renew'})

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























