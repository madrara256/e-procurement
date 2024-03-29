# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, tools
from datetime import datetime,timedelta,date

class BudgetActivity(models.Model):
	_name = 'budget.activity.summary'
	_description = 'Budget Progress Summary'
	_auto = False

	active = fields.Boolean(string='Active', readonly=True)
	department_id = fields.Many2one('hr.department', readonly=True)
	product_id = fields.Many2one('product.template', string='Product', readonly=True)
	budget_cat_product = fields.Char(string='Budget Category', readonly=True)
	budget_quantity = fields.Integer(string='Budgeted Quantity', readonly=True)
	budget_unit_cost = fields.Float(string='Budgeted Unit Cost', readonly=True)
	budgetted_product_category = fields.Char(string='Product Category', readonly=True)
	budget_total = fields.Float(string='Budget Total', readonly=True)

	product_state = fields.Char(string='Item State', readonly=True)
	order_reference = fields.Many2one('purchase.order', string='Order Reference', readonly=True)
	order_state = fields.Char(string='Order State', readonly=True)
	budget_subtotal = fields.Float(string='Budget Subtotal', readonly=True)
	budget_date_from = fields.Datetime(string='Start Date', readonly=True)
	budget_date_to = fields.Datetime(string='End Date', readonly=True)

	purchased_qnty = fields.Integer(string='Purchased Quantity', readonly=True)
	purchase_unit_cost = fields.Float(string='Unit Cost', readonly=True)
	purchase_total = fields.Float(string='Price Total', readonly=True)
	purchase_tax = fields.Float(string='Tax', readonly=True)
	budget_balance = fields.Float(string='Budget Balance', readonly=True)
	quantity_left = fields.Integer(string='Quantity left', readonly=True)
	# order_state = fields.Char(string='Order State', readonly=True)


	def _select(self):
		return """
			SELECT
				bm.id as id,
				bm.active,
				bm.department_id,
				bm.total_budget_cost as budget_total,
				bml.product_id,
				bml.total_qty,
				bml.budget_cat_product,
				SUM(bml.total_qty) as budget_quantity,
				bml.unit_cost as budget_unit_cost,
				bml.status as product_state,
				bml.product_category as budgetted_product_category,
				pol.order_id as order_reference,
				po.state as order_state,
				bml.practical_amount as budget_subtotal,
				bm.date_from as budget_date_from,
				bm.date_to as budget_date_to,
				SUM(pol.product_qty) as purchased_qnty,
				pol.price_unit as purchase_unit_cost,
				pol.price_total as purchase_total,
				pol.price_tax as purchase_tax,
				SUM(bml.total_qty - pol.price_total) as budget_balance,
				SUM(bml.total_qty - pol.product_qty) as quantity_left

		"""

	def _from(self):
		return """
			FROM budget_management as bm
		"""

	def _join(self):
		return """
			JOIN bm_budget_lines AS bml 
				ON bm.id = bml.budget_management_id

			JOIN purchase_order_line AS pol
				ON bml.product_id = pol.product_id

			JOIN product_template AS ptmpl
				ON bml.product_id = ptmpl.id

			JOIN purchase_order AS po
				ON pol.order_id = po.id
		"""

	def _where(self):
		return """
			WHERE bm.active = True 
		"""

	def _groupby(self):
		return """
			GROUP BY
				bm.id,
				bm.active,
				bm.department_id,
				bml.product_id,
				bml.budget_cat_product,
				bml.total_qty,
				bml.unit_cost,
				bml.status,
				bml.product_category,
				pol.order_id,
				po.state,
				bml.practical_amount,
				bm.date_from,
				bm.date_to,
				pol.price_unit,
				pol.price_total,
				pol.price_tax,
				bm.total_budget_cost
		"""

	def init(self):
		tools.drop_view_if_exists(self._cr,self._table)
		self._cr.execute("""
			CREATE OR REPLACE VIEW %s AS (
				%s
				%s
				%s
				%s
				%s
			)
			""" % (self._table, self._select(), self._from(), self._join(), self._where(), self._groupby()))