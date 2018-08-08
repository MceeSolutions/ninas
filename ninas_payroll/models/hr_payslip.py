#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_total(self, code):
        return self.env['hr.payslip.line'].search([('slip_id','=',self.id),('code','=',code)], limit=1).total

    @api.multi
    def write(self, values):
        super(HRPayslip, self).write(values)
        self.update_loan_request()
        return True
    
    @api.multi
    def update_loan_request(self):
        for payslip in self.filtered(lambda p: p.state == 'done'):
            inputLines = payslip.input_line_ids.filtered(lambda i: i.code.strip() == 'LOAN')
            if inputLines:
                loanRequest = self.env['loan.request'].sudo()
                for inputLine in inputLines:
                    amount_paid = inputLine.amount
                    if amount_paid > 0:
                        ln = loanRequest.search([('name','=',payslip.employee_id.id),('state','=','approve'),('balance','>',0.0)],limit=1)
                        for loan_line in ln.loan_line_ids:
                            if loan_line.loan_amount > loan_line.loan_paid:
                                amount_left = loan_line.loan_amount - loan_line.loan_paid
                                if amount_left < amount_paid:
                                    loan_line.write({'loan_paid':amount_left})
                                    amount_paid -= amount_left
                                else:
                                    loan_line.write({'loan_paid':amount_paid})
                                    break