from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError,ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp

from fuzzywuzzy import fuzz

VALID_PERCENTAGE = 95

class KolaRequisition(models.Model):
	_name = 'kola.requisition'
	_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
	_description = 'Purchase Request'
	_mail_post_access = 'read'
	_rec_name = 'name'
	_order = 'create_date desc'

	#-----------------------------------------------------------------------
	#Database
	#-----------------------------------------------------------------------
	@api.depends('requisition_lines_id.actual_amount')
	def _compute_requisition_amount(self):
		for requisition in self:
			sub_total_amount = 0.0
			for item in requisition.requisition_lines_id:
				sub_total_amount +=item.actual_amount
				requisition.update({
									'requisition_amount':requisition.currency_id.round(sub_total_amount)
									})

	def default_department(self):
		employee_id = self.env['hr.employee'].search([('active','=',True), ('user_id', '=', self.env.uid)])
		if employee_id:
			return employee_id.department_id

	def default_employee(self):
		employee_id = self.env['hr.employee'].search([('active', '=', True), ('user_id', '=', self.env.uid)])
		return employee_id

	name = fields.Char(
		string='Request',track_visibility='onchange',default='New', required=True)
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,
		default=lambda self: self.env.user.company_id.currency_id.id)
	reference_number = fields.Char(string='Reference Number')
	employee_id = fields.Many2one('hr.employee',string='Employee',track_visibility='onchange',
		default=default_employee)

	company_id = fields.Many2one('res.company',
		default=lambda self: self.env['res.company']._company_default_get('kolarequisition'))

	def department_manager(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if employee_id:
			return employee_id.department_id.manager_id

	department_manager_id = fields.Many2one('hr.employee',string='Deprtment Manager',
		default=department_manager)
	user_id = fields.Many2one('res.users',string='Responsible',default=lambda self: self.env.user.id,
		track_visibility='onchange')
	approver_id = fields.Many2one('res.users',string='Approver',
		track_visibility='onchange')
	partner_id = fields.Many2one('res.partner',string='Partner',
		track_visibility='onchange')
	department_id = fields.Many2one('hr.department',string='User Deprtment',default=default_department,
		store=True)
	requisition_lines_id = fields.One2many('kola.requisition.lines','kola_requisition_id',string='Product Requested',
		copy=True)

	requisition_date = fields.Datetime(string='Request Date',
		default=datetime.today())
	received_date = fields.Datetime(string='Recieved Date',
		readonly=True)
	requisition_deadline = fields.Datetime(string='Request Deadline')
	vendor_id = fields.Many2one('res.partner',string='vendor',domain=[('is_company', '=', True),
		('supplier', '=',True)])
	po_name = fields.Char(string='PO Reference',default='New')
	internal_picking = fields.Boolean(string='Internal Picking',
		default=True)
	purchase_order = fields.Boolean(string='Purchase Order',
		default=False)
	remarks = fields.Text(string='Remarks')
	requisition_amount = fields.Float(string='Total Amount',compute='_compute_requisition_amount',
		store=True,)
	is_service = fields.Boolean(string='Request for Service', default=False, compute='_onchange_request_line', store=True,)

	@api.depends('requisition_lines_id.product_id')
	def _onchange_request_line(self):
		product_services = self.env['product.template'].search([('type', '=', 'service')])
		service_ids = []
		for service in product_services:
			service_ids.append(service.id)
		print(service_ids)
		for record in self:
			for product in record.requisition_lines_id:
				if product.product_id.id in service_ids:
					record.is_service = True
				else:
					record.is_service = False

	def get_year(self):
		return str(datetime.now().year)
	year = fields.Char(string='Current Year', default=get_year)

	state = fields.Selection([
		('draft', 'New Request'),
		('validate1', 'For Department Approval'),
		('validate2','Admin Approval'),
		('validate3', 'Review & Approval'),
		('validate', 'Approved Requests'),
		('order', 'RFQs'),
		('reject', 'Cancelled')
		], default='draft', group_expand='_expand_states', help='Status of purchase request',
		track_visibility='onchange', string='Status')

	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	email_from = fields.Char(string='Email',help='These people will receive email',
		index=True)

	email_cc = fields.Char(string='Watchers Emails',
		help='These people will be copied in the Email',index=True)

	image_small = fields.Binary(
		'Photo',attachment=True,
		help="Small-sized photo of the contracttor/supplier/customer/partner. It is automatically"
		"resized as a 64x64px image, with aspect ratio preserved."
		"Use this field anywhere a small image is required.")
	active = fields.Boolean(string='Active', default=True)
	color = fields.Integer(string='Index', default=0)

	doc_attachment = fields.Many2many('ir.attachment', string='Attach Files', attachment=True)
	docs_count = fields.Integer(string='Files', compute='_compute_docs')

	@api.depends('doc_attachment')
	def _compute_docs(self):
		for record in self:
			record.docs_count = len(record.doc_attachment)


	@api.onchange('user_id')
	def _onchange_user_id(self):
		self.email_from = self.user_id.email

	def _compute_access_url(self):
		super(KolaRequisition, self)._compute_access_url()
		for request in self:
			request.access_url = '/my/purchaserequest/%s' %(request.id)
	#------------------------------------------------------------------------
	#Override ORM methods
	#------------------------------------------------------------------------

	def _check_state_access_right(self, vals):
		if vals.get('state') and vals['state'] not in ['draft', 'request', 'supervise', 'validate', 'reject'] and not self.env['res.users'].has_group('kolarequisition.kola_requisition_administration'):
			return False
		return True

	def send_email_notification(self, obj):
		for record in self:
			if record.state == 'draft':
				template_id = self.env.ref('kolarequisition.pr_draft_mail_template')
				if template_id:
					self.env['mail.tempalate'].browse(template_id.id).send_mail(obj.id, force_send=True)
			if record.state == 'validate1':
				template_id = self.env.ref('kolarequisition.pr_dept_approval_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)
			if record.state == 'validate2':
				template_id = self.env.ref('kolarequisition.pr_admin_approval_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)
			if record.state == 'validate3':
				template_id = self.env.ref('kolarequisition.pr_proc_review_approval_mail_template')
				if template_id:
					self.env['mail.tempalate'].browse(template_id.id).send_mail(obj.id, force_send=True)
			if record.state == 'validate':
				template_id = self.env.ref('kolarequisition.pr_approved_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)
			if record.state == 'order':
				template_id = self.env.ref('kolarequisition.pr_rfq_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)
			if record.state == 'reject':
				template_id = self.env.ref('kolarequisition.pr_rejected_mail_template')
				if template_id:
					self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)


	@api.multi
	def add_followers(self, employee_id):
		employee = self.env['hr.employee'].browse(employee_id)
		if employee.user_id:
			self.message_subscribe(user_ids=employee.user_id.ids)

	@api.model
	def create(self, values):
		employee_id = values.get('employee_id', False)
		if values.get('name', 'New') == 'New':
			values['name'] = self.env['ir.sequence'].next_by_code('pr.sequence') or 'New'
		purchase_request = super(KolaRequisition, self).create(values)
		# purchase_request.email_with_template()
		return purchase_request

	@api.multi
	def write(self, values):
		employee_id =values.get('employee_id', False)
		return super(KolaRequisition, self).write(values)

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('A Purchase Requests can not be duplicated'))

	@api.multi
	def unlink(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		for kola_line_request in self.filtered(lambda kola_line_request: kola_line_request.state not in ['reject', 'draft']):
			raise UserError(_('You can not delete Purchase Request which is in a %s state') % (kola_line_request.state))
		return super(KolaRequisition, self).unlink()

	#---------------------------------------------------------------------
	#Business methods
	#---------------------------------------------------------------------
	def common_members(self, list1, list2):
		intersected_list = [value for value in list1 if value in list2]
		return intersected_list

	def list_differences(self, list1, list2):
		differences_in_list = [value for value in list1 if value not in list2]
		return differences_in_list

	def _update_pr_based_on_budget(self):
		all_pr_item_ids = []
		all_budget_item_ids = []
		all_purchase_requisition_items = self.env['kola.requisition.lines'].search([('kola_requisition_id', '=', self.id)])
		for item in all_purchase_requisition_items:
			all_pr_item_ids.append(item.product_id.id)
		all_items_in_budget = self.env['bm.budget.lines'].search([('budget_management_id.department_id.id', '=', self.department_id.id),('product_id', 'in', all_pr_item_ids)])

		for budget_item in all_items_in_budget:
			all_budget_item_ids.append(budget_item.product_id.id)
			for each in all_purchase_requisition_items:
				if each.product_id.id == budget_item.product_id.id:
					each.sudo().write({
						'status':'true',
						'unit_cost':budget_item.unit_cost,
						'actual_amount':(budget_item.unit_cost*each.total_qty)
						})

	@api.constrains('requisition_lines_id.purchase_item_state')
	def _check_purchaseline_approvals(self):
		for purchase_line in self.requisition_lines_id:
			if purchase_line.purchase_item_state != 'approved' or purchase_line.purchase_item_state != 'rejected':
				raise UserError(_('Check Purchase line Items \n'+
								  'Please ensure all purchase line items have been approved...'))

	@api.multi
	def department_approval(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(purchase_request.state != 'draft' for purchase_request in self):
			raise ValidationError(_('Purchase Request must be in draft before it can be approved by the department'))
		self.write({'state': 'validate1'})
		self._update_pr_based_on_budget()

	@api.multi
	def admin_approval(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(purchase_request.state != 'validate1' for purchase_request in self):
			raise ValidationError(_('Purchase Request must approved by department before approval by administration'))
		self.write({'state':'validate2'})
		self._update_pr_based_on_budget()

	@api.multi
	def finance_approval(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(purchase_request.state != 'validate2' for purchase_request in self):
			raise ValidationError(_('Purchase Request must be approved by administration before Finance Approval'))
		self.write({'state':'validate3'})
		self._update_pr_based_on_budget()

	@api.multi
	def procurement_approval(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(purchase_request.state != 'validate3' for purchase_request in self):
			raise ValidationError(_('Purchase Request must be approved by administration before Procurement Approval'))
		self.write({'state':'validate'})

	@api.multi
	def reject_request(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		self.write({'state': 'reject'})

	@api.multi
	def reset_to_draft(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		self.write({'state': 'draft'})

	def _check_state_administration_right(self, values):
		if values.get('state') and values['state']  in ['validate'] and not self.env['res.users'].has_group('kolarequisition.kola_requisition_administration'):
			return False
		return True

	@api.multi
	def generate_rfq(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		self.write({'state':'order'})

	@api.multi
	def validate_request(self, values):
		partner_id = self.vendor_id.id
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if not self._check_state_access_right(values):
			raise AccessError(_('You have no access right to this document \n'+
				' Please Contact the System Administrator'))
		else:
			if self.partner_id == '':
				raise UserError(_('Vendor Records are Mandatory'+
								'Please fill the Vendor Details before generating an RFQ...'))
			#create rfq
			elif self.is_service == False:
				self.write({'state':'order'})
				purchase_requisition_items = self.env['kola.requisition.lines'].search([('kola_requisition_id', '=', self.id)])
				all_purchase_orders_items = self.env['purchase.order'].search([('name', '=', self.name)])
				if len(all_purchase_orders_items) == 0:
					self.env['purchase.order'].sudo().create({
						'name':self.name,
						'order_date':datetime.today(),
						'date_planned':datetime.today(),
						'partner_id':partner_id,
						'create_date':datetime.today(),
						'write_date':datetime.today(),
						'create_uid':self.employee_id,
						'request_reference':self.id
					})
					current_purchase = self.env['purchase.order'].search([('request_reference', '=', self.id)])
					purchase_request_line = self.env['kola.requisition.lines'].search([('kola_requisition_id', '=', self.id)])
					for purchase in current_purchase:
						for purchase_item in purchase_request_line:
							print('Products'+str(purchase_item.product_id.id))
							print('Purchase Order Reference '+str(purchase.name))
							self.env['purchase.order.line'].browse(purchase_item.id).create(
								{
									'product_id':purchase_item.product_id.id,
									'name':purchase_item.description,
									'date_planned':datetime.today(),
									'product_qty':purchase_item.total_qty,
									'price_unit':purchase_item.unit_cost,
									'price_subtotal':purchase_item.actual_amount,
									'product_uom':purchase_item.product_uom_id.id,
									'order_id':purchase.id
								}
							)
				else:
					raise UserError(_('Request For Quotation (RFQ) Already Exists \n'+
						'Please Contact System Administrator'))

	@api.multi
	def generate_contract_draft(self):
		partner_id = self.vendor_id.id
		if self.partner_id == '':
			raise UserError(_('Vendor Records are Mandatory'+
						'Please fill the Vendor Details before generating an RFQ...'))
		if self.is_service == True:
			self.write({'active':False})
			self.env['kola.contract'].sudo().create({
					'name':self.name,
					'department_id':self.department_id.id,
					'contractor_id':self.vendor_id.id,
					'state':'draft',
					'active':True
				})
			all_contracts = self.env['kola.contract'].search([('name', '=', self.name)], limit=1)
			purchase_request_line = self.env['kola.requisition.lines'].search([('kola_requisition_id', '=', self.id)])
			for contract in all_contracts:
				for request in purchase_request_line:
					self.env['kola.contract.line'].browse().create({
						'product_id':request.product_id.id,
						'total_qnty':request.total_qty,
						'unit_cost':request.unit_cost,
						'total_amount':request.actual_amount,
						'kolacontract_id':contract.id
					})

	@api.multi
	def print_purchase_request(self):
		return self.env.ref('kolarequisition.report_purchase_request').report_action(self)
	@api.multi
	def action_pr_send(self):
		'''
		This window opens a window to compose an email, with pr tempalate message loaded by default
		'''
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('kolarequisition', 'kola_requisition_email_template')[1]

		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = {
			'default_model':'kola.requisition',
			'default_res_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_so_as_sent': True,
			'force_email': True
		}

		return {
			'type':'ir.actions.act_window',
			'view_type':'form',
			'view_mode':'form',
			'res_model':'mail.compose.message',
			'views':[(compose_form_id, 'form')],
			'view_id':compose_form_id,
			'target':'new',
			'context':ctx,
		}

	@api.multi
	def _message_notification_recipients(self, message, recipients):
		pass

	#---------------------------------------------------------------------
	#Messaging methods
	#---------------------------------------------------------------------

	@api.multi
	def _track_subtype(self, init_values):
		if 'state' in init_values and self.state == 'draft':
			return 'kolarequisition.mt_request_drafted'
		if 'state' in init_values and self.state == 'validate1':
			return 'kolarequisition.mt_request_validate1'
		if 'state' in init_values and self.state == 'validate2':
			return 'kolarequisition.mt_request_validate2'
		if 'state' in init_values and self.state == 'validate3':
			return 'kolarequisition.mt_request_validate3'
		if 'state' in init_values and self.state == 'validate':
			return 'kolarequisition.mt_request_validate'
		if 'state' in init_values and self.state == 'reject':
			return 'kolarequisition.mt_request_rejected'
		return super(KolaRequisition, self)._track_subtype(init_values)


class kolaRequisitionLine(models.Model):
	_name = 'kola.requisition.lines'
	_description = 'Request lines'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'kola_requisition_id'
	_order = 'kola_requisition_id desc'

	#-----------------------------------------------------
	#DATABASE
	#-----------------------------------------------------

	name = fields.Char(string='Reference')
	kola_requisition_id = fields.Many2one('kola.requisition','Request Reference', ondelete='cascade')
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,
		default=lambda self: self.env.user.company_id.currency_id.id)
	paid_date = fields.Datetime(string='Paid Date')
	total_qty = fields.Float(string='Quantity',track_visibility='onchange',
		store=True)
	unit_cost = fields.Float(string='Unit Cost')
	product_id = fields.Many2one(comodel_name='product.product',string='Product',
		required=True)

	actual_amount = fields.Float(string='Subtotal Cost',track_visibility='onchange',
		store=True)
	product_category = fields.Many2one('product.category',string='Category',track_visibility="onchange",
		store=True)
	description = fields.Char(string='Specifications')
	status = fields.Selection(
		[
			('draft', 'Approve'),
			('validate', 'Approved'),
			('reject', 'Rejected')
		],
		string='Status', default='draft'
		)

	state = fields.Selection(related='kola_requisition_id.state',string='State')

	purchase_item_state = fields.Selection(
		[
			('draft', 'To Approve'),
			('approved', 'Approved'),
			('rejected', 'Rejected')
		],string='Item Status', default='draft')

	product_uom_id = fields.Many2one('uom.uom',related='product_id.uom_id',
		readonly=True)
	requisition_practical_cost = fields.Float(string='Total Amount',digits = 0,compute='_compute_total_amount',
		track_visibility='onchange',store=True)
	budget_balance = fields.Float(string='Budget Balance', track_visibility='onchange')

	product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', string='Product Template')

	purchase_cat_product = fields.Char(string='Budget Category',track_visibility='onchange', store=True)


	#--------------------------------------------------------
	#Override ORM
	#--------------------------------------------------------

	@api.model
	def create(self,values):
		rec = super(kolaRequisitionLine, self).create(values)
		return rec

	@api.multi
	def write(self, values):
		rec = super(kolaRequisitionLine, self).write(values)
		return rec

	@api.multi
	def unlink(self):
		rec = super(kolaRequisitionLine, self).unlink()
		return rec

	def copy_data(self, context=None):
		raise UserError(_('Request lines can not be duplicated'))


	#-----------------------------------------------------------------
	#Business logic
	#-----------------------------------------------------------------
	@api.one
	def _search_request_budget(self, product_category, product_id):
		amount_left_on_budget = 0.0
		search_product_budget = self.env['budget.management'].search([('department_id.name', 'ilike', product_category),('active', '=', True)])
		for budget in search_product_budget:
			print(budget.department_id.name)
			search_product_budget_line = self.env['bm.budget.lines'].search([('budget_management_id', '=', budget.id)])

			for product in search_product_budget_line:
				if product.product_id.id == self.product_id.id:
					amount_left_on_budget+=product.practical_amount
		self.update({
				'budget_balance':amount_left_on_budget
			})

	@api.onchange('product_id')
	def _onchange_product_id(self):
		all_products = self.env['product.template'].browse(self.product_id.id)
		for product in all_products:
			self.purchase_cat_product = product.product_budget_category
			if fuzz.partial_ratio(str(product.product_budget_category).lower(), 'ict') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'business') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'finance') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'credit') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'audit') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'compliance') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'operations') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'human') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'administration') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'risk') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			elif fuzz.partial_ratio(str(product.product_budget_category).lower(), 'legal') >= VALID_PERCENTAGE:
				self._search_request_budget(product.product_budget_category, product.id)

			else:
				print('Product not configured to any budget category')


	@api.onchange('total_qty', 'unit_cost')
	def _actual_amount(self):
		self.actual_amount = self.total_qty*self.unit_cost


	@api.multi
	def approve_purchase_line(self):
		# if self.kola_requisition_id.department_manager_id:
		self.write(
					{
						'status':'validate',
						'purchase_item_state':'approved',
					}
				)
		# else:
		# 	raise UserError(_('You don\'t have sufficient rights to approve purchase line \n'+
		# 						'Please contact system Administrator'))
	@api.multi
	def reject_purchase_line(self):
		# if self.kola_requisition_id.department_manager_id:
		self.write(
				{
					'status':'reject',
					'purchase_item_state':'rejected'
				}
			)
		# else:
		# 	raise UserError(_('You don\'t have sufficient rights to reject purchase line \n'+
		# 						'Please contact your system Administrator'))







