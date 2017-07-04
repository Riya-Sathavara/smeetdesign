{
    'name': 'Sale Invoice Report Extention',
    'summary' : '',
    'version': '1.0',
    'category': 'account',
    'website': '',
    'complexity': "normal",
    'sequence': 20,
    'description': """

""",

    # Dependencies
    'depends': ['account'],
    'external_dependencies': {},

    'data': [
        'report/sale_invoice_report_ext.xml',
        'security/ir.model.access.csv',
        'views/partner_view.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active':True,
    'auto_install': False,
}
