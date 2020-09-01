from odoo import api, models, tools

import logging
import threading

_logger = logging.getLogger(__name__)


class KolaConsolidateCompute(models.TransientModel):
	_name = 'kolaconsolidate.compute'
	_description = 'Generate Consolidated Purchase Requests'

	@api.multi
	def print_consolidated_requests(self):
		return self.env.ref('kolarequisition.action_consolidated_purchase_request').report_action(self)


