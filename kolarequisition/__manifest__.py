# -*- coding: utf-8 -*-
{
	'name': "kolarequisition",

	'summary': """
		Short (1 phrase/line) summary of the module's purpose, used as
		subtitle on modules listing or apps.openerp.com""",

	'description': """
		Long description of module's purpose
	""",

	'author': "Kola Technologies Limited",
	'website': "http://www.yourcompany.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'Uncategorized',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base','mail','stock', 'hr',],

	# always loaded
	'data': [
		'data/kolarequest_data.xml',
		'report/requisition_reports.xml',
		'data/kolarequest_mail_template.xml',
		'report/kola_requisition_templates.xml',
		'security/kola_requisition_security.xml',
		'security/ir.model.access.csv',
		'views/kolarequisition_menu_views.xml',
		'views/kola_request_views.xml',
		'views/templates.xml',
		'views/kolarequisitioncase_views.xml',
		'views/res_partner_views.xml',
		'views/kola_requisition_analysis_views.xml',

		'data/kolarequest_data.xml',
		'data/kolarequest_line.xml',
		'data/report_paperformat.xml',
		'report/requisition_report_views.xml',
		'report/kolaconsolidation_report_views.xml',
		'report/kolaconsolidate_report.xml',

		'wizard/kolaconsolidate_views.xml',
		'wizard/add_refuse_reason_views.xml',


	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
	"application":False,
	"installable":True,
}
