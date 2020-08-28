from odoo import models, fields, api
from datetime import datetime,timedelta,date

class kolaratingService(models.Model):
	_name = 'kola.rating.service'
	_description = 'Contract Ratings Based On Service Delivery'


	kolaevaluate_service_id = fields.Many2one('kolacontract.evaluate', string='Service Rating', ondelete='cascade')
	rating_params = fields.Many2one('rating.parameter', string='Parameter', domain=[('category','=','service'),])
	ratings = fields.Selection(
		[
			(4, 'Excellent'),
			(3, 'Good'),
			(2, 'Fair'),
			(1, 'Poor')
		], string='Ratings')

	score = fields.Float(string='Score', compute='_compute_average_score', store=True,)
	comments = fields.Char(string='Comments')

	@api.multi
	def _compute_average_score(self):
		pass

class KolaratingGoods(models.Model):
	_name = 'kola.rating.goods'
	_description = 'Contract Rating Based On Goods Supply'


	kolaevaluate_goods_id = fields.Many2one('kolacontract.evaluate', string='Ratings', ondelete='cascade')
	rating_params = fields.Many2one('rating.parameter', string='Parameter',domain=[('category','=','goods'),])
	ratings = fields.Selection(
		[
			(4, 'Excellent'),
			(3, 'Good'),
			(2, 'Fair'),
			(1, 'Poor')
		], string='Ratings')

	score = fields.Float(string='Score', compute='_compute_average_score', store=True,)
	comments = fields.Char(string='Comments')

	@api.multi
	def _compute_average_score(self):
		pass
