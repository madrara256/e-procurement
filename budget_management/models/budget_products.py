 # Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class BudgetProducts(models.Model):
	_inherit = 'product.product'
	_description = 'Products'


