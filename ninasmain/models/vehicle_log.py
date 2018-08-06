#-*- coding: utf-8 -*-
#@author: Chuka
#Date: 2/08/2018

from odoo import fields, models, api
import datetime 

class VehicleLog(models.Model):
    _name='ninas.vehicle_log'
    _description='Vehicle Daily Log'

    serial_no=fields.Float(
        string='S/NO.'
        )
    date=fields.Date(
        string='Date'
        )
    vehicle_plate=fields.Char(
        string='Vehicle Plate Number'
         )
    fuel=fields.Float(
        string='Fuel Purchased (liters)'
        )
    meter=fields.Float(
            string='Meter Reading (KM)'
        ) 
    journey_from=fields.Char(
        string='Place Journey Commenced'
        )
    journey_to=fields.Char(
        string='Place Journey Ended'
        )
    daily_log=fields.One2many(
        comodel_name='vehicle.log',
        inverse_name='name',
        string='Vehicle Daily Log'
        )

    class vehicle_daily_log(models.Model):
        _name='vehicle.log'

        name= fields.Char(
            string="Name",
            required=1
        )
        employee_id=fields.Many2one(
            comodel_name='hr.employee',
            string='Driver'
        )
        time_in=fields.Datetime(
            string='Journey (Time in)'
        )
        time_out=fields.Datetime(
            string='Journey (Time out)'
        )    
        meter_in=fields.Datetime(
            string='Meter (Time in)'
        )
        meter_out=fields.Datetime(
            string='Meter (Time out)'
        )
        kilometers=fields.Float(
            string='K/M Used'
        )
        fuelunit=fields.Float(
            string='Fuel Unit'
        )
        purpose=fields.Selection(
            [('official','Official'),('personal','Personal')],
            string='Purpose of Journey'
        )
        destination=fields.Char(
            string='Destination'
        )
        passengers=fields.Char(
            string='Passengers Name'
        )