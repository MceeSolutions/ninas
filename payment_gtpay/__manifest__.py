# -*- coding: utf-8 -*-

{
    'name': 'GTPay Payment Acquirer',
    'category': 'Accounting',
    'summary': 'Payment Acquirer: GTPay Implementation',
    'version': '1.0',
    'author':'MCEE Business Solutions',               
    'website': 'https://mceesolutions.com',
    'contributors': [
        "Tosin Komolafe <tkomolafe@mceesolutions.com>, <komolafetosin@gmail.com>",
    ],
    'description': """GTPay Payment Acquirer""",
    'depends': ['ninasmain'],
    'data': [
        'views/payment_views.xml',
        'views/payment_gtpay_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
}
