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
            
class JobRec(models.Model):
    _inherit = "hr.job"

    state = fields.Selection([
        ('approve', 'Awaiting Approval'),
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='approve', help="Set whether the recruitment process is open or closed for this job position.")
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'recruit'})
        return {}
    
class JobApp(models.Model):
    _inherit = "hr.applicant"
    
    approved = fields.Boolean(
        string='Approved')
    
    @api.multi
    def button_approve(self):
        self.write({'approved':True})
        return {}   
    
class CreateInvoice(models.Model):
    _inherit = "helpdesk.ticket"
    
    type = fields.Selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Vendor Bill'),
            ('out_refund','Customer Credit Note'),
            ('in_refund','Vendor Credit Note'),
        ], readonly=True, index=True, change_default=True,
        default='out_invoice',
        track_visibility='always')
    
    invoice_count = fields.Integer(compute="_invoice_count", string="Invoices", store=False)
    checklist_count = fields.Integer(compute="_checklist_count",string="Checklist")
    car_count = fields.Integer(compute="_car_count",string="C.A.R")
    
    @api.depends('invoice_count')
    def _invoice_count(self):
        oe_invoice = self.env['account.invoice']
        for inv in self:
            invoice_ids = self.env['account.invoice'].search([('partner_id', '=', inv.partner_id.id)])
            invoices = oe_invoice.browse(invoice_ids)
            invoice_count = 0
            for inv_id in invoices:
                invoice_count+=1
            inv.invoice_count = invoice_count
        return True

    @api.depends('checklist_count')
    def _checklist_count(self):
        oe_checklist = self.env['checklist.ticket']
        for pa in self:
            domain = [('ticket_id', '=', pa.id)]
            pres_ids = oe_checklist.search(domain)
            pres = oe_checklist.browse(pres_ids)
            checklist_count = 0
            for pr in pres:
                checklist_count+=1
            pa.checklist_count = checklist_count
        return True
    
    @api.multi
    def _car_count(self):
        car_rep = self.env['car.report']
        for car in self:
            domain = [('ticket_id', '=', car.id)]
            car_ids = car_rep.search(domain)
            cars = car_rep.browse(car_ids)
            car_count = 0
            for ca in cars:
                car_count+=1
            car.car_count = car_count
        return True
    
    @api.onchange('stage_id')
    def _onchange_kanban_state(self):
        self.update({'kanban_state':'normal'})
        return {} 
    
    '''
    @api.multi
    def action_create_new(self):
        ctx = self._context.copy()
        model = 'account.invoice'
        ctx.update({'journal_type': self.type, 'default_type': 'out_invoice', 'type': 'out_invoice', 'default_journal_id': self.id})
        if ctx.get('refund'):
            ctx.update({'default_type':'out_refund', 'type':'out_refund'})
        view_id = self.env.ref('account.invoice_form').id
        return {
            'name': _('Create invoice/bill'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model,
            'view_id': view_id,
            'context': ctx,
        }
    '''
    
    @api.multi
    def action_create_new(self):
       """
       Method to open create customer invoice form
       """
       
       partner_id = self.partner_id
            
       view_ref = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
       view_id = view_ref[1] if view_ref else False
        
       res = {
           'type': 'ir.actions.act_window',
           'name': _('Customer Invoice'),
           'res_model': 'account.invoice',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': view_id,
           'target': 'current',
           'context': {'default_partner_id': partner_id.id}
       }
     
       return res
       
    '''
    @api.multi
    def action_create_new(self):
        self.write({'stage_id': 4})
        return {}
    '''
   
    @api.multi
    def open_customer_invoices(self):

        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Invoices'),
            'res_model': 'account.invoice',
            'view_mode': 'tree,kanban,form,pivot,graph',
            'domain':[('type','=','out_invoice')],
            'context': {'search_default_partner_id': self.partner_id.id}
        }

    
class Checklist(models.Model):
    _name = "checklist.ticket"
    
    ticket_id = fields.Many2one(comdel_name='helpdesk.ticket')
    
    partner_id = fields.Many2one('res.partner', string='Applicant')
    
    quality_manual = fields.Boolean(
        string='A copy of current version of Quality Manual',
      
    )
    procedures=fields.Boolean(
        string='Operating Procedures'
    )
    work_inst=fields.Boolean(
        string ='Work Instructions'
    )
    org_charts=fields.Boolean(
        string="Up-to-date Organisational Chart(with identity of key personnel involved in each function"
    )
    report_rela=fields.Boolean(
         string="If part of a larger organisation, include a chart of the laboratory’s position and reporting relationships within the organisation"
    )
    prof_testing=fields.Boolean(
        string="Proficiency testing plan and proficiency test results with any corrective action response (if applicable)"
    )
    list_equip=fields.Boolean(
        string="A list of all the equipment used to support the tests or calibrations including in-house (i.e. equipment calibrations that your lab performs) and external calibrations (i.e. those that an external calibration laboratory performs), and rented/borrowed equipment."
    )
    cali_cert=fields.Boolean(
        string="For Calibration Applicants Only: a sample of a calibration certificate which your laboratory issued and uncertainty calculations that support the Measurement Uncertainties to be claimed on your scope of accreditation."
    )
    evi_pay=fields.Boolean(
         string="Additional Requirement: Evidence of payment or funding support"
    )
    
    
class CarReport(models.Model):
    _name = 'car.report'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    name = fields.Char(string='Organization Name')
    ref_no = fields.Integer(string='Reference No:')
    faculty_rep = fields.Char(string='Name/Signature of Facility Representative:')
    scope_assessed = fields.Char(string='Scope Assessed:')
    rel_equip = fields.Char(string='Relevant Standard Requirement')
    name_lead =fields.Char(string='Name/Signature of Lead Assessor / Date')
    name_rep = fields.Char(string='Name /Signature of Representative/ Date')
    root_cause = fields.Text(string='(Root Cause Analysis)')
    corrective_action = fields.Text(string='Clearly indicate what corrective action was taken and attach supporting evidence')
    rep_sign = fields.Date(string='Signature of Representative/ Date')
    assessor_nc = fields.Text(string='Comment on the effectiveness of clearance of the NC')
    assessor_sign = fields.Date(string='Signature of Assessor/ Date')
    implemantation = fields.Text(string='Comment on the implementation of the corrective actions')
    sign_assessor = fields.Date(string='Signature of Assessor/ Date')
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
            
            
            
            