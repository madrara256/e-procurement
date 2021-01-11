from odoo import fields, models,_


class ContractSLA(models.Model):
	_name = 'contract.sla'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Contracting Process SLA'


	name = fields.Char(string='Name')
	maximum_time_for_action = fields.Integer(string='Time In Hours')
	active = fields.Boolean(string='Active', default=True)

	