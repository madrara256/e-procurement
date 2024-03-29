# -*- coding: utf-8 -*-
# Part of System. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    picking_type_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + ", spt.warehouse_id as picking_type_id"

    def _from(self):
        return super(PurchaseReport, self)._from() + " left join stock_picking_type spt on (spt.id=s.picking_type_id)"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", spt.warehouse_id"
