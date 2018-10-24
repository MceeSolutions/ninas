# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time
import re
import hashlib
import requests
from bs4 import BeautifulSoup

TRANSFER_STATUS = [
    ('outgoing','Outgoing'),('sent','Sent'),
    ('received','Received'),('exception','Transfer Failed'),
    ('cancel','Cancelled')]

class GatewayConfig(models.Model):
    _name = 'gateway.config'
    _description = 'Gateway Config'

    name = fields.Char(string='Name of Bank',required=True)
    url = fields.Char(string='URL',required=True)
    access_code = fields.Char(string='Access Code',required=True)
    username = fields.Char(string='Username',required=True)
    password = fields.Char(string='Password',required=True)


class Banks(models.Model):
    _name = 'ninas.bank'
    _description = 'NiNAS Banks'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    sort_code = fields.Char(string='Sort Code', required=True)

class BulkTransfer(models.Model):
    _name = 'ninas.bulk.transfer'
    _description = 'NiNAS Bulk Bank Transfer'
    _inherit = ['mail.thread']

    name = fields.Char(string='Reference', track_visibility='onchange')
    payment_date = fields.Date(string='Payment Date', default=lambda *a: time.strftime("%Y-%m-%d"), required=True, track_visibility='onchange')
    remarks = fields.Char(string='Remarks', track_visibility='onchange')
    transfer_ids = fields.Many2many(comodel_name='ninas.bank.transfer', 
                        column1='bulk_transfer_id', column2='bank_tranfer_id',
                        rel='bulk_tranfer_rel', string='Transfer(s)')

    state = fields.Selection(TRANSFER_STATUS,string='Status',track_visibility='onchange', default='outgoing')


