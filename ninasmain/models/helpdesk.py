 # -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18

import datetime

from datetime import date, timedelta
from odoo import api, fields, models
from datetime import *
from dateutil.relativedelta import *
#from gevent._ssl3 import name
#from plainbox.impl.unit import file
from ast import literal_eval
from odoo.exceptions import ValidationError, Warning

class Accreditation(models.Model):
    _inherit = 'helpdesk.ticket'
    
    current_date = date.today() + relativedelta(years=2)
    
    attachment_ids = fields.Many2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'helpdesk.ticket')], string='Attachments')

    assessment_team_ids = fields.Many2many(comodel_name='hr.employee',
                                     string='Assessment Team')
    
    assessment_type_id = fields.Many2one(
        comodel_name='assessment.type',
        string='Assesment Type',
        track_visibility='onchange')
    
    assessment_plan_id = fields.Many2one(
        comodel_name='ninas.assessment_plan',
        string='Assesment Plan',
        track_visibility='onchange')

    
    funding = fields.Selection(
        [('not_funded','Not Funded'),('partly_funded', 'Partly Funded'),('fully_funded', 'Fully Funded')],
        string='Funding',
        default='not_funded',
        track_visibility='onchange')
    
    funding_company_name = fields.Char(
        string='Company Name',
        track_visibility='onchange')
    
    funding_company_rep = fields.Char(
        string='Company Representative Name',
        track_visibility='onchange')
    
    funding_company_rep_num = fields.Char(
        string='Company Representative Number',
        track_visibility='onchange')
    
    
    lead_assessor_id = fields.Many2one(comodel_name='hr.employee', string='Lead Assessor', track_visibility='onchange',)
    tech_assessor_id = fields.Many2one(comodel_name='hr.employee', string='Technical Assessor', track_visibility='onchange',)
    
    ac_members= fields.Many2many(comodel_name='res.users',
                                 string='AC Members')
    
    re_assessment_date = fields.Date(string='Re-Assessment Date', track_visibility='onchange')
    
    creation_date = fields.Date(default = date.today() , string='Application Date')
    
    resources_available = fields.Boolean(string='Resources Available?', track_visibility='onchange')
    checklist_sent = fields.Boolean(string='Review Checklist Filled?', track_visibility='onchange')
    checklist_id = fields.Many2one(comodel_name='checklist.ticket', string='Review Checklist Filled?', track_visibility='onchange')
    conflict_agreement = fields.Boolean(string='contract Agreement?', readonly=True, track_visibility='onchange')
    confidentiality_agreement = fields.Boolean(string='confidentiality Agreemnt?', readonly=True, track_visibility='onchange')
    preassessment_needed = fields.Boolean(string='pre-assessment Needed?', track_visibility='onchange')
    document_review = fields.Selection([('yes', 'Yes.')],
                                       string='Document(s) Reviewed?', track_visibility='onchange')
    assessment_date = fields.Date(string='Assessment Date', related='assessment_plan_id.assessment_date', track_visibility='onchange', readonly=True)
    
    
    #Application Form Sheet
    name_applicant = fields.Char(
        string='Applicant’s Authorized Representative’s Name',
        track_visibility='onchange')
    applicant_rep_title = fields.Selection([('mr','Mr.'),('ms', 'Ms.'), ('mrs','Mrs.'), ('dr','DR.'), ('engr','Engr.'), ('prof','Prof.')],
        string='Authorized Representative’s Title',
        track_visibility='onchange')
    laboratory_legal_name = fields.Char(
        string="Laboratory’s Legal Name",
        track_visibility='onchange')
    
    laboratory_address= fields.Char(
        string='Laboratory Address',
        track_visibility='onchange')
    
    lab_number = fields.Char(
        string='Number')
    lab_street = fields.Char(
        string='Street')
    lab_city = fields.Char(
        string='City')
    lab_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    lab_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    
    telephone_number = fields.Char(
        string='Telephone Numbers',
        track_visibility='onchange')
    email_address = fields.Char(
        string='Email Address(es) official for laboratory and alternate contact',
        track_visibility='onchange')
    mailing_address = fields.Char(
        string='Mailing Address (if different from the laboratory location)')
    
    mail_number = fields.Char(
        string='Number')
    mail_street = fields.Char(
        string='Street')
    mail_city = fields.Char(
        string='City')
    mail_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    mail_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    
    account = fields.One2many(
        comodel_name='application.account',
        inverse_name='contact_name',
        string="""
        Accounts: Enter the details of the staff member who will liaise with NiNAS
        for all financial matters.
        """, track_visibility='onchange')
    
    name_address_of_owners = fields.Text(
        string='Name and Address of Owners (applicable in the case of private ownership)',
        track_visibility='onchange')
    
    
    testing_lab = fields.Boolean(
        string='ISO/IEC 17025 Testing Laboratory', 
        track_visibility='onchange')
    calibration_lab = fields.Boolean(
        string='ISO/IEC 17025 Calibration Laboratory',
        track_visibility='onchange')
    med_lab = fields.Boolean(
        string='ISO 15189: Medical Laboratory',
        track_visibility='onchange')
    
    tertiary_level_lab = fields.Boolean(
        string='Tertiary level lab/ Tests (>20)',
        track_visibility='onchange')
    secondary_level_lab = fields.Boolean(
        string='Secondary level lab 11-20 Tests',
        track_visibility='onchange')
    primary_level_lab = fields.Boolean(
        string='Primary level lab (1-10)',
        track_visibility='onchange')
    
    number_of_scopes = fields.Selection(
        [('above_20','(>20)'),('11_to_20', '11-20'),('1_to_10', '(1-10)')],
        string='Number of Scopes',
        track_visibility='onchange')
    
    
    test = fields.One2many(
        comodel_name='test.method',
        inverse_name='test_name',
        track_visibility='onchange')
    
    lab_capabilities=fields.Text(
        string='Laboratory Capabilities:', 
        track_visibility='onchange')
    num_of_lab_staff=fields.Text(
        string='Number of Laboratory Staff:', 
        track_visibility='onchange')
    
    signed_by_authorized_rep = fields.Char(
        string='Signed by Authorized Representative:',
        track_visibility='onchange')
    
    place_and_date = fields.Char(
        string='Place:',
        track_visibility='onchange')
    
    place_sign = fields.Char(
        string='Place:',
        track_visibility='onchange')
    place_date = fields.Char(
        string='Date:',
        track_visibility='onchange')
    
    print_name_below = fields.Char(
        string='Print Name below:',
        track_visibility='onchange')
    
    telephone = fields.Char(
        string='Telephone',
        track_visibility='onchange')
    fax = fields.Char(
        string='Fax',
        track_visibility='onchange')
    email = fields.Char(
        string='Email',
        track_visibility='onchange')
    
    mobile_app_attachment_ids = fields.One2many(
        comodel_name = 'mobile.app.attachment',
        inverse_name = 'ticket_id',
        string='Mobile App Attachment',
        track_visibility='onchange',
        help='Attachments from the NiNAS Mobile app will be seen and accessible from here')
    
