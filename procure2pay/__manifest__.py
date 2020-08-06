# -*- coding: utf-8 -*-
{
	'name': "procure2pay",

	'summary': """
		Short (1 phrase/line) summary of the module's purpose, used as
		subtitle on modules listing or apps.openerp.com""",

	'description': """
		Long description of module's purpose
	""",

	'author': "KolaPro",
	'website': "https://www.kolapro.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'Uncategorized',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base','kolacontract', 'kolarequisition','purchase','stock', 'budget_management'],

	# always loaded
	'data': [
		'security/security.xml',
		'security/ir.model.access.csv',
		'views/p2p_menu_views.xml',
		'views/procure2pay_views.xml',
		'views/templates.xml',
		'views/res_config_settings_views.xml',
		'views/kolacontract_views.xml',
		'views/kolarequisition_views.xml',
		'views/kolabudget_views.xml',
		'views/kolapurchase_views.xml',
		'views/dashboard_views.xml',
		#'views/kolainvoicing_views.xml',
		'views/kolainventory_views.xml',
		'views/procure_pay_onboarding_templates.xml',
		'report/p2p_purchase_report.xml',
		'views/dashboard_views.xml',

	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
	'qweb':[
		'static/src/xml/*',
	]
}
