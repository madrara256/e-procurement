# -*- coding: utf-8 -*-
from odoo.addons.mail.controllers.main import MailController
from odoo import http

class Kolacontract(http.Controller):
	@http.route('/kolacontract/approve', type='http', auth='user', method=['GET'])
	def kolcontract_approve(self, res_id, token):
		comparison, record, redirect = MailController._check_token_and_record_or_redirect('kola.contract', int(res_id), token)
		if comparison and record:
			try:
				record.approve_contract()
			except Exception:
				raise MailController._redirect_to_messaging()
		return redirect

	@http.route('/kolacontract/reject', type='http', auth='user', method=['GET'])
	def kolacontract_refuse(self, res_id, token):
		comparison, record, redirect = MailController._check_token_and_record_or_redirect('kola.contract',int(res_id), token)
		if comparison and record:
			try:
				record.cancel_drafted_contract()
			except Exception:
				raise MailController._redirect_to_messaging()
		return redirect

	@http.route('/kolacontract/terminate', type='http', auth='user', method=['GET'])
	def kolcontract_terminate(self, res_id, token):
		comparison, record, redirect = MailController._check_token_and_record_or_redirect('kola.contract', int(res_id), token)
		if comparison and record:
			try:
				record.cancel_contract()
			except Exception:
				raise MailController._redirect_to_messaging()
		return redirect
