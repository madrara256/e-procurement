# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import calendar

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class KolaConsolidatedSummaryReport(models.AbstractModel):
	_name = 'report.consolidated.requestsummary'

	def get_department_id(self, data):
		res = []
		request_departments = self.env['kola.requisition'].search([('active', '=', True)])
		for request in request_departments:
			res.append({'department':request.department_id.name})
		return res

	@api.model
	def get_report_values(self, docids, data=None):
		if not data.get('form'):
			raise UserError(_('Form content is missing, this report can not be printed'))
		kola_request_report = self.env['ir.actions.report']._get_report_from_name('kolarequisition.report_consolidate_purchase_request')
		purchase_requests = self.env['kola.requisition'].browse(self.ids)
		return {
			'doc_ids': self.ids,
			'requests': purchase_requests,
		}
