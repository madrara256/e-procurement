# -*- coding: utf-8 -*-

from odoo import models, fields, api,_,tools,SUPERUSER_ID
from datetime import datetime,timedelta,date
from odoo.exceptions import UserError, AccessError, ValidationError
import math
from odoo.http import request
from werkzeug import url_encode


class KolaevaluateOverall(models.Model):
	_name = 'kola.evaluate.overall'
	_description = 'Kola Evaluate Overall Score'
	_auto = False
	_rec_name = 'supplier_id'


	supplier_id = fields.Many2one('res.partner',string='Supplier', readonly=True)
	department_id = fields.Many2one('hr.department', readonly=True)
	color = fields.Integer(string='Index', readonly=True)
	surveys_submitted = fields.Integer(string='Surveys', readonly=True)
	service_provider_average_score = fields.Float(string='Average Score', digits=(12,1))
	supplier_average_score = fields.Float(string='Average Score', digits=(12,1))
	evaluation = fields.Char(string='Evaluate for?')

	def _select(self):
		return """ 
			SELECT 
				min(ke.id) as id,
				ke.supplier_id,
				ke.department_id,
				ke.evaluation,
				count(supplier_id) as surveys_submitted,
				(sum(service_provider_score)/
				count(supplier_id)
				) AS service_provider_average_score,
				(sum(supplier_score)/
					count(supplier_id)
				) AS supplier_average_score
				
		"""

	def _from(self):
		return """
			FROM 
				kolacontract_evaluate as ke
		"""

	def _groupby(self):
		return """
			GROUP BY
				ke.supplier_id,
				ke.department_id,
				ke.evaluation
		"""
	def init(self):
		tools.drop_view_if_exists(self._cr, self._table)
		self._cr.execute("""
			CREATE OR REPLACE VIEW %s AS (
				%s
				%s
				%s
			)
			""" % (self._table, self._select(), self._from(), self._groupby()))

