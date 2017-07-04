{
    'name': 'Sale Delivery Report Extention',
    'summary': 'Delivery',
    'version': '1.0',
    'category': 'Sale',
    'website': '',
    'complexity': "normal",
    'sequence': 20,
    'description': """

""",

    # Dependencies
    'depends': ['sale', 'sale_stock','portal_sale'],
    'external_dependencies': {},

    'data': [
        'views/sale_order_view.xml',
        'report/sale_delivery_report.xml',
        'report/sale_quotation_report.xml',
        'report/picking_operation.xml',
        'report/sale_delivery_price_report.xml',
        'views/mail_template_data.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': True,
    'auto_install': False,
}