class Accounts(models.Model):
    _name = 'application.account'
    
    contact_name = fields.Char(
        string='Contact Name', required=True)
    telephone = fields.Char(
        string='Telephone', required=True)
    email = fields.Char(
        string='Email', required=True)
    alternate_email = fields.Char(
        string='Alternate Email')
    
    
class TestMethod(models.Model):
    _name = 'test.method'
    
    test_name = fields.Char(
        string='Name', required=True)
    test_method = fields.Char(
        string='Test Method Number Test', required=True)
    


class AssessmentType(models.Model):
    _name = 'assessment.type'
    
    name = fields.Char(string='Assessment Type')
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='ninas_assessment_type_rel',
        column1='assessment_type_id',
        column2='attachment_id',
        string='Attachment')
    

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
    checklist_count = fields.Integer(compute="_checklist_count",string="Checklist", store=False)
    car_count = fields.Integer(compute="_car_count",string="C.A.R")
    
    @api.multi
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

    @api.multi
    def _checklist_count(self):
        oe_checklist = self.env['checklist.ticket']
        for pa in self:
            domain = [('partner_id', '=', pa.partner_id.id)]
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
    def action_create_new_invoice(self):
       """
       Method to open create customer invoice form
       """
       
       partner_id = self.partner_id
            
       view_ref = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
       view_id = view_ref[1] if view_ref else False
        
       res = {
           'type': 'ir.actions.act_window',
           'name': ('Customer Invoice'),
           'res_model': 'account.invoice',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': view_id,
           'target': 'current',
           'context': {'default_partner_id': partner_id.id}
       }
     
       return res
    
    @api.multi
    def invoice_prompt(self):
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_admin_finance_officer')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "An invoice is required for {}".format(self.name)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return False
    
    @api.multi
    def send_invoice_prompt_mail(self):
        config = self.env['mail.template'].sudo().search([('name','=','Invoice Prompt for Accreditation')], limit=1)
        mail_obj = self.env['mail.mail']
        if config:
            values = config.generate_email(self.id)
            mail = mail_obj.create(values)
            if mail:
                mail.send()
    
    '''
    @api.multi
    def open_customer_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_refund_out_tree').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.id))
        return action
    
    
    '''
    @api.multi
    def open_customer_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': ('Customer Invoices'),
            'res_model': 'account.invoice',
            'view_mode': 'tree,kanban,form,pivot,graph',
            'domain':[('type','=','in_invoice')],
            'target': 'current',
            'context': {'search_default_is_open': True, 'search_default_partner_id': self.partner_id.id}
        }
    
        
    @api.multi
    def open_checklist_ticket(self):
        return {
            'type': 'ir.actions.act_window',
            'name': ('Checklist'),
            'res_model': 'checklist.ticket',
            'view_mode': 'tree,kanban,form,pivot,graph',
            'target': 'current',
            'context': {'search_default_is_open': True, 'search_default_partner_id': self.partner_id.id}
        }
    
    
    @api.multi
    def button_confirm_sponsor(self):
        self.write({'stage_id': 5})
        return {}
    
    @api.multi
    def button_complete_approved(self):
        if self.resources_available == False:
            raise Warning('Resources are not available')
        else:
            self.invoice_prompt()
            self.send_invoice_prompt_mail()
            self.write({'stage_id': 3})
        return True
    
    @api.multi
    def button_complete_reject(self):
        self.write({'stage_id': 1})
        return {}
    
    @api.multi
    def button_complete_approve(self):
        self.write({'stage_id': 5})
        return {}
    
    @api.multi
    def confirm_funding(self):
        if self.funding not in ['fully_funded'] or self.invoice_count == 0:
            raise Warning('No invoice has been generated for this Application')
        else:
            self.write({'stage_id': 9})
        return {}
    
    @api.multi
    def confirmed_funding(self):
        self.write({'stage_id': 9})
        return {}
    
    @api.multi
    def action_resources_available(self):
        if self.resources_available == False:
            raise Warning('You must set Assessment Team And Lead Assessor!')
        else:
            self.write({'resources_available': True})
            self.write({'stage_id': 10})
        return {}
    
    @api.multi
    def action_checklist_sent(self):
        if self.checklist_count == 0:
            raise Warning('You must review the CheckList First!')
        else:
            self.write({'checklist_sent': True})
            self.write({'stage_id': 9})
        return {}
    
    
    @api.multi
    def button_assessor_agreement(self):
        self.write({'conflict_agreement': True})
        self.write({'confidentiality_agreement': True})
        self.write({'stage_id': 17})
        return {}
    
   
    @api.multi
    def button_ready_assessment(self):
        self.write({'stage_id': 19})
        return {}
    
    @api.multi
    def button_assessment_plan(self):
        self.write({'stage_id': 12})
        return {}
    
    @api.multi
    def button_assessment(self):
        self.write({'stage_id': 11})
        return {}
    
    
    
    @api.multi
    def button_car(self):
        self.write({'stage_id': 13})
        return {}
    
    @api.multi
    def button_decision_making(self):
        self.write({'stage_id': 16})
        return {}
    
    @api.multi
    def button_awaiting_approval(self):
        self.write({'stage_id': 20})
        return {}
    
    
    
    
    
    @api.multi
    def button_approved_app(self):
        current_date = date.today() + relativedelta(years=2)
        self.re_assessment_date = current_date
        self.write({'stage_id': 21})
        return {}
    
    @api.multi
    def button_reject_app(self):
        self.write({'stage_id': 18})
        return {}
    
