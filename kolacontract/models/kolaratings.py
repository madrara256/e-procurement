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

	@api.depends('ratings')
	def _compute_average_score(self):
		for record in self:
			if record.ratings == 4:
				#record.score = 4.0
				record.update({'score':4.0})
			elif record.ratings == 3:
				record.update({'score':3.0})
			elif record.ratings == 2:
				record.update({'score':2.0})
			elif record.ratings == 1:
				record.update({'score':1.0})

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

	@api.depends('ratings')
	def _compute_average_score(self):
		for record in self:
			if record.ratings == 4:
				return record.update({'score':4.0})
			elif record.ratings == 3:
				return record.update({'score':3.0})
			elif record.ratings == 2:
				return record.update({'score':2.0})
			elif record.ratings == 1:
				return record.update({'score':1.0})
