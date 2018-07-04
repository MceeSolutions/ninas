# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

#

{
    'name': 'Ninas Assessor ToolKit',
    'summary': 'Ninas Assessor ToolKit',
    'Description': """
                        Ninas Assessor ToolKit
                   """,
    'author':'intelligenti.io',               
    'website': 'http://www.intelligenti.io',
    'category': 'ninas',
    'version':'11.0.0.0.6',
    'application': True,
    'insatallable': True,
    'auto-install': True,
        
    'depends': ['ninasmain'],
    'data':[
        'security/ir.model.access.csv',
        'views/assessor_view.xml'
        ],    
}

