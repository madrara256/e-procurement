# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import _, fields, http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo import release


class BudgetsController(http.Controller):
	@http.route('/procure2pay_dashboard/data', type='json', auth='user')
	def web_settings_dashboard_data(self, **kw):
		approved_budgets = request.env['budget.management'].search_count([
			('state', '=', 'validate')])

		cr = request.cr
		cr.execute("""
		 	SELECT count(*)
				FROM budget_management
				WHERE state = 'draft'""")
		draft_budgets = cr.dictfetchall()[0].get('drafts')

		#stock


		return {
			'budgets':{
				'approved_budgets':approved_budgets
			}
		}
