# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import calendar

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class KolaConsolidatedSummaryReport(models.AbstractModel):
	_name = 'report.consolidated.requestsummary'

	def _get_data_from_report(self, data):
		res = []

		return res

	@api.model
	def _get_report_values(self, docids, data=None):
		pass
