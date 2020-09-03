# -*- coding: utf-8 -*-
{
	'name': "purchase_cases",

	'summary': """
		Purchase Cases""",

	'description': """
		This module re-aligns the purchase approval process based on the amounts
	""",

	'author': "My Company",
	'website': "http://www.yourcompany.com",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'Uncategorized',
	'version': '0.1',

	# any module necessary for this one to work correctly
	'depends': ['base','purchase'],

	# always loaded
	'data': [
		'security/ir.model.access.csv',
		'views/purchase_case_views.xml',
		'views/templates.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
}
