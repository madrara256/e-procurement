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
	_inherit = ['mail.thread']
	_rec_name = 'supplier_id'
	_description = 'Contract Evaluation'

	#contract_id = fields.Many2one('kola.contract', string='Contract', track_visibility='onchange')
	supplier_id = fields.Many2one('res.partner',string='Vendor', domain=[('is_company', '=', True),('supplier', '=', True)])
	address = fields.Char(string='Address')
	evaluation_date = fields.Datetime(string='Date', default=datetime.today().now(), track_visibility='onchange')
	user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
	def default_employee(self):
		employee_id = self.env['hr.employee'].search([('active','=',True), ('user_id', '=', self.env.uid)])
		if employee_id:
			return employee_id.department_id
	employee_id = fields.Many2one('hr.employee', string='Employee', track_visibility='onchange', default=default_employee)
	def default_department(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		return employee_id.department_id.id

	department_id = fields.Many2one('hr.department', string='Department', default=default_department, readonly=True)
	prepared_by = fields.Many2one('hr.employee', string='Prepared By')
	goods_supplied = fields.Many2one('product.product', string='Goods Supplied')
	service_line_ratings_id = fields.One2many('kola.rating.service', 'kolaevaluate_service_id', string='Service Ratings')
	goods_line_ratings_id = fields.One2many('kola.rating.goods', 'kolaevaluate_goods_id', string='Supply Ratings')

	def _department_manager(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if employee_id:
			manager_id = employee_id.department_id.manager_id.id
			related_user_id = self.env['hr.employee'].search([('user_id', '=', manager_id)], limit=1)
			for user in related_user_id:
				return user.user_id

	department_manager = fields.Many2one('hr.employee', string='Department Manager', 
		default=_department_manager)
	
	param_count_goods = fields.Integer(string='Param Count(Goods)',compute='_compute_params_goods', store=True,)
	max_score_goods = fields.Float(string='Maximum Score', compute='_compute_maximum_score_goods', store=True,)
	actual_supplier_score = fields.Float(string='Actual Supplier Score', compute='_compute_actual_supplier_score', store=True,)
	supplier_score = fields.Float(string='Supplier Ratings', compute='_compute_supplier_ratings', store=True,)

	param_count_service = fields.Integer(string='Param Count(Service)', compute='_compute_params_service', store=True,)
	max_score_service = fields.Float(string='Maximum Score', compute='_compute_maximum_score_service', store=True,)
	actual_provider_score = fields.Float(string='Actual Provider Score', compute='_compute_actual_service_provider_score', store=True,)
	service_provider_score = fields.Float(string='Service Provider Ratings', compute='_compute_service_provider_ratings', store=True,)
	color = fields.Integer(string='Index')
	evaluation = fields.Selection([
		('supply', 'Supply Of Goods'),
		('service', 'Provision Of Service')], 
	string='Evaluation for?', default='supply')
	active = fields.Boolean(string='Active', default=True)

	#goods
	@api.depends('goods_line_ratings_id.score')
	def _compute_maximum_score_goods(self):
		for evaluation in self:
			maximum_score = 0.0
			for param in evaluation.goods_line_ratings_id:
				maximum_score = (evaluation.param_count_goods*4)
				evaluation.update({'max_score_goods':maximum_score})

	@api.depends('goods_line_ratings_id.score')
	def _compute_actual_supplier_score(self):
		for evaluation in self:
			actual_score = 0.0
			for param in evaluation.goods_line_ratings_id:
				actual_score += param.score
				evaluation.update({'actual_supplier_score':actual_score})

	@api.depends('goods_line_ratings_id')
	def _compute_params_goods(self):
		param_search_count = len(self.goods_line_ratings_id)
		self.update({'param_count_goods':param_search_count})


	@api.depends('param_count_goods', 'max_score_goods')
	def _compute_supplier_ratings(self):
		if self.max_score_goods > 0:
			actual_score = 0.0
			actual_score = (self.actual_supplier_score/self.max_score_goods)*100
			self.update({'supplier_score':actual_score})

	#service
	@api.depends('service_line_ratings_id.score')
	def _compute_maximum_score_service(self):
		for evaluation in self:
			maximum_score = 0.0
			for param in evaluation.service_line_ratings_id:
				maximum_score = (evaluation.param_count_service*4)
				evaluation.update({'max_score_service':maximum_score})

	@api.depends('service_line_ratings_id.score')
	def _compute_actual_service_provider_score(self):
		for evaluation in self:
			actual_score = 0.0
			for param in evaluation.service_line_ratings_id:
				actual_score += param.score
				evaluation.update({'actual_provider_score':actual_score})

	@api.depends('service_line_ratings_id')
	def _compute_params_service(self):
		param_search_count = len(self.service_line_ratings_id)
		self.update({'param_count_service':param_search_count})

	@api.depends('param_count_service')
	def _compute_service_provider_ratings(self):
		if self.max_score_service > 0:
			actual_score = 0.0
			actual_score = (self.actual_provider_score/self.max_score_service)*100
			self.update({'service_provider_score':actual_score})

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
		return evaluate

	@api.multi
	def copy_data(self, default=None):
		raise UserError(_('Evaluation can not be duplicated'))

	@api.multi
	def unlink(self):
		return super(KolaEvaluate, self).unlink()

	#------------------------------------------------
	#Business logic
	#------------------------------------------------

	@api.multi
	def confirm_evaluation(self):
		self.write({'state':'confirm'})

	@api.multi
	def validate_evaluation(self):
		self.write({'state': 'validate'})

	@api.multi
	def reset_to_draft(self):
		self.write({'state': 'draft'})


class VendorScore(models.Model):
	_name = 'vendor.score'

	vendor_id = fields.Many2one('res.partner', string='Vendor')
	score = fields.Float(string='Score')






