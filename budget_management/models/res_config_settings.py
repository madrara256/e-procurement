from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	budget_expiry_date = fields.Boolean(string='Budget End Date', default=True)