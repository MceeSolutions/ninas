# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

#

{
    'name': 'Ninas ToolKits',
    'summary': 'Ninas ToolKits',
    'Description': """
                        Ninas ToolKits
                   """,
    'author':'intelligenti.io',               
    'website': 'http://www.intelligenti.io',
    'category': 'ninas',
    'version':'11.0.0.0.22',
    'application': True,
    'insatallable': True,
    'auto-install': True,
        
    'depends': ['ninasmain'],
    'data':[
        'security/ir.model.access.csv',
        'views/toolkit_view.xml'
        ],    
}

