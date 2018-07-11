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
    'category': 'ninas',
    'version':'11.0.0.0.11',
    'application': True,
    'insatallable': True,
    'auto-install': True,
        
    'depends': ['base', 'hr', 'hr_holidays', 'hr_recruitment', 'website', 'stock', 'mail', 'sale',
                'purchase', 'account_budget', 'hr_payroll', 'helpdesk', 'hr_expense', 'hr_appraisal'],
    'external_dependencies': {
        'python': [],
        'bin': []
        },
    'init_xml':[],
    'data':[
        'security/ninas_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/helpdesk_views.xml',
        'views/stock_view.xml',
        'views/hr_views.xml',
        'views/application_form.xml',
        'views/views.xml'
        ],
    'css':[],
    'demo_xml':[],
    'test':[],            
    
    }
