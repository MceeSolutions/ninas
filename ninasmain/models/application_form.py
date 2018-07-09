
from odoo import api, fields, models

class ApplicationForm(models.Model):
    _name = 'ninas.application.form'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        string='Applicant’s Authorized Representative’s Name')
    applicant_rep_title = fields.Selection([('mr','Mr.'),('ms', 'Ms.'), ('mrs','Mrs.'), ('dr','DR.'), ('engr','Engr.'), ('prof','Prof.')],
        string='Authorized Representative’s Title')
    laboratory_legal_name = fields.Text(
        string="Laboratory’s Legal Name")
    laboratory_address= fields.Text(
        string='Laboratory Address (Number and Street, City, State and Country)')
    telephone_number = fields.Char(
        string='Telephone Numbers')
    email_address = fields.Char(
        string='Email Address(es) official for laboratory and alternate contact')
    mailing_address = fields.Char(
        string='Mailing Address (if different from the laboratory location – Number, Street, City, State, Country)')
    account = fields.One2many(
        comodel_name='application.account',
        inverse_name='contact_name',
        string="""
        Accounts: Enter the name, telephone number, and email address(es) of the staff member who will liaise with NiNAS
        for all financial matters.
        """)
    
    name_address_of_owners = fields.Text(
        string='Name and Address of Owners (applicable in the case of private ownership)')
    
    
    testing_lab = fields.Boolean(
        string='ISO/IEC 17025 Testing Laboratory')
    calibration_lab = fields.Boolean(
        string='ISO/IEC 17025 Calibration Laboratory')
    med_lab = fields.Boolean(
        string='ISO 15189: Medical Laboratory')
    
    tertiary_level_lab = fields.Boolean(
        string='Tertiary level lab/ Tests (>20)')
    secondary_level_lab = fields.Boolean(
        string='Secondary level lab 11-20 Tests')
    primary_level_lab = fields.Boolean(
        string='Primary level lab (1-10)')
    
    test = fields.One2many(
        comodel_name='test.method',
        inverse_name='test_name')
    
    lab_capabilities=fields.Text(
        string='Laboratory Capabilities:')
    num_of_lab_staff=fields.Text(
        string='Number of Laboratory Staff:')
    
    signed_by_authorized_rep = fields.Char(
        string='Signed by Authorized Representative:')
    place_and_date = fields.Char(
        string='Place and date:')
    print_name_below = fields.Char(
        string='Print Name below:')
    
    telephone = fields.Char(
        string='Telephone')
    fax = fields.Char(
        string='Fax')
    email = fields.Char(
        string='Email')
    
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
    