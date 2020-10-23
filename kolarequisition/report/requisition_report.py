# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, tools

class RequisitionReport(models.Model):
	_name = 'requisition.dashboard'
	_description = 'Purchase Request Dashboard'
	_auto = False

	reference_number = fields.Char(string='Reference', readonly=True, )
	active = fields.Boolean(string='Active', readonly=True, )
	employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True, )
	department_id = fields.Many2one('hr.department', string='Department', readonly=True, )
	requisition_date = fields.Datetime(string='Request Date', readonly=True, )
	requisition_amount = fields.Float(string='Total Amount', readonly=True)
	state = fields.Char(string='Status', readonly=True)
	def _select(self):
		return """
			SELECT
				kr.id as id,
				kr.active,
				kr.employee_id,
				kr.department_id,
				kr.requisition_date,
				kr.name as reference_number,
				kr.requisition_amount,
				kr.state
		"""

	def _from(self):
		return """
			FROM kola_requisition as kr
		"""

	def _where(self):
		return """
			WHERE
				kr.active = True
		"""

	def _groupby(self):
		return """
			GROUP BY
				kr.id,
				kr.active,
				kr.employee_id,
				kr.department_id,
				kr.requisition_date,
				kr.reference_number,
				kr.requisition_amount,
				kr.state
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




