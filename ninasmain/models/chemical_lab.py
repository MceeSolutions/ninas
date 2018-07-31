#-*- coding: utf-8 -*-
#@author: Chuka 
#Date: 31/07/2018

from odoo import fields, models, api
import datetime

class ChemicalLab(models.Model):
    _name= 'ninas.chemical_lab'
    _description= 'Chemical Testing Laboratory'

    issue_no= fields.Date(
        string='Issue No. 1',
        required=1
    )
    institution= fields.Char(
        string= 'Name of Laboratory',
        required=1
    )
    address= fields.Char(
        string='Address of Laboratory',
        required=1
    )
    schedule_number= fields.Char(
        string='Schedule No.',
        required=1
    ) 
    valid_no= fields.Date(
        string='Valid To',
        required=1
    )
    chem_lab= fields.One2many(
        comodel_name='chem.lab',
        inverse_name='name',
        string='Chemical Laboratory'
    )

class Lab(models.Model):
    _name= 'chem.lab'

    name= fields.Char(
        string="Name",
        required=1
    )
    employee_id= fields.Many2one(
        comodel_name='hr.employee',
        string='',
        required=0
    )
    products= fields.Char(
        string='Materials/ Products Tested',
        required=1
    )
    tests= fields.Char(
        string='Type of Tests/ Property Measured /Range of Managements',
        required=1
    )
    standards= fields.Char(
        string='Standard Specifications',
        required=1
    )
    techniques= fields.Char(
        string='Techniques Used',
        required=1
    )