#    @api.multi
#    def button_pending_closure(self):
#        self.write({'stage_id': 18})
#        return {}
    
    @api.multi
    def button_reset_app(self):
        self.write({'stage_id': 20})
        return {}
    
    @api.multi
    def button_closed(self):
        self.write({'stage_id': 4})
        return {}
    
    
class Checklist(models.Model):
    _name = "checklist.ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    ticket_id = assessment_type_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Application ID',
        track_visibility='onchange')
    
    partner_id = fields.Many2one(comodel_name='res.partner', related='ticket_id.partner_id', string='Applicant')
    
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
    
    @api.multi
    def button_select_all(self):
        self.write({'quality_manual': True})
        self.write({'procedures': True})
        self.write({'work_inst': True})
        self.write({'org_charts': True})
        self.write({'report_rela': True})
        self.write({'prof_testing': True})
        self.write({'list_equip': True})
        self.write({'cali_cert': True})
        self.write({'evi_pay': True})
        return {}
    
    pre_assessment_needed = fields.Boolean(
        string="pre-assessment Needed?"
    )
    no_of_assessor = fields.Char(string="Estimated Number of Assessors")
    assessment_days = fields.Integer(string="Estimated Number of Days")
    
class CarReport(models.Model):
    _name = 'car.report'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    name = fields.Char(string='Organization Name')
    ref_no = fields.Integer(string='Reference No:')
    faculty_rep = fields.Char(string='Name/Signature of Facility Representative:')
    scope_assessed = fields.Char(string='Scope Assessed:')
    rel_equip = fields.Text(string='Relevant Standard Requirement')
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
    
    attachment_count = fields.Integer(compute="_car_count",string="C.A.R")
    
    @api.multi
    def _car_count(self):
        car_rep = self.env['car.report.attachment']
        for car in self:
            domain = [('ticket_id', '=', car.id)]
            car_ids = car_rep.search(domain)
            cars = car_rep.browse(car_ids)
            car_count = 0
            for ca in cars:
                car_count+=1
            car.car_count = car_count
        return True
    
class CarReportAttachment(models.Model):
    _name = 'car.report.attachment'
    
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
    name = fields.Char(string='Attachment Name')
    attachment_description = fields.Char(string='Attachment Description')
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string='Attachment')
    
class MobileAppAttachment(models.Model):
    _name = 'mobile.app.attachment'
    
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
    name = fields.Char(string='Attachment Name')
    attachment_description = fields.Char(string='Attachment Description')
    attachment_image = fields.Binary(
        attachment=True, store=True,
        string='Attachment')
    
class account_payment(models.Model):
    _inherit = "account.payment"
    
    @api.multi
    def send_register_payment_mail(self):
        config = self.env['mail.template'].sudo().search([('name','=','Register Payment Notification')], limit=1)
        mail_obj = self.env['mail.mail']
        if config:
            values = config.generate_email(self.id)
            mail = mail_obj.create(values)
            if mail:
                mail.send()
    
    def action_validate_invoice_payment(self):
        """ Posts a payment used to pay an invoice. This function only posts the
        payment by default but can be overridden to apply specific post or pre-processing.
        It is called by the "validate" button of the popup window
        triggered on invoice form by the "Register Payment" button.
        """
        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        self.send_register_payment_mail()
        return self.post()
    

    
    