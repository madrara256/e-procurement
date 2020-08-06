from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	contract_duration_settings = fields.Boolean(string='Yearly Contract Renewal')