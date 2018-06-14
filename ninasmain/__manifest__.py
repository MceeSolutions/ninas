# -*- coding: utf-8 -*-

#@author steve
#Date: 4/06/18
#'views/instructor_view.xml',
{
    'name': 'Ninas',
    'summary': 'Ninas',
    'Description': """
                        Ninas
                   """,
    'author':'Mcee',               
    'website': 'https://mceesolutions.com',
    'category': 'Ninas',
    'version':'11.0.0.0.1',
    'application': True,
    'insatallable': True,
    'auto-install': False,
        
    'depends': ['base', 'hr', 'hr_holidays', 'hr_recruitment', 'website', 'stock', 'mail', 'sale', 'purchase', 'account_budget'],
    'external_dependencies': {
        'python': [],
        'bin': []
        },
    'init_xml':[],
    'data':[
        'data/data.xml',
        'views/stock_view.xml',
        'views/views.xml'
        ],
    'css':[],
    'demo_xml':[],
    'test':[],            
    
    }