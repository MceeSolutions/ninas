# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import Warning

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    bulk_transfer_id = fields.Many2one(comodel_name='ninas.bulk.transfer', string='Bulk Transfer')

    @api.multi
    def generate_bank_transfers(self):
        self.ensure_one()
        slips = self.slip_ids.filtered(lambda a: a.state=='draft')
        if slips:
            raise Warning('Cannot generate bulk transfer because some slips are still in draft state.')
        slips = self.slip_ids.filtered(lambda a: a.state=='done')
        if slips:
            if not self.bulk_transfer_id:
                bulk = self.env['ninas.bulk.transfer'].sudo().create({
                    'remarks':self.name})
                self.bulk_transfer_id = bulk.id
            
            for slip in slips:
                if not self.env['ninas.bank.transfer'].sudo().search([
                    ('remarks','=',slip.name),
                    ('partner_id','=',slip.employee_id.bank_account_id.partner_id.id),
                    ('communication','=',slip.number),
                    ('bulk_transfer_id','=',self.bulk_transfer_id.id)]):
                    
                    input_line_amounts = slip.input_line_ids.mapped('amount')
                    line_amounts = slip.line_ids.mapped('amount')
                    total_amount = sum(input_line_amounts + line_amounts)
                    transaction = self.env['ninas.bank.transfer'].sudo().create({
                        'currency_id':slip.contract_id.currency_id.id,
                        'amount': total_amount,
                        'remarks': slip.name,
                        'partner_id':slip.employee_id.bank_account_id.partner_id.id,
                        'communication':slip.number,
                        'bulk_transfer_id':self.bulk_transfer_id.id
                    })

                    transaction.get_default_account()
                    transaction.get_default_debit_account()