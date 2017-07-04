# -*- coding: utf-8 -*-
{
    'name': "Menu in Banner",

    'summary': """
        """,

    'description': """
    """,

    'author': "",
    'website': "",

    'category': '',
    'version': '',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup', 'bus', 'mail', 'crm_voip'],

    'qweb': [
            'static/src/xml/customer_counter.xml',
    ],
    'data': [
        'views/template.xml',
    ],
}
