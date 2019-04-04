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
    'version':'11.0.0.0.86',
    'application': True,
    'insatallable': True,
    'auto-install': True,

    'depends': ['hr_holidays', 'hr_recruitment', 'website', 'stock', 'mail', 'sale',
                'purchase', 'account_budget', 'helpdesk', 'hr_expense', 'hr_appraisal',
                'maintenance','website_helpdesk','website_helpdesk_form', 'hr_payroll',
                'payment'],
    'external_dependencies': {
        'python': [],
        'bin': []
        },
    'init_xml':[],
    'data':[
        'security/ninas_security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/helpdesk_view_template.xml',
        'views/helpdesk_views.xml',
        'views/stock_view.xml',
        'views/hr_views.xml',
        'views/application_form.xml',
        'views/website_ninas_hr_recruitment_template.xml',
        'report/ninas_conflict_interest_report_template.xml',
        'report/ninas_conflict_interest_report.xml',
        'report/ninas_code_conduct_report_template.xml',
        'report/ninas_code_conduct_report.xml',
        'controller/web_forms.xml',
        'views/views.xml'
        ],
    'css':[],
    'demo_xml':[],
    'test':[],            
    
    }
