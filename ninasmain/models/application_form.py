# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ApplicationForm(models.Model):
    _name = 'ninas.application.form'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        string='Applicantâ€™s Authorized Representativeâ€™s Name',
        track_visibility='onchange')
    applicant_rep_title = fields.Selection([('mr','Mr.'),('ms', 'Ms.'), ('mrs','Mrs.'), ('dr','DR.'), ('engr','Engr.'), ('prof','Prof.')],
        string='Authorized Representativeâ€™s Title',
        track_visibility='onchange')
    laboratory_legal_name = fields.Text(
        string="Laboratoryâ€™s Legal Name",
        track_visibility='onchange')
    laboratory_address= fields.Text(
        string='Laboratory Address (Number and Street, City, State and Country)',
        track_visibility='onchange')
    telephone_number = fields.Char(
        string='Telephone Numbers',
        track_visibility='onchange')
    email_address = fields.Char(
        string='Email Address(es) official for laboratory and alternate contact',
        track_visibility='onchange')
    mailing_address = fields.Char(
        string='Mailing Address (if different from the laboratory location â€“ Number, Street, City, State, Country)')
    account = fields.One2many(
        comodel_name='application.account',
        inverse_name='contact_name',
        string="""
        Accounts: Enter the name, telephone number, and email address(es) of the staff member who will liaise with NiNAS
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
    
    place_sign = fields.Char(
        string='Place:',
        track_visibility='onchange')
    place_date = fields.Date(
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
    
class Accounts(models.Model):
    _name = 'application.account'
    
    contact_name = fields.Char(
        string='Contact Name')
    telephone = fields.Char(
        string='Telephone')
    email = fields.Char(
        string='Email')
    alternate_email = fields.Char(
        string='Alternate Email')
    
    
class TestMethod(models.Model):
    _name = 'test.method'
    
    test_name = fields.Char(
        string='Name')
    test_method = fields.Char(
        string='Test Method Number Test')
    