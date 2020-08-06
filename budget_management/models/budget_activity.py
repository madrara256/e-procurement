from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _,exceptions
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError,ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp

from fuzzywuzzy import fuzz


class BudgetActivity(models.Model):
	_name = 'budget.activity'
	_description = 'Budget Activity'
	_rec_name = 'name'


	name = fields.Char(string='Budget Reference')
	budget_id = fields.Many2one('budget.management', string='Budget Name')
