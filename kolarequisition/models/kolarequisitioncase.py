from odoo import models, fields, api, _

class KolaRequisitionCase(models.Model):
	_name = 'kola.requisition.case'
	_inherit = ['mail.thread']
	_description = 'Purchase Request Case'


	#---------------------------------------
	# DATABASES
	#---------------------------------------
	name = fields.Char(string='Name')
	case_value = fields.Float(string='Case Value')
	description = fields.Html(string='Description')
	active = fields.Boolean(string='Active', default=True)


