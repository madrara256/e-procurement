from odoo import models, fields, api

class ResPartner(models.Model):
	_inherit = 'res.partner'

	# @api.multi
	# def compute_overall_ratings_score(self):
	# 	all_ratings = self.env['kolacontract.evaluate'].search([('supplier_id', '=', self.id)])
	# 	for record in all_ratings:
	# 		total_score = 0.0
	# 		final_score = 0.0
	# 		if record.actual_provider_score:
	# 			total_score+=record.actual_provider_score
	# 			final_score = total_score/(len(record.id))
	# 		elif record.actual_supplier_score:
	# 			total_score+=record.actual_supplier_score
	# 			final_score = total_score/(len(record.id))

	# overall_ratings_score = fields.Float(string='Ratings', compute='compute_overall_ratings_score', store=True)



