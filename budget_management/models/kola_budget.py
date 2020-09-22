from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _,exceptions
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError,ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from werkzeug import url_encode

from fuzzywuzzy import fuzz

VALID_PERCENTAGE = 95

class BudgetManagement(models.Model):
	_name = 'budget.management'
	_description = 'Budget'
	_rec_name = 'name'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	#-------------------------------------------------
	#DATABASE
	#-------------------------------------------------

	@api.depends('bm_budget_lines_id.practical_amount')
	def _compute_budget_total(self):
		for budget in self:
			subtotal_amount = 0.0
			for item in budget.bm_budget_lines_id:
				subtotal_amount += item.practical_amount
				budget.update({
					'total_budget_cost':budget.currency_id.round(subtotal_amount)
					})

	@api.depends('bm_budget_lines_id.practical_amount')
	def _compute_used_budget_amount(self):
		pass

	def default_department(self):
		employee_id = self.env['hr.employee'].search([('active','=',True), ('user_id', '=', self.env.uid)])
		if employee_id:
			return employee_id.department_id

	def get_year(self):
		return str(datetime.now().year)

	def default_employee(self):
		employee_id = self.env['hr.employee'].search([('active', '=', True), ('user_id', '=', self.env.uid)])
		return employee_id

	def department_manager(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if employee_id:
			manager_id = employee_id.department_id.manager_id.id
			related_user_id = self.env['hr.employee'].search([('user_id', '=', manager_id)], limit=1)
			for user in related_user_id:
				return user.user_id

	name = fields.Char(string='Reference', default='New', required=True, track_visibility='onchange')
	employee_id = fields.Many2one('hr.employee', default=default_employee)
	creating_user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, readonly=True, track_visibility='onchange')
	budget_config_id = fields.Many2one('budget.config', string='Budget Type', track_visibility='onchange')
	bm_budget_lines_id = fields.One2many('bm.budget.lines', 'budget_management_id', 'Budget line', required=True)
	department_id = fields.Many2one('hr.department', string='Department',default=default_department, track_visibility='onchange')
	department_manager_id = fields.Many2one('hr.employee',default=department_manager, string='Manager')

	state = fields.Selection([
		('draft', 'To Submit'),
		('propose', 'Budget Proposal'),
		('review1', 'Budget Review'),
		('consolidate', 'Consolidation'),
		('review', 'Management Review'),
		('validate', 'Approved Budget'),
		('reject', 'Rejected Budget'),
		('reset', 'Reset To Draft')
		],'Status', default='draft', index=True, readonly=False, copy=False, track_visibility='always',
		group_expand='_expand_states',
		help='Status of Budgets',)

	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	date_from = fields.Date('Period', required=True, state={'done': [('readonly', True)]})
	date_to = fields.Date('End Date', required=True, state={'done': [('readonly', True)]})
	comments = fields.Html(string='Comments')
	year = fields.Char(string='Current Year', default=get_year)
	total_budget_cost = fields.Float(string='Total Amount', compute="_compute_budget_total", store=True)

	user_id = fields.Many2one('res.users', 'logged in user', default=lambda self: self.env.user)
	total_used_budget = fields.Float(string='Achievement', store=True)
	total_actual_amount = fields.Float(string='Actual Amount', compute='', store=True)

	company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,
		default=lambda self: self.env.user.company_id.currency_id.id)
	color = fields.Integer(string='Color Index', default=0)
	active = fields.Boolean(string='Active', default=True)
	partner_id = fields.Many2one('res.partner',string='Partner',track_visibility='onchange')

	def _compute_access_url(self):
		action = self.env.ref('budget_management.action_budget_management').id
		form_view_id = self.env.ref('budget_management.budget_management_form').id
		for record in self:
			url_params = {
				'view_type': 'form',
				'model': 'budget_management.budget_management',
				'id':record.id,
				'active_id': record.id,
				'view_id': form_view_id,
				'action': action
			}

			url = '/web?#%s' % url_encode(url_params)
			record.budget_url = url

	budget_url = fields.Char(string='Budget Url', compute='_compute_access_url')

	total_budget_line_requests = fields.Integer(
		compute='_compute_budget_line_requests',
		string='Total Requests')

	total_budget_line_requests_approved = fields.Integer(
		compute='_compute_budget_line_request_approved',
		string='Approved Requests')

	total_budget_line_requests_rejected = fields.Integer(
		compute='_compute_budget_line_request_rejected',
		string='Rejected Requests')

	#--------------------------------------------------------------------------------
	#Overried ORM methods
	#--------------------------------------------------------------------------------

	@api.multi
	def mail_notification(self, obj):
		if self.state == 'draft':
			template_id = self.env.ref('budget_management.budget_draft_mail_template')
			if template_id:
				self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

		elif self.state == 'propose':
			template_id = self.env.ref('budget_management.budget_proposal_mail_template')
			if template_id:
				self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

		elif self.state == 'review1':
			template_id = self.env.ref('budget_management.budget_review1_mail_template')
			if template_id:
				self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

		elif self.state == 'consolidate':
			template_id = self.env.ref('budget_management.budget_consolidate_mail_template')
			if template_id:
				self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

		elif self.state == 'review':
			template_id = self.env.ref('budget_management.budget_review_mail_template')
			if template_id:
				self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

		elif self.state == 'validate':
			template_id = self.env.ref('budget_management.budget_validate_mail_template')
			if template_id:
				self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

		elif self.state == 'reject':
			template_id = self.env.ref('budget_management.budget_reject_mail_template')
			if template_id:
				self.env['mail.template'].browse(template_id.id).send_mail(obj.id, force_send=True)

	@api.multi
	@api.depends('name','department_id')
	def name_get(self):
		result = []
		for bgt in self:
			name = bgt.name
			if bgt.department_id:
				name += ' (' + str(bgt.department_id.name) + ')'
			result.append((bgt.id, name))
			lang = self.env.context.get('lang')
		return result

	@api.multi
	def add_followers(self):
		partner_ids = []
		if self.employee_id:
			department_id = self.employee_id.department_id
			employee_ids = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)])
			for self.employee_id in employee_ids:
				self.message_subscribe(partner_ids=self.employee_id.user_id.partner_id.ids)

	@api.model
	def create(self, values):
		employee_id = values.get('employee_id', False)
		if values.get('name', 'New') == 'New':
			values['name'] = self.env['ir.sequence'].next_by_code('budget.sequence') or 'New'
		rec = super(BudgetManagement, self).create(values)
		#rec.add_followers()
		#self.mail_notification()
		return rec

	@api.multi

	def write(self, values):
		employee_id = values.get('employee_id', False)
		rec = super(BudgetManagement, self).write(values)
		return rec

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('Budget cannot be duplicated'))


	@api.multi
	def unlink(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(budget.state not in ['draft','reject'] for budget in self):
			raise UserError(_('Budget cannot be deleted while not in draft/reject state'))
		rec = super(BudgetManagement, self).unlink()
		return rec

	#--------------------------------------------------------------------------
	#Business methods
	#--------------------------------------------------------------------------

	@api.multi
	def _check_approval_update(self, state):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		for rec in self:
			if rec.state == 'draft':
				if rec.employee_id == current_employee and rec.department_manager_id == self.env.uid:
					continue
				else:
					raise UserError(_('You do not have rights to modify this record \n'+
										'Pleas contact system Administrator'))
			elif rec.state == 'propose':
				if current_employee.has_group('budget_management.bm_finance'):
					continue
				else:
					raise UserError(_('You do not have rights to modify this record \n'+
										'Please contact system Administrator'))
			elif rec.state == 'review1':
				if current_employee.has_group('budget_management.bm_finance'):
					continue
				else:
					raise UserError(_('You do not have rights to modify this record \n'+
										'please contact system Administrator'))
			elif rec.state == 'consolidate':
				if current_employee.has_group('budget_management.bm_finance'):
					continue
				else:
					raise UserError(_('You do not have rights to modify this record \n'+
										'please contact system Administrator'))
			elif rec.state == 'review':
				if current_employee.has_group('budget_management.bm_approval_committee'):
					continue
				else:
					raise UserError(_('You do not have rights to modify this record \n'+
										'please contact system Administrator'))
			elif rec.state == 'validate':
				if current_employee.has_group('budget_management.bm_approval_committee'):
					continue
				else:
					raise UserError(_('You do not have rights to modify this record \n'+
										'please contact system Administrator'))

	@api.multi
	def _get_approvers_to_notify(self):
		if self.state == 'propose':
			user_group = self.env.ref('budget_management.bm_finance')
			email_list = [
				user.partner_id.email for user in user_group.users if user.partner_id
			]
			print(email_list)
			return ",".join(email_list)

		elif self.state == 'review1':
			user_group = self.env.ref('budget_management.bm_finance')
			email_list = [
				user.partner_id.email for user in user_group.users if user.partner_id
			]
			print(email_list)
			return ",".join(email_list)

		elif self.state == 'consolidate':
			user_group = self.env.ref('budget_management.bm_finance')
			email_list = [
				user.partner_id.email for user in user_group.users if user.partner_id
			]
			print(email_list)
			return ",".join(email_list)

		elif self.state == 'review':
			user_group = self.env.ref('budget_management.bm_approval_committee')
			email_list = [
				user.partner_id.email for user in user_group.users if user.partner_id
			]
			print(email_list)
			return ",".join(email_list)

		elif self.state == 'validate':
			user_group = self.env.ref('budget_management.bm_approval_committee')
			email_list = [
				user.partner_id.email for user in user_group.users if user.partner_id
			]
			print(email_list)
			return ",".join(email_list)

	@api.constrains('bm_budget_lines_id.budget_item_state')
	def _check_budgetline_approvals(self):
		pass
		# for budget_line in self.bm_budget_lines_id:
		# 	if budget_line.budget_item_state != 'approved' or budget_line.budget_item_state != 'rejected':
		# 		raise UserError(_('Check Budgetline Items \n'+
		# 						'Please ensure that budget line items have all been approved'))


	@api.multi
	def action_propose_draft(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(budget.state != 'draft' for budget in self):
			raise UserError(_('Budget must be drafted before it can be proposed for review & approval'))
		#self._check_budgetline_approvals()
		self.write({'state':'propose'})
		for record in self:
			self.mail_notification(self)
		return reload

	@api.multi
	def action_review_proposal(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(budget.state != 'propose' for budget in self):
			raise UserError(_('Budget must be proposed before it can be reviewed by finance team'))
		#self._check_budgetline_approvals()
		self.write({'state':'review1'})
		self.mail_notification(self)
		return reload

	@api.multi
	def action_reject_proposal(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		self.write({'state':'draft'})
		self.mail_notification(self)
		return reload

	@api.multi
	def action_consolidate_proposal(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(budget.state != 'review1' for budget in self):
			raise UserError(_('Budget must be reviewed by finance team before it can be consolidated'))
		#self._check_budgetline_approvals()
		self.write({'state': 'consolidate'})
		self.mail_notification(self)
		return reload


	@api.multi
	def action_reject_consolidation(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		self.write({'state': 'draft'})
		self.mail_notification(self)
		return reload

	@api.multi
	def action_submit_for_mgt_review(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(budget.state != 'consolidate' for budget  in self):
			raise UserError(_('Budget must proposed before it can be reviewed by finance'))
		#self._check_budgetline_approvals()
		self.write({'state': 'review'})
		self.mail_notification(self)
		return reload

	@api.multi
	def action_mgt_approve(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(budget.state != 'review' for budget in self):
			raise UserError(_('Budget must be consolidated by finance team before it can be reviewed by administration'))
		#self._check_budgetline_approvals()
		self.write({'state':'validate'})
		self.mail_notification()
		return reload

	@api.multi
	def action_mgt_reject(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if any(budget.state != 'review' for budget in self):
			raise UserError(_('Budget must be reviews by management before it can be rejected by administration'))
		#self._check_budgetline_approvals()
		self.write({'state': 'reject'})
		self.mail_notification(self)
		return reload

	@api.multi
	def print_budget(self):
		return self.env.ref('budget_management.action_report_annual_budgets').report_action(self)

	@api.multi
	def action_budget_send(self):
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id  = ir_model_data.get_object_reference('budget_management', 'budget_mail_template')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = {
			'default_model':'budget.management',
			'default_res_id':self.ids[0],
			'default_use_template':bool(template_id),
			'default_template_id':template_id,
			'mark_so_as_sent':True,
			'force_email':True
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
	#-----------------------------------------------------------------------
	#Messagging methods
	#-----------------------------------------------------------------------

	@api.multi
	def _track_subtype(self, init_values):
		if 'state' in init_values and self.state == 'draft':
			return 'budget_management.mt_bm_draft'
		elif 'state' in init_values and self.state == 'propose':
			return 'budget_management.mt_bm_propose'
		elif 'state' in init_values and self.state == 'review1':
			return 'budget_management.mt_bm_review1'
		elif 'state' in init_values and self.state == 'consolidate':
			return 'budget_management.mt_bm_consolidate'
		elif 'state' in init_values and self.state == 'review':
			return 'budget_management.mt_bm_review'
		elif 'state' in init_values and self.state == 'validate':
			return 'budget_management.mt_bm_validate'
		elif 'state'in init_values and self.state == 'reject':
			return 'budget_management.mt_bm_reject'
		return super(BudgetManagement,self)._track_subtype(init_values)

	@api.multi
	def _notify_get_groups(self, message, groups):
		groups = super(BudgetManagement, self)._notify_get_groups(message, groups)
		self.ensure_one()
		budget_actions = []
		if self.state == 'propose':
			app_action = self._notify_get_action_link('controller', controller='/budget/propose')
			budget_actions += [{'url': app_action, 'title': _('Review Budget')}]
		if self.state == 'review1':
			app_action = self._notify_get_action_link('controller', controller='/budget/consolidate')
			budget_actions += [{'url': app_action, 'title': _('consolidate Budget')}]
		if self.state == 'consolidate':
			app_action = self._notify_get_action_link('controller', controller='/budget/review')
			budget_actions += [{'url': app_action, 'title': _('Review Budget')}]
		if self.state == 'review':
			app_action = self._notify_get_action_link('controller', controller='/budget/approve')
			budget_actions += [{'url': app_action, 'title': _('Approve Budget')}]
		if self.state in  ['propose', 'review1', 'consolidate', 'review']:
			app_action = self._notify_get_action_link('controller', controller='/budget/refuse')
			budget_actions += [{'url': app_action, 'title': _('Refuse Budget')}]

		bm_finance_group_id = self.env.ref('budget_management.bm_finance').id
		new_group = (
			'bm_finance_group_id', lambda pdata: pdata['type'] == 'user' and bm_finance_group_id in pdata['groups'], {
				'actions': budget_actions,
			})

		return [new_group] + groups

	@api.multi
	def message_subscribe(self, partner_ids=None, channel_ids=None,subtype_ids=None):
		if self.state in ['validate', 'reject']:
			return super(BudgetManagement, self.sudo()).message_subscribe(partner_ids=partner_ids, channel_ids=channel_ids, subtype_ids=subtype_ids)
		return super(BudgetManagement, self).message_subscribe(partner_ids=partner_ids, channel_ids=channel_ids, subtype_ids=subtype_ids)


class budgets(models.Model):
	_name = 'budget.config'
	name = fields.Char(string='Budget Type', required=True,)
	description = fields.Char(string='Description')
	active = fields.Boolean(string='Active')

	@api.model
	def create(self, values):
		current_user = self.env['res.users'].search([('user_id', '=', self.env.uid)])
		rec = super(budgets, self).create(values)
		# if not current_user.has_group('budget_management.bm_ict_admin'):
		# 	raise AccessError('You do not have enough rights to create this record')
		return rec

	@api.multi
	def write(self,values):
		current_user = self.env['res.users'].search([('user_id', '=', self.env.uid)])
		rec = super(budgets, self).write(values)
		# if not current_user.has_group('budget_management.bm_ict_admin'):
		# 	raise AccessError('You do not have enough rights to edit this record')
		return rec

	@api.multi
	def unlink(self):
		current_user = self.env['res.users'].search([('user_id', '=', self.env.uid)])
		rec = super(budgets, self).unlink()
		# if not current_user.has_group('budget_management.bm_ict_admin'):
		# 	raise AccessError('You do not have enough rights to delete this record')
		return rec

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('Budget type can not be duplicated!'))



class BudgetLines(models.Model):
	_name = 'bm.budget.lines'
	_description = 'Budget Lines'
	_rec_name = 'budget_management_id'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	#------------------------------------------------
	#DATABASE
	#------------------------------------------------

	def compute_start_date(self):
		res = self.env['budget.management'].search([])
		for record in res:
			return record.date_from

	def compute_end_date(self):
		res = self.env['budget.management'].search([])
		for record in res:
			return record.date_to


	name = fields.Char(string='Product Reference')
	budget_management_id = fields.Many2one('budget.management', 'Budget Reference')
	currency_id = fields.Many2one(related='budget_management_id.currency_id', store=True, string='Currency', readonly=True)
	date_from = fields.Datetime('Start Date')
	date_to = fields.Datetime('End Date')
	paid_date = fields.Datetime('Paid Date')
	planned_amount = fields.Float(string='Planned Amount', required=False, digits=0)
	practical_amount = fields.Float(string='Subtotal Cost', digits=0, track_visibility='onchange', store=True)
	theoritical_amount = fields.Float(string='Theoretical Amount', digits=0)
	percentage = fields.Float(string='Achievement')
	total_qty = fields.Float(string='Units', track_visibility='onchange', store=True)
	unit_cost = fields.Float( ing='Unit Cost')
	product_id = fields.Many2one('product.product', string='Product')
	actual_amount = fields.Float(string='Actual Cost')
	actual_spent = fields.Float(string='Amount Spent')

	status = fields.Selection(
								[
									('draft', 'Approve'),
									('validate', 'Approved'),
									('reject', 'Rejected')
								],
								string='Status', default='draft'
								)
	budget_item_state = fields.Selection(
										[
											('draft', 'To Approve'),
											('approved', 'Approved'),
											('rejected', 'Rejected')
										], string='State',default='draft')

	product_category = fields.Many2one('product.category', string='Product Category', track_visibility='onchange', store=True)
	product_uom_id = fields.Many2one('uom.uom',related='product_id.uom_id',readonly=True)
	product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', string='Product Template')

	budget_cat_product = fields.Char(string='Budget Category',track_visibility='onchange', store=True)
	source = fields.Many2one('res.users', string='Source', default=lambda self: self.env.user)


	@api.onchange('unit_cost', 'total_qty')
	def _compute_practical_amount(self):
		self.practical_amount = self.total_qty * self.unit_cost

	@api.multi
	def _compute_theoritical_amount(self):
		pass

	@api.multi
	def _compute_percentage(self):
		pass

	@api.multi
	def _actual_amount(self):
		pass

	@api.multi
	def actual_amount_spent(self):
		pass

	@api.onchange('product_id')
	def _product_category(self):
		product_categories = self.env['product.template'].browse(self.product_id.id)
		for product in product_categories:
			print('Current budget line' +str(self.budget_management_id.department_id.name))
			if self.product_id.id == product.id:
				self.product_category = product.categ_id
				self.budget_cat_product = product.product_budget_category
			if fuzz.partial_ratio(str(self.budget_management_id.department_id.name),str(product.product_budget_category))>=VALID_PERCENTAGE:
				# return {
				# 	'warning':{
				# 		'title':_('Budget Item Configured to %s Budget line' %product.product_budget_category),
				# 		'message':_('Therefore this Item will appear in the %s Budget line ' %product.product_budget_category),
				# 		},
				# }
				pass
			else:
				return {
					'warning':{
						'title':_('Budget Item Configured to %s Budget line' %product.product_budget_category),
						'message':_('Therefore this Item will appear in the %s Budget line' %product.product_budget_category),
						},
				}

	#-----------------------------------------------------
	#Override ORM
	#-----------------------------------------------------
	@api.model
	def create(self, values):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		rec = super(BudgetLines, self).create(values)
		if rec.product_id:
			product_categories = self.env['product.template'].browse(rec.product_id.id)
			for product in product_categories:
				if fuzz.partial_ratio(str(product.product_budget_category),str(rec.budget_management_id.department_id.name)) >= VALID_PERCENTAGE:
					pass
				elif not fuzz.partial_ratio(str(product.product_budget_category),str(rec.budget_management_id.department_id.name)) >= VALID_PERCENTAGE:
					#search through thr budget line
					search_budget_line = self.env['budget.management'].search([('department_id.name', 'ilike', product.product_budget_category),('active', '=', True)])
					for budget in search_budget_line:
						rec.budget_management_id = budget.id
						rec.source = current_employee.id
		return rec

	@api.multi
	def write(self, values):
		rec = super(BudgetLines, self).write(values)
		return rec

	@api.multi
	def unlink(self):
		rec = super(BudgetLines, self).unlink()
		return rec

	def copy_data(self, context=None):
		raise UserError(_('Budget line can not be duplicated'))

	#----------------------------------------------------------
	#Business logic
	#----------------------------------------------------------

	@api.multi
	def approve_budget_line_item(self):
		#if self.budget_management_id.department_manager_id:
		self.write({
			'status':'validate',
			'budget_item_state':'approved',
		})
		# else:
		# 	raise UserError(_('You don\'t sufficient rights to approve budget line \n'
		# 						+'Please contact system Administrator'))
	@api.multi
	def reject_budget_line_item(self):
		#if self.budget_management_id.department_manager_id:
		self.write({
			'status':'reject',
			'budget_item_state':'rejected',
		})
		# else:
		# 	raise UserError(_('You don\'t have sufficient rights to reject budget line \n'
		# 						+'Please contact system Administrator'))
class kolarequestlines(models.Model):
	_inherit = 'kola.requisition.lines'





