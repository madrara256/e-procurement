# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseCases(http.Controller):
#     @http.route('/purchase_cases/purchase_cases/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_cases/purchase_cases/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_cases.listing', {
#             'root': '/purchase_cases/purchase_cases',
#             'objects': http.request.env['purchase_cases.purchase_cases'].search([]),
#         })

#     @http.route('/purchase_cases/purchase_cases/objects/<model("purchase_cases.purchase_cases"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_cases.object', {
#             'object': obj
#         })