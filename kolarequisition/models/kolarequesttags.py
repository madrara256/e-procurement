# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class Tags(models.Model):
	_name = 'request.tag'
	_inherit = ['mail.thread']

	name = fields.Char(string='Tag')
	description = fields.Char(string='Description')
	active = fields.Boolean(string='Active')
