# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'NiNAS Payroll Extend',
    'category': 'Human Resources',
    'sequence': 38,
    'website': '',
    'depends': [
        'ninasmain', 'hr_payroll',
    ],
    'data': [
        'views/hr_payslip_view.xml',
        'views/hr_payroll_report.xml',
        'views/report_ninaspayslipdetails_templates.xml',
    ],
}
