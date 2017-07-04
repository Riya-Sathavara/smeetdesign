{
    'name': 'Purchase Order Report Extention',
    'summary' : '',
    'version': '1.0',
    'category': '',
    'website': '',
    'complexity': "normal",
    'sequence': 20,
    'description': """

""",

    # Dependencies
    'depends': ['purchase', 'portal_sale'],
    'external_dependencies': {},

    'data': [
        'report/purchase_order_report_ext.xml',
        'views/mail_template_data.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active':True,
    'auto_install': False,
}
