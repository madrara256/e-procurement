# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class BudgetGuidlines(models.Model):
	_name = 'budget.guidline'
	_description = 'Budget Guidelines'

	name = fields.Char(
		string='Name'
	)

