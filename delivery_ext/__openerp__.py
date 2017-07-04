# -*- coding: utf-8 -*-
# Copyright (C) iCreative Technologies.
{
    'name': 'Delivery extension ',
    'version': '1.0',
    'summary': '',
    'description': """

====================
        """,
    'author': 'iCreative Technologies',
    'category': '',
    'depends': ['delivery', 'sale',],
    'installable': True,
    'qweb': ['static/src/xml/chatter.xml'],
    'data': [
        'views/delivery_ext.xml',
    ],
    'application': True,
}
