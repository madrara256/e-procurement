# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockScrap(models.Model):
	_name = 'stock.scrap'
	_order = 'id desc'
	_description = 'Scrap'

	def _get_default_scrap_location_id(self):
		return self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1).id

	def _get_default_location_id(self):
		company_user = self.env.user.company_id
		warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
		if warehouse:
			return warehouse.lot_stock_id.id
		return None

	name = fields.Char(
		'Reference',  default=lambda self: _('New'),
		copy=False, readonly=True, required=True,
		states={'done': [('readonly', True)]})
	origin = fields.Char(string='Source Document')
	product_id = fields.Many2one(
		'product.product', 'Product', domain=[('type', 'in', ['product', 'consu'])],
		required=True, states={'done': [('readonly', True)]})
	product_uom_id = fields.Many2one(
		'uom.uom', 'Unit of Measure',
		required=True, states={'done': [('readonly', True)]})
	tracking = fields.Selection('Product Tracking', readonly=True, related="product_id.tracking")
	lot_id = fields.Many2one(
		'stock.production.lot', 'Lot',
		states={'done': [('readonly', True)]}, domain="[('product_id', '=', product_id)]")
	package_id = fields.Many2one(
		'stock.quant.package', 'Package',
		states={'done': [('readonly', True)]})
	owner_id = fields.Many2one('res.partner', 'Owner', states={'done': [('readonly', True)]})
	move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
	picking_id = fields.Many2one('stock.picking', 'Picking', states={'done': [('readonly', True)]})
	location_id = fields.Many2one(
		'stock.location', 'Location', domain="[('usage', '=', 'internal')]",
		required=True, states={'done': [('readonly', True)]}, default=_get_default_location_id)
	scrap_location_id = fields.Many2one(
		'stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
		domain="[('scrap_location', '=', True)]", required=True, states={'done': [('readonly', True)]})
	scrap_qty = fields.Float('Quantity', default=1.0, required=True, states={'done': [('readonly', True)]})
	state = fields.Selection([
		('draft', 'Draft'),
		('done', 'Done')], string='Status', group_expand='_expand_states', default="draft")

	def _expand_states(self, states, domain, order):
		return [key for key, val in type(self).state.selection]

	date_expected = fields.Datetime('Expected Date', default=fields.Datetime.now)
	color = fields.Integer(string='Index')

	@api.onchange('picking_id')
	def _onchange_picking_id(self):
		if self.picking_id:
			self.location_id = (self.picking_id.state == 'done') and self.picking_id.location_dest_id.id or self.picking_id.location_id.id

	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.product_uom_id = self.product_id.uom_id.id

	@api.model
	def create(self, vals):
		if 'name' not in vals or vals['name'] == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
		scrap = super(StockScrap, self).create(vals)
		return scrap

	def unlink(self):
		if 'done' in self.mapped('state'):
			raise UserError(_('You cannot delete a scrap which is in done state.'))
		return super(StockScrap, self).unlink()

	def _get_origin_moves(self):
		return self.picking_id and self.picking_id.move_lines.filtered(lambda x: x.product_id == self.product_id)

	def _prepare_move_values(self):
		self.ensure_one()
		return {
			'name': self.name,
			'origin': self.origin or self.picking_id.name or self.name,
			'product_id': self.product_id.id,
			'product_uom': self.product_uom_id.id,
			'product_uom_qty': self.scrap_qty,
			'location_id': self.location_id.id,
			'scrapped': True,
			'location_dest_id': self.scrap_location_id.id,
			'move_line_ids': [(0, 0, {'product_id': self.product_id.id,
										   'product_uom_id': self.product_uom_id.id,
										   'qty_done': self.scrap_qty,
										   'location_id': self.location_id.id,
										   'location_dest_id': self.scrap_location_id.id,
										   'package_id': self.package_id.id,
										   'owner_id': self.owner_id.id,
										   'lot_id': self.lot_id.id, })],
#             'restrict_partner_id': self.owner_id.id,
			'picking_id': self.picking_id.id
		}

	@api.multi
	def do_scrap(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		for scrap in self:
			move = self.env['stock.move'].create(scrap._prepare_move_values())
			# master: replace context by cancel_backorder
			move.with_context(is_scrap=True)._action_done()
			scrap.write({'move_id': move.id, 'state': 'done'})
		return True,reload

	def action_get_stock_picking(self):
		action = self.env.ref('stock.action_picking_tree_all').read([])[0]
		action['domain'] = [('id', '=', self.picking_id.id)]
		return action

	def action_get_stock_move_lines(self):
		action = self.env.ref('stock.stock_move_line_action').read([])[0]
		action['domain'] = [('move_id', '=', self.move_id.id)]
		return action

	def action_validate(self):
		reload = {'type':'ir.actions.client', 'tag': 'reload'}
		self.ensure_one()
		if self.product_id.type != 'product':
			return self.do_scrap()
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		available_qty = sum(self.env['stock.quant']._gather(self.product_id,
															self.location_id,
															self.lot_id,
															self.package_id,
															self.owner_id,
															strict=True).mapped('quantity'))
		scrap_qty = self.product_uom_id._compute_quantity(self.scrap_qty, self.product_id.uom_id)
		if float_compare(available_qty, scrap_qty, precision_digits=precision) >= 0:
			return self.do_scrap(), reload
		else:
			return {
				'name': _('Insufficient Quantity'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'stock.warn.insufficient.qty.scrap',
				'view_id': self.env.ref('stock.stock_warn_insufficient_qty_scrap_form_view').id,
				'type': 'ir.actions.act_window',
				'context': {
					'default_product_id': self.product_id.id,
					'default_location_id': self.location_id.id,
					'default_scrap_id': self.id
				},
				'target': 'new'
			}
