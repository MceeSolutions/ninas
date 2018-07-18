#-*- coding: utf-8 -*-
#@author: Chuka 
#Date: 18/07/2018

from odoo import fields, models

class CheckList(models.Model):
    _name = 'multea.checklist'

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
 
	