# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

#'security/ninas_security.xml',
#'security/ir.model.access.csv',

{
    'name': 'Ninas Accessor ToolKit',
    'summary': 'Ninas Accessor ToolKit',
    'Description': """
                        Ninas Accessor ToolKit
                   """,
    'author':'intelligenti.io',               
    'website': 'http://www.intelligenti.io',
    'category': 'ninas',
    'version':'11.0.0.0.0',
    'application': True,
    'insatallable': True,
    'auto-install': True,
        
    'depends': ['ninasmain'],
    'data':[
        'views/accessor_view.xml'
        ],    
}

