#-*- coding: utf-8 -*-
#@author: Chuka
#Date: 2/08/2018

from odoo import fields, models, api
import datetime 

class VehicleLog(models.Model):
    _name='ninas.vehicle_log'
    _description='Vehicle Daily Log'

    serial_no=fields.Char(
        string='S/NO.',
        readonly=1, default="New"
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
    fuel_cost=fields.Float(
        string='Fuel Cost',
        default=(0)
        )
    meter=fields.Float(
            string='Meter Reading (KM)',
            default=(0)
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
    passenger_id=fields.Char(
            related='daily_log.passengers',
            string='Passenger',
            readonly=1
        )
    employee_id=fields.Char(
            related='daily_log.employees',
            string='Driver',
            readonly=1
        )

    @api.model
    def create(self, vals):
        if vals.get('serial_no', 'New') == 'New':
            vals['serial_no'] = self.env['ir.sequence'].next_by_code('ninas.vehicle_log') or '/'
        return super(VehicleLog, self).create(vals)


    class vehicle_daily_log(models.Model):
        _name='vehicle.log'

        name=fields.Char(
            string="Name",
            required=1
        )
        employees=fields.Char(
            comodel_name='hr.employee',
            string='Driver'
        )
        time_in=fields.Float(
            string='Journey (Time in)'
        )
        time_out=fields.Float(
            string='Journey (Time out)',
            digits=(2,2),
            default=(00.00)
        )    
        meter_in=fields.Float(
            string='Meter (in)',
            default=(0)
        )
        meter_out=fields.Float(
            string='Meter (out)',
            default=(0)
        )
        kilometers=fields.Float(
            compute="_subtract_",
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
            string='Passengers'
        )

        @api.multi
        def _subtract_(self):
            for num in self:
                kilometers = num.meter_in - num.meter_out
                num.kilometers = kilometers

       # @api.multi
        #def create_serial_num(self):
         #  serial = self.search([('id','!=',self.id),'|',('active','!=',False),
          #      ('active','=',False)], order='name DESC', limit=1)
           # if serial:
            #    previous_serial_num=serial.serial_no
             #   return 'V' + str(int(previous_serial_num[1:]+1))
              #  return 'V100001'
           
        