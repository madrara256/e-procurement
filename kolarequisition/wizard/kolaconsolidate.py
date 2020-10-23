from odoo import api, fields, models, tools,_
import time
import logging
import threading
from odoo.exceptions import UserError, AccessError,ValidationError

_logger = logging.getLogger(__name__)


class KolaConsolidateCompute(models.TransientModel):
	_name = 'kolaconsolidate.compute'
	_description = 'Generate Consolidated Purchase Requests'


	date_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
	depts = fields.Many2many('hr.department',string='Department(s)')


	request_type = fields.Selection([
		('draft', 'Draft'),
		('validate1', 'To Supervisor'),
		('validate2','Second Approval'),
		('validate3', 'To Admin & Finance'),
		('validate', 'Approved'),
		('order', 'RFQs(Sourcing)'),
		('reject', 'Cancelled')
		], string='Request Status', required=True, default='validate')

	@api.multi
	def print_consolidated_requests(self):
		self.ensure_one()
		[data] = self.read()
		if not data.get('depts'):
			raise UserError(_('You have to select at least one department. And try again'))
		departments = self.env['hr.department'].browse(data['depts'])
		datas = {
			'ids': [],
			'model': 'hr.department',
			'form': data
		}		
		return self.env.ref('kolarequisition.action_consolidated_purchase_request').with_context(from_transition_model=True).report_action(departments, data=datas)