class BankTransfer(models.Model):
    _name = 'ninas.bank.transfer'
    _description = 'NiNAS Bank Transfer'
    _inherit = ['mail.thread']

    amount = fields.Float(string='Amount', required=True, track_visibility='onchange')
    payment_date = fields.Date(string='Payment Date', default=lambda *a: time.strftime("%Y-%m-%d"), required=True, track_visibility='onchange')
    name = fields.Char(string='Reference', track_visibility='onchange', required=True)
    remarks = fields.Char(string='Remarks', track_visibility='onchange')
    vendor_code = fields.Char(related='partner_id.code', string='Vendor Code', store=True, track_visibility='onchange')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', track_visibility='onchange')
    vendor_name = fields.Char(related='partner_id.name', string='Vendor Name', store=True, track_visibility='onchange')
    partner_bank = fields.Many2one(comodel_name='ninas.bank',string='Bank', track_visibility='onchange')
    vendor_acctnumber = fields.Char(string='Vendor Account Number', track_visibility='onchange')
    vendor_bankcode = fields.Char(related='partner_bank.sort_code', string='Vendor Bank Code', store=True, track_visibility='onchange')
    state = fields.Selection(TRANSFER_STATUS,string='Status',track_visibility='onchange', default='outgoing')
    log_ids = fields.One2many(comodel_name='ninas.bank.transfer.logs', inverse_name='bank_transfer_id', string='Log(s)')


    @api.multi
    def mark_outgoing(self):
        self.write({'state':'outgoing'})
    
    @api.multi
    def cancel(self):
        self.write({'state':'cancel'})
    
    @api.multi
    def check_status(self):
        gateway = self.env['gateway.config'].sudo().search([], limit=1)
        accesscode = gateway.access_code
        username = gateway.username
        password = gateway.password
        url = gateway.url

        for transfer in self:
            tr = self.escape("<TransactionRequeryRequest><TransRef>%s</TransRef></TransactionRequeryRequest>"%(transfer.name))
            body = """<?xml version="1.0" encoding="utf-8"?>
                        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fil="http://tempuri.org/GAPS_Uploader/FileUploader">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <fil:TransactionRequery>
                                <!--Optional:-->
                                <fil:xmlstring>%s</fil:xmlstring>
                                <!--Optional:-->
                                <fil:customerid>%s</fil:customerid>
                                <!--Optional:-->
                                <fil:username>%s</fil:username>
                                <!--Optional:-->
                                <fil:password>%s</fil:password>
                            </fil:TransactionRequery>
                        </soapenv:Body>
                        </soapenv:Envelope>"""%(tr, accesscode,username,password)
            print(body)
            
            headers = {'content-type': 'text/xml'}
                    
        response = requests.post(url,data=body,headers=headers)
        message = code = False
        print(response.text)
        if response.status_code == 200:            
            soup = BeautifulSoup(response.text, "lxml")
            try:
                transactionrequeryresult = soup.transactionrequeryresult.string
                result = BeautifulSoup(transactionrequeryresult, "lxml")
                code = result.code.string
                message = result.message.string
            except Exception as e:
                message = e
        
        for transfer in self:
            self.env['ninas.bank.transfer.logs'].create({
                'status_code':response.status_code,
                'response':response.text,
                'message':message,
                'code': code,
                'bank_transfer_id':transfer.id
            })
        if code in ['1007', '1006']:
            self.write({'state':'sent'})
        elif code in ['1000','1009']:
            self.write({'state':'received'})
        else:
            self.write({'state':'exception'})
        return
    
    @api.multi
    def transfer_funds(self):
        transactions = {}
        transactions = '<transactions>'
        for transfer in self:
            transactions += '<transaction>'
            try:
                date = transfer.payment_date.split('-')
                date = date[0]+'/'+date[1]+'/'+date[2]
            except:
                date = time.strftime("%Y/%m/%d")

            transactions += """
                            <amount>%s</amount>
                            <paymentdate>%s</paymentdate>
                            <reference>%s</reference>
                            <remarks>%s</remarks>
                            <vendorcode>%s</vendorcode>
                            <vendorname>%s</vendorname>
                            <vendoracctnumber>%s</vendoracctnumber>
                            <vendorbankcode>%s</vendorbankcode>
                            """%(transfer.amount or 0,
                                 date or '',
                                 transfer.name or '',
                                 transfer.remarks or '',
                                 transfer.vendor_code or '',
                                 transfer.vendor_name or '',
                                 transfer.vendor_acctnumber or '',
                                 transfer.vendor_bankcode or '',)
            transactions += '</transaction>'
        transactions += '</transactions>'
        filtered_transactions = self.filter(transactions)
        #print(filtered_transactions)

        transfer_request = self.get_transfer_request(filtered_transactions)
        #print(transfer_request)
        TYPE = ['single', 'bulk']
        self.transfers(transfer_request, TYPE[0])
        return


    def get_transfer_request(self, transactions):   
        gateway = self.env['gateway.config'].sudo().search([], limit=1)
        transdetails = '<transdetails>%s</transdetails>'%self.escape(transactions)
        accesscode = gateway.access_code
        username = gateway.username
        password = gateway.password
        url = gateway.url
        hash = hashlib.sha512()
        #print(transactions+accesscode+username+password)
        hash.update((transactions+accesscode+username+password).encode('utf-8'))
        hash = hash.hexdigest().upper()

        return {
            'transdetails':transdetails,
            'accesscode':accesscode,
            'username':username,
            'password':password,
            'hash':hash,
            'url':url
        }
    
    def escape(self, s):
        s = s.replace("<", "&lt;")
        s = s.replace(">", "&gt;")
        #s = s.replace("&", "&amp;")
        return s
    
    def filter(self, s):
        return re.sub('\s+', '', s)
    
    def transfers(self, transfer_request, type):
        url = transfer_request['url']   
        tr = transfer_request['transdetails']
        tr += """<accesscode>%s</accesscode>
                <username>%s</username>
                <password>%s</password>
                <hash>%s</hash>"""%(transfer_request['accesscode'],
                 transfer_request['username'],
                 transfer_request['password'],
                 transfer_request['hash'])
        
        headers = {'content-type': 'text/xml'}
        
        if type == 'single':
            body = """<?xml version="1.0" encoding="utf-8"?>
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fil="http://tempuri.org/GAPS_Uploader/FileUploader">
                    <soapenv:Header/>
                    <soapenv:Body>
                    <fil:SingleTransfers>
                    <!--Optional:-->
                    <fil:xmlRequest><![CDATA[<SingleTransfers>%s</SingleTransfers>]]></fil:xmlRequest>
                    </fil:SingleTransfers>
                    </soapenv:Body>
                    </soapenv:Envelope>"""%(tr)
        elif type == 'bulk':
            body = """<?xml version="1.0" encoding="utf-8"?>
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fil="http://tempuri.org/GAPS_Uploader/FileUploader">
                    <soapenv:Header/>
                    <soapenv:Body>
                    <fil:BulkTransfers>
                    <!--Optional:-->
                    <fil:xmlRequest><![CDATA[<BulkTransfers>%s</BulkTransfers>]]></fil:xmlRequest>
                    </fil:BulkTransfers>
                    </soapenv:Body>
                    </soapenv:Envelope>"""%(tr)
                    
        response = requests.post(url,data=body,headers=headers)
        message = code = False

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            try:
                if type == 'single':
                    singletransfersresult = soup.singletransfersresult.string
                    result = BeautifulSoup(singletransfersresult, "lxml")
                elif type == 'bulk':
                    bulktransfersresult = soup.bulktransfersresult.string
                    result = BeautifulSoup(bulktransfersresult, "lxml")
                code = result.code.string
                message = result.message.string
            except Exception as e:
                message = e
        
        for transfer in self:
            self.env['ninas.bank.transfer.logs'].create({
                'status_code':response.status_code,
                'response':response.text,
                'message':message,
                'code': code,
                'bank_transfer_id':transfer.id
            })
        if code in ['1100','1007']:
            self.write({'state':'sent'})
        elif code in ['1000','1009']:
            self.write({'state':'received'})
        else:
            self.write({'state':'exception'})
        return

class BankTransferLogs(models.Model):
    _name = 'ninas.bank.transfer.logs'
    _description = 'NiNAS Bank Transfer Logs'
    _order = 'create_date DESC'

    status_code = fields.Char(string='Status Code')
    code = fields.Char(string='Code')
    message = fields.Text(string='Message')
    response = fields.Text(string='Full Response')
    bank_transfer_id = fields.Many2one(comodel_name='ninas.bank.transfer', string='Bank Transfer')