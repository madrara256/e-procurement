# -*- coding: utf-8 -*-
{
	'name': "kolacontract",

	'summary': """
		Contracts Management""",

	'description': """
		Contracts Management is tailored to meet all your company
		Contracts Management Processes from Contract Drafting to Renewal and finally
		Termination in a Simple Systematic and Precise Workflows
	""",

	'author': "kola Automation Systems",
	'website': "http://www.yourcompany.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'Uncategorized',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': [
		'base',
		'mail',
		'portal',
	],

	# always loaded
	'data': [
		'security/kolacontract_security.xml',
		'security/ir.model.access.csv',
		'views/kolacontract_views.xml',
		'views/templates.xml',
		'views/kolastages_views.xml',
		'views/res_partner_views.xml',
		'views/res_config_settings_views.xml',
		'views/kolacontract_terminate_views.xml',
		'views/kolaevaluate_views.xml',
		'views/rating_params_views.xml',

		'data/kolacontract_terminate_data.xml',
		'data/kolacontract_data.xml',
		'data/mail_template.xml',
		'data/terminate_mail_template.xml',

		'crons/cron_mail_template.xml',
		'crons/expiry_reminders_views.xml',

		'report/kolacontract_dashboard_views.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
	 'qweb': [
		'static/src/xml/*.xml',
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}
