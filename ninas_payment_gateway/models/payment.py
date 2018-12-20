# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    @api.constrains('state')
    def create_transfer(self):
        for payment in self:
            if payment.state == 'posted' and payment.payment_type =='outbound' and payment.partner_type == 'supplier':
                transaction = self.env['ninas.bank.transfer'].sudo().create({
                    'currency_id':payment.currency_id.id,
                    'amount': payment.amount,
                    'remarks': payment.name,
                    'partner_id':payment.partner_id.id,
                    'communication':payment.communication
                })
                transaction.get_default_account()
                transaction.get_default_debit_account()