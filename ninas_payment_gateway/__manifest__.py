# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'NiNAS Payment Gateway',
    'category': 'Human Resources',
    'sequence': 38,
    'website': '',
    'depends': [
        'hr_payroll_account', 'ninas_payroll','account_accountant','account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/gateway_security.xml',
        'views/sequence.xml',
        'views/partner.xml',
        'views/gateway_view.xml',
        'views/gateway_cron.xml',
        'views/payslip.xml'
    ],
}
