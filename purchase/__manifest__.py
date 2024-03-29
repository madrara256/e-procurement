# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name': 'Purchase',
	'version': '1.2',
	'category': 'Purchases',
	'sequence': 60,
	'summary': 'Purchase orders, tenders and agreements',
	'description': "",
	'website': 'https://www.odoo.com/page/purchase',
	'depends': ['account'],
	'data': [
		'security/purchase_security.xml',
		'security/ir.model.access.csv',
		'views/account_invoice_views.xml',
		'views/purchase_task_views.xml',
		'data/purchase_data.xml',
		'report/purchase_reports.xml',
		'views/purchase_views.xml',
		'views/res_config_settings_views.xml',
		'views/product_views.xml',
		'views/res_partner_views.xml',
		'views/purchase_template.xml',
		'report/purchase_bill_views.xml',
		'report/purchase_report_views.xml',
		'data/mail_template_data.xml',
		#'report/report_paper_format.xml',
		'views/portal_templates.xml',

		'report/purchase_order_templates.xml',
		'report/purchase_quotation_templates.xml',
		'report/rfq_reports.xml',
		'report/rfq_report_template.xml',

		'data/purchase_order_line.xml',

		'wizard/add_approval_comments_views.xml',
		'wizard/add_refuse_reason_views.xml',
		'wizard/add_validation_comments_views.xml',
		'wizard/board_approval_views.xml',
		'wizard/procurement_approval_views.xml',
		'wizard/send_procurement_views.xml',


	],
	'demo': [
		'data/purchase_demo.xml',
	],
	'installable': True,
	'auto_install': False,
	'application': True,
}
