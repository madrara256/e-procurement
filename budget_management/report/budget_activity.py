# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, tools

class BudgetActivity(models.Model):
	_name = 'budget.activity.summary'
	_description = 'Budget Activity Summary'
	_auto = False

	active = fields.Boolean(string='Active', readonly=True)
	department_id = fields.Many2one('hr.department', readonly=True)

	def _select(self):
		return """
			SELECT
				bm.id as id,
				bm.active,
				bm.department_id
		"""

	def _from(self):
		return """
			FROM budget_management as bm
		"""

	def _where(self):
		return """
			WHERE active = True
		"""

	def _groupby(self):
		return """
			GROUP BY
				bm.id,
				bm.active,
				bm.department_id
		"""

	def init(self):
		tools.drop_view_if_exists(self._cr,self._table)
		self._cr.execute("""
			CREATE OR REPLACE VIEW %s AS (
				%s
				%s
				%s
				%s
			)
			""" % (self._table, self._select(), self._from(), self._where(), self._groupby()))