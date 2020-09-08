# -*- coding: utf-8 -*-

from odoo import models, fields, api,_,tools,SUPERUSER_ID
from datetime import datetime,timedelta,date
from odoo.exceptions import UserError, AccessError, ValidationError
import math
from odoo.http import request
from werkzeug import url_encode


class KolaevaluateOverall(models.Model):
	_name = 'kola.evaluate.overall'
	_description = 'Kola Evaluate Overall Score'
	_inherit = ['mail.thread']

	name = fields.Char(string='Reference', default='New', require=True, track_visibility='onchange')
	contract_id = fields.Many2one('kola.contract', string='Contract', track_visibility='onchange')
	supplier_id = fields.Many2one('res.partner',string='Supplier')
	department_id = fields.Many2one('hr.department', related='contract_id.department_id', string='Department')
	color = fields.Integer(string='Index')
