# -*- coding: utf-8 -*-
import base64
import logging
import psycopg2
import werkzeug

from werkzeug import url_encode

from odoo.addons.mail.controllers.main import MailController
from odoo import http, api, registry, SUPERUSER_ID,_
from odoo.exceptions import AccessError
from odoo.http import request

_logging = logging.getLogger(__name__)

# controllers
class KolaRequisition(http.Controller):

	@http.route('/kolarequisition/validate1', type='http', auth='user', methods=['GET'])
	def kolarequisition_validate1(self, res_id, token):
		comparison, record, redirect = MailController._check_token_and_record_or_redirect('kola.requisition', int(res_id), token)
		if comparison and record:
			try:
				record.confirm_request()
			except Exception:
				return MailController._redirect_to_messaging()
		return redirect

	@http.route('/kolarequisition/validate2', type='http', auth='user', methods=['GET'])
	def kolarequisition_validate2(self, res_id, token):
		comparison, record, redirect = MailController._check_token_and_record_or_redirect('kola.requisition', int(res_id), token)
		if comparison and record:
			try:
				record.validate1_request()
			except Exception:
				return MailController._redirect_to_messaging()
		return redirect

	@http.route('/kolarequisition/validate', type='http', auth='user', methods=['GET'])
	def kolarequisition_validate(self, res_id, token):
		comparison, record, redirect = MailController._check_token_and_record_or_redirect('kola.requisition', int(res_id), token)
		if comparison and record:
			try:
				record.validate2_request()
			except Exception:
				return MailController._redirect_to_messaging()
		return redirect

	@http.route('/kolarequisition/order', type='http', auth='user', methods=['GET'])
	def kolarequisition_rfqs(self, res_id, token):
		comparison, record, redirect = MailController._check_token_and_record_or_redirect('kola.requisition', int(res_id), token)
		if comparison and record:
			try:
				record.validate_request()
			except Exception:
				return MailController._redirect_to_messaging()
		return redirect
