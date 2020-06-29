# -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18
import datetime

from datetime import date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero

from dateutil.relativedelta import relativedelta

class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ['purchase.order']
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.partner_ref = self.partner_id.ref
    
    def _default_employee(self):
        self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)])
    
    @api.multi
    def _check_override(self):
        for self in self:
            for line in self.order_line:
                if line.need_override and line.override_budget == False:
                    self.need_override = True
                else:
                    self.need_override = False
          
    need_override = fields.Boolean ('Need Budget Override', compute= "_check_override", track_visibility="onchange")
    employee_id = fields.Many2one('hr.employee', 'Employee',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, default=_default_employee)
    approval_date = fields.Date(string='Manager Approval Date', readonly=True, track_visibility='onchange')
    manager_approval = fields.Many2one('res.users','Manager Approval Name', readonly=True, track_visibility='onchange')
    

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('submit', 'Manager Approval'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    
    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        return {}
    
    @api.multi
    def button_confirm(self):
        self.approval_date = date.today()
        self.manager_approval = self._uid
        self.write({'state': 'to approve'})
        return {}
        
            
        
'''
    @api.multi
    def _check_budget(self):
        override = False
        for line in self.order_line:
            self.env.cr.execute("""
                    SELECT * FROM crossovered_budget_lines WHERE
                    general_budget_id in (SELECT budget_id FROM account_budget_rel WHERE account_id=%s) AND
                    analytic_account_id = %s AND 
                    to_date(%s,'yyyy-mm-dd') between date_from and date_to""",
                    (line.account_id.id,line.account_analytic_id.id, line.order_id.date_order))
            result = self.env.cr.fetchone()
            if result:
                result = self.env['crossovered.budget.lines'].browse(result[0]) 
                if line.price_total > result.allowed_amount and line.override_budget == False:
                    override = True
                    line.write({'need_override': True})
            else:
                if line.override_budget == False:
                    override = True
                    line.write({'need_override': True})
        if override:
            group_id = self.env['ir.model.data'].xmlid_to_object('netcom.group_sale_account_budget')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Purchase Order {} needs a budget override".format(self.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return True

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft','submit', 'sent']:
                continue
            if self._check_budget() == False and self.need_override:
                return {}
            self.approval_date = date.today()
            self.manager_approval = self._uid
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True
'''       
class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ['purchase.order.line']
    
    def _default_analytic(self):
        return self.env['account.analytic.account'].search([('name','=','Netcom')])
    
    def _default_account(self):
        return self.product_id.property_account_expense_id
#     
#     @api.multi
#     @api.onchange('type')
#     def type_change(self):
#         self.product_id = False
    
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', default=_default_analytic)
    account_id = fields.Many2one('account.account', string='Account', domain = "[('user_type_id', '=', 'Expenses')]")
    need_override = fields.Boolean ('Need Budget Override', track_visibility="onchange")
    override_budget = fields.Boolean ('Override Budget', track_visibility="onchange")
    
    @api.multi
    def action_override_budget(self):
        self.write({'override_budget': True})
        if self.order_id.need_override == False:
            subject = "Budget Override Done, Purchase Order {} can be approved now".format(self.name)
            partner_ids = []
            for partner in self.order_id.message_partner_ids:
                partner_ids.append(partner.id)
            self.order_id.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            
class Inventory(models.Model):
    _name = "stock.inventory"
    _inherit = "stock.inventory"
    
    name = fields.Char(
        'Inventory Reference',
        readonly=True, required=True, default='New')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.inventory') or '/'
        return super(Inventory, self).create(vals)

class account_payment(models.Model):
    _inherit = "account.payment"
    
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'), ('approve', 'Approved'), ('reject', 'Rejected'),
                              ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled'), 
                              ('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")


    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_ceo')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        #subject = "Payment '{}' needs your approval".format(self.name)
        subject = "Payment needs your approval"
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        #return False
        return {}
    
    @api.multi
    def ceo_approval(self):
        if not self.user_has_groups('ninasmain.group_ceo'):
            raise UserError(_("Only CEO can approve expense"))
        self.write({'state': 'approve'})
        #subject = "Payment '{}' has been Approved".format(self.name)
        subject = "Payment has been Approved"
        partner_ids = []
        for partner in self.message_partner_ids:
            partner_ids.append(partner.id)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return {}
    
    @api.multi
    def ceo_reject(self):
        if not self.user_has_groups('ninasmain.group_ceo'):
            raise UserError(_("Only CEO can approve expense"))
        self.write({'state': 'approve'})
        #subject = "Payment '{}' was REJECTED".format(self.name)
        subject = "Payment was REJECTED"
        partner_ids = []
        for partner in self.message_partner_ids:
            partner_ids.append(partner.id)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return {}
    
    
    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'approve':
                raise UserError(_("Only an approved payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})
        return True
    

class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread', 'rating.mixin', 'mail.activity.mixin']
    
    state = fields.Selection([('draft', 'Unposted'), ('submit', 'Submitted'), 
                              ('approve', 'Approved'), ('reject', 'Rejected'), ('posted', 'Posted')], string='Status',
      required=True, readonly=True, copy=False, default='draft',
      help='All manually created new journal entries are usually in the status \'Unposted\', '
           'but you can set the option to skip that status on the related journal. '
           'In that case, they will behave as journal entries automatically created by the '
           'system on document validation (invoices, bank statements...) and will be created '
           'in \'Posted\' status.')
    
    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_ceo')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        #subject = "Payment '{}' needs your approval".format(self.name)
        subject = "Journal Entries needs your approval"
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        #return False
        return {}
    
    @api.multi
    def ceo_approval(self):
        if not self.user_has_groups('ninasmain.group_ceo'):
            raise UserError(_("Only CEO can approve journal entries"))
        self.write({'state': 'approve'})
        #subject = "Payment '{}' has been Approved".format(self.name)
        subject = "Journal Entries has been Approved"
        partner_ids = []
        for partner in self.message_partner_ids:
            partner_ids.append(partner.id)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return {}
    
    @api.multi
    def ceo_reject(self):
        if not self.user_has_groups('ninasmain.group_ceo'):
            raise UserError(_("Only CEO can approve journal entries"))
        self.write({'state': 'approve'})
        #subject = "Payment '{}' was REJECTED".format(self.name)
        subject = "Journal Entries was REJECTED"
        partner_ids = []
        for partner in self.message_partner_ids:
            partner_ids.append(partner.id)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return {}
    
    
class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice','mail.thread', 'utm.mixin', 'rating.mixin', 'mail.activity.mixin', 'portal.mixin']
    
    @api.onchange('accreditation_id')
    def _onchange_partner_id(self):
        self.partner_id = self.accreditation_id.partner_id
        return {}
    
    #ninas_partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
        #required=True, readonly=True, states={'draft': [('readonly', False)]},
        #track_visibility='always', related="accreditation_id.partner_id")
    
    accreditation_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Accreditation")
    
    date_invoice = fields.Date(string='Invoice Date', default = date.today(),
        readonly=True, states={'draft': [('readonly', False)]}, index=True,
        help="Keep empty to use the current date", copy=False)
    
    @api.model
    def create(self, vals):
        a = super(AccountInvoice, self).create(vals)
        a.send_created_message()
        return a
    
    @api.multi
    def send_created_message(self):
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_ceo')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "An invoice has been created and awaiting validation".format(self.number)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return False
    
    @api.multi
    def _onchange_send_validated_message(self):
        subject = "invoice has been validated {} ".format(self.number)
        partner_ids = []
        for partner in self.message_partner_ids:
            partner_ids.append(partner.id)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return {}
    
    @api.multi
    def onchange_send_paid_message(self):
        group_id = self.env['ir.model.data'].xmlid_to_object('account.group_account_invoice')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "Invoice {} has been paid".format(self.number)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return False
    
    @api.multi
    def invoice_validate(self):
        for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
            invoice.message_subscribe([invoice.partner_id.id])
        self._check_duplicate_supplier_reference()
        self._onchange_send_validated_message()
        self.action_invoice_sent()
        return self.write({'state': 'open'})
    
class ResourceCalendarLeaves(models.Model):
    _name = "resource.calendar.leaves"
    _inherit = ['resource.calendar.leaves','mail.thread', 'rating.mixin', 'mail.activity.mixin']
    
    @api.model
    def create(self, vals):
        a = super(ResourceCalendarLeaves, self).create(vals)
        a.send_created_message()
        return a
    
    @api.multi
    def send_created_message(self):
        employees = self.env['hr.employee'].search([])
        config = self.env['mail.template'].sudo().search([('name','=','Public Holiday')], limit=1)
        mail_obj = self.env['mail.mail']
        if config:
            values = config.generate_email(self.id)
            mail = mail_obj.create(values)
            if mail:
                for self in employees:
                    if self.active == True:
                        mail.send()
    
    
class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run','mail.thread', 'rating.mixin', 'mail.activity.mixin']
    _description = 'Payslip Batches'
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('close', 'Close'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    
    @api.multi
    def compute_all_sheets(self):
        self.slip_ids.compute_sheet()
        return True
    
    @api.multi
    def send_payslip_created_message(self):
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_ceo','ninasmain.group_admin_finance_officer')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "Payslip Batch {} has been created and needs approval".format(self.name)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return self.write({'state': 'submit'})
    
    @api.multi
    def close_payslip_run(self):
        self.slip_ids.action_payslip_done()
        subject = "Payslip Batch {} has been approved".format(self.name)
        partner_ids = []
        for partner in self.message_partner_ids:
            partner_ids.append(partner.id)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return self.write({'state': 'close'})
    
    
            
