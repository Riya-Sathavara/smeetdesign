# -*- coding: utf-8 -*-
{
    'name': "Smeets Sale Template",

    'summary': """
	Sale Email Template
      """,

    'description': """
        Inheritance Sale Order email template
    """,

    'author': "Icreative technolabs.com",
    'website': "http://www.odoo.com",

    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'website_quote', 'portal_sale', 'smt_delivery_report'],

    # always loaded
    'data': [
	'data/mail_template_data.xml',
    ],
}
