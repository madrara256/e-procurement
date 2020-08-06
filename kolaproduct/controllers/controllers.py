# -*- coding: utf-8 -*-
from odoo import http

# class Kolaproduct(http.Controller):
#     @http.route('/kolaproduct/kolaproduct/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kolaproduct/kolaproduct/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kolaproduct.listing', {
#             'root': '/kolaproduct/kolaproduct',
#             'objects': http.request.env['kolaproduct.kolaproduct'].search([]),
#         })

#     @http.route('/kolaproduct/kolaproduct/objects/<model("kolaproduct.kolaproduct"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kolaproduct.object', {
#             'object': obj
#         })