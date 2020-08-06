from odoo import models, fields, api


class kolacontractstage(models.Model):
	_name = 'kola.stage'
	_inherit = ['mail.thread']
	_description = 'Contract Stage'
	_order = 'sequence, id'

	name = fields.Char(string='Stage Name', required=True, translate=True)
	description = fields.Html(translate=True,string='Description')
	sequence = fields.Integer(default=1)
	fold = fields.Boolean(string='Folded in Kanban',
		help='This stage is folded in the kanban view when there are no records in that stage to display.', default=False)
	active = fields.Boolean(string='Active', default=True)
