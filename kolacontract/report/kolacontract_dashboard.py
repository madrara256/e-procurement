# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, tools


class KolacontractDashboard(models.Model):
	_name = 'kolacontract.dashboard'
	_auto = False
	_description = 'Contract Dashboard'
	_rec_name = 'contractor_id'

	contractor_id = fields.Many2one('res.partner', string='Contractor', readonly=True, )
	department_id = fields.Many2one('hr.department', string='Department', readonly=True, )
	state = fields.Char(string='State', readonly=True, )
	active = fields.Boolean(string='Acive', readonly=True, )
	number_of_days = fields.Float(string='Number Of Days', readonly=True, )
	amount = fields.Float(string='Amount', readonly=True, )

	def _select(self):
		return """
			SELECT
				kc.id as id,
				kc.contractor_id,
				kc.department_id,
				kc.state,
				kc.number_of_days_due as number_of_days,
				kc.amount,
				kc.active
		"""
	def _from(self):
		return """
			FROM
				kola_contract as kc
		"""

	def _where(self):
		return """
			WHERE
				kc.active = True
		"""

	def _groupby(self):
		return """
			GROUP BY
				kc.id,
				kc.contractor_id,
				kc.department_id,
				kc.state,
				kc.number_of_days_due,
				kc.amount,
				kc.active
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


