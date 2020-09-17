# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class RatingParameter(models.Model):
	_name = 'rating.parameter'
	_inherit = ['mail.thread']
	_description = 'Rating Parameters'


	name = fields.Char(string='Parameter')
	category = fields.Selection(
		[
			('service', 'Services Offered'),
			('goods', 'Delivered Supplies')
		],
	string='Category')








