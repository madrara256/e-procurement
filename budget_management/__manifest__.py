# -*- coding: utf-8 -*-
{
	'name': "kolabudget",

	'summary': """
		Short (1 phrase/line) summary of the module's purpose, used as
		subtitle on modules listing or apps.openerp.com""",

	'description': """
		Long description of module's purpose
	""",

	'author': "Kola Automation Systems",
	'website': "http://www.yourcompany.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'Uncategorized',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base','mail','stock', 'kolarequisition','hr',],

	# always loaded
	'data': [
		'security/security.xml',
		'security/ir.model.access.csv',

		'views/templates.xml',
		'views/kolabudget_menu.xml',
		'data/mail_template.xml',
		'views/kolabudget_views.xml',
		'views/loan_forecasts_views.xml',
		'views/savings_forecasts_views.xml',
		'views/staffing_forecasts_views.xml',
		'views/manpower_forecasts_views.xml',
		'views/res_config_settings_views.xml',
		'views/team_views.xml',
		'views/budget_guidelines_views.xml',
		'report/budget_activity_views.xml',
		'data/budget_config_data.xml',
		'report/budget_reports.xml',
		'report/budget_templates.xml',
		'views/assets.xml',
		'views/templates.xml',
		'data/budgets_data.xml',
		#'data/budget_line_data.xml',
		#'data/ir_ui_views.xml',


	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
	'qweb':[
		'static/src/xml/*',
	]
}
