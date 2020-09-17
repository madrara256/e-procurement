from datetime import date, datetime,timedelta
from dateutil.relativedelta import relativedelta
import calendar

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class PurchaseTask(models.Model):
	_name = 'purchase.task'
	_description = 'Purchase Tasks'


	name = fields.Char(string='Name')
	description = fields.Html(string='Description')
	active = fields.Boolean(string='Active')
	color = fields.Integer(string='Index')
	due_date = fields.Datetime(string='Due Date')
	state = fields.Selection(
		[
		('new', 'New'),
		('done', 'Complete')
		], string='States', expand='_expand_states', default='new')
	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	@api.multi
	def mark_done(self):
		self.write({'state':'done'})