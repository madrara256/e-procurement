# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class Team(models.Model):
	_name = 'budget.team'
	_description = 'Teams'
	_rec_name = 'name'

	name = fields.Char(string='Branch Name',)
	description = fields.Char(string='Description')
	active = fields.Boolean(string='Active', default=True)

