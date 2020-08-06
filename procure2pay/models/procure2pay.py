# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd
from pytz import utc
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils
ROUNDING_FACTOR = 16

class KolaBudget(models.Model):
	_inherit = 'budget.management'
	_description ='Budgets'

	@api.model
	def get_all_current_budgets(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			budgets = self.env['budget.management'].sudo().search_count([])
			return {
				'budgets': budgets if budgets else 0
			}
		else:
			return False

	@api.model
	def get_all_budget_analysis(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			cr = self._cr
			cr.execute("""
			select budget_management.state, sum(budget_management.total_budget_cost) as budget_total
			from budget_management
			group by
			budget_management.state
			order by budget_total desc
			""")

			budget_results =  cr.fetchall()
			return {
				'budget_results':budget_results
			}
		else:
			return False

	@api.model
	def get_department_budget(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			month_list = []
			graph_result = []

			for i in range(5, -1, 1):
				last_month = datetime.now() - relativedelta(months=i)
				text = format(last_month, '%B %Y')
				month_list.append(text)
			self.env.cr.execute("""select id, name from hr_department""")
			departments = self.env.cr.dictfetchall()
			departments_list = [x['name'] for x in departments]
			for month in month_list:
				budget = {}
				for dept in departments:
					budget[dept['name']] = 0
				vals = {
					'l_month': month,
					'budget': budget
				}
				graph_result.append(vals)
				sql = """
				SELECT name, total_budget_cost, department_id, state

				"""
			return {
			}
		else:
			return False

class KolaContract(models.Model):
	_inherit = 'kola.contract'
	_description ='Contract'


	@api.model
	def get_contract_details(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			contracts_due_to_expire = self.env['kola.contract'].sudo().search_count([('state', '=', 'renew')])
			return {
				'id':contracts_due_to_expire if contracts_due_to_expire else 0
				}
		else:
			return False

	@api.model
	def get_running_contracts(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			contracts_running = self.env['kola.contract'].sudo().search_count([('state', '=', 'validate')])
			return {
				'contracts_running':contracts_running if contracts_running else 0
			}
		else:
			return False


	@api.model
	def get_contracts_analysis(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			cr = self._cr
			cr.execute("""
			select kola_contract.state, count(*)
			from kola_contract
			group by kola_contract.state""")

			dat = cr.fetchall()
			print(dat)
			data = []
			for i in range(0, len(dat)):
				data.append({'label': dat[i][0], 'value':dat[i][1]})
			#print(data)
			return data
		else:
			return False

class KolaInventory(models.Model):
	_inherit = 'stock.inventory'
	_description = 'Inventory'


	@api.model
	def get_all_inventory_analysis(self):
		uid = request.session.uid

		return {

		}

class KolaStock(models.Model):
	_inherit = 'stock.quant'

	@api.model
	def get_all_stock_analysis(self):
		uid = request.session.uid

		return {

		}


class KolaInvoicing(models.Model):
	_inherit='account.account'
	_description ='Invoicing'

class KolaPurchase(models.Model):
	_inherit = 'purchase.order'
	_description ='Purchase'

	@api.model
	def get_purchases(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			purchases = self.env['purchase.order'].sudo().search_count([])

			return {
				'purchases': purchases if purchases else 0
			}
		else:
			return False

	@api.model
	def get_purchase_trend_analysis(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			cr = self._cr
			cr.execute("""
			select purchase_order.state, count(*)
			from purchase_order
			group by purchase_order.state""")

			dat = cr.fetchall()
			print(dat)
			data = []
			for i in range(0, len(dat)):
				data.append({'label': dat[i][0], 'value':dat[i][1]})
			#print(data)
			return data
		else:
			return False

	@api.model
	def get_expenditure_by_department(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			cr = self._cr
			cr.execute("""
			select sum(amount_total) as amount_total, hr_department.name from purchase_order
			inner join hr_employee on hr_employee.user_id = purchase_order.user_id
			inner join hr_department  on hr_department.id = hr_employee.department_id
			group by
			hr_department.name
			""")

			data = cr.fetchall()
			print(data)
			result = []
			for i in range(0, len(data)):
				result.append({'amount': data[i][0], 'department':data[i][1]})
			return result;
		else:
			return False



	@api.model
	def get_all_purchases_records(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			purchase_lines = []
			graph_result = []

			cr = self._cr
			cr.execute("""
			select state, sum(amount_total) as amount_total
			from purchase_order
			group by state
			""")

			purchase_lines =  cr.fetchall()
			result = []
			for i in range(0,len(purchase_lines)):
				result.append({'amount': purchase_lines[i][1], 'state': purchase_lines[i][0]})
			print('****printing result ****')
			print(result)
			print('****printing data *****')
			return purchase_lines,result

		else:
			return False


class KolaRequisition(models.Model):
	_inherit='kola.requisition'
	_description ='Purchase Requisition'

	@api.model
	def get_purchase_requests(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			requests = self.env['kola.requisition'].sudo().search_count([])
			new_requests = self.env['kola.requisition'].sudo().search_count([('state', '=', 'draft')])
			approved_requests = self.env['kola.requisition'].sudo().search_count([('state', '=', 'validate')])
			return {
				'requests': requests if requests else 0,
				'new_requests':new_requests if new_requests else 0,
				'approved_requests': approved_requests if approved_requests else 0
			}
		else:
			return False



class KolaProduct(models.Model):
	_inherit = 'product.product'

	@api.model
	def get_highest_stock_standings(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			query = """
			select product_template.name,product_product.qty_available  from product_product
			inner join product_template on product_template.id=product_product.product_tmpl_id
			order by product_product.qty_available desc
			limit 10
			"""
			cr = self._cr
			cr.execute(query)
			top_ranking_stock = cr.fetchall()
			return {
				'top_ranking_stock':top_ranking_stock if top_ranking_stock else 0
			}
		else:
			return False

	@api.model
	def get_lowest_stock_standings(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			query = """
			select product_template.name,product_product.qty_available  from product_product
			inner join product_template on product_template.id=product_product.product_tmpl_id
			where product_template.type = 'product'
			order by product_product.qty_available asc
			limit 10
			"""

			cr = self._cr
			cr.execute(query)
			lowest_ranking_stock = cr.fetchall()
			return {
				'lowest_ranking_stock': lowest_ranking_stock if lowest_ranking_stock else 0
			}
		else:
			return False


class KolaScrapQuant(models.Model):
	_inherit = 'stock.scrap'

	@api.model
	def get_stock_scrap_quant(self):
		uid = request.session.uid
		employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
		if employee:
			query = """
			select product_template.name, stock_scrap.scrap_qty from
			stock_scrap
			inner join product_template on product_template.id = stock_scrap.product_id
			order by stock_scrap.scrap_qty desc
			limit 10
			"""

			cr = self._cr
			cr.execute(query)
			scrap_ranking_stock = cr.fetchall()
			return {
				'scrap_ranking_stock': scrap_ranking_stock if scrap_ranking_stock else 0
			}
		else:
			return False















