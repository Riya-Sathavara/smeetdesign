# -*- coding: utf-8 -*-
# Copyright (C) iCreative Technologies.
{
    'name': 'Inherit Product ',
    'version': '1.0',
    'summary': '',
    'description': """

====================
        """,
    'author': 'iCreative Technologies',
    'category': '',
    'depends': ['product', 'sale', 'account', 'stock','purchase'],
    'installable': True,
    'qweb': ['static/src/xml/chatter.xml'],
    'data': [
        'view/inherit_product_view.xml',
        'view/sale_order_view.xml',
        'view/purchase_ext_view.xml',
        'view/invoice_view.xml',
        'view/stock_move_view.xml',
        'view/send_by_mail_ext.xml',
        'view/partner_view.xml',
        'wizard/delivery_cancel_wiz.xml',
        'wizard/product_history.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
}
