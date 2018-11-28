# -*- coding: utf-8 -*-

from odoo import api, fields, models
import time
import re
import hashlib
import requests
from bs4 import BeautifulSoup
from odoo.exceptions import Warning

TRANSFER_STATUS = [
    ('outgoing','Outgoing'),
    ('approve','Approved'),
    ('sent','Sent'),
    ('received','Received'),
    ('exception','Transfer Failed'),
    ('cancel','Cancelled')]

def escape(s):
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    #s = s.replace("&", "&amp;")
    return s
    
def filter(s):
    return re.sub('\s+', '', s)

class GatewayConfig(models.Model):
    _name = 'gateway.config'
    _description = 'Gateway Config'

    name = fields.Char(string='Name of Bank',required=True)
    url = fields.Char(string='URL',required=True)
    access_code = fields.Char(string='Access Code',required=True)
    username = fields.Char(string='Username',required=True)
    password = fields.Char(string='Password',required=True)


class Banks(models.Model):
    _inherit = 'res.bank'

    code = fields.Char(string='Code', required=True)

class BulkTransfer(models.Model):
    _name = 'ninas.bulk.transfer'
    _description = 'NiNAS Bulk Bank Transfer'
    _inherit = ['mail.thread']
    _order = 'name DESC'

    name = fields.Char(string='Reference', track_visibility='onchange', copy=False)
    payment_date = fields.Date(string='Payment Date', default=lambda *a: time.strftime("%Y-%m-%d"), required=True, track_visibility='onchange')
    remarks = fields.Char(string='Remarks', track_visibility='onchange')   
    transfer_ids = fields.One2many(comodel_name='ninas.bank.transfer', inverse_name='bulk_transfer_id', string='Transfer(s)', copy=False)
    log_ids = fields.One2many(comodel_name='ninas.bank.transfer.logs', inverse_name='bulk_transfer_id', string='Log(s)', copy=False)
    state = fields.Selection(TRANSFER_STATUS,string='Status',track_visibility='onchange', default='outgoing', copy=False)
    debit_account_id = fields.Many2one(comodel_name='account.journal', string='Debit Account', required=False, track_visibility='onchange', domain=[('type','=','bank')])


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('ninas.bulk.transfer')
        return super(BulkTransfer, self).create(values)
    
    @api.multi
    def mark_outgoing(self):
        self.write({'state':'outgoing'})
        self.transfer_ids.filtered(lambda t: t.state not in ['received', 'cancel']).write({'state':'outgoing'})
    
    @api.multi
    def reset(self):
        self.write({'state':'outgoing'})
        self.transfer_ids.filtered(lambda t: t.state not in ['received', 'cancel']).write({'state':'outgoing'})
    
    @api.multi
    def approve(self):
        self.write({'state':'approve'})
        self.transfer_ids.filtered(lambda t: t.state not in ['received', 'cancel']).write({'state':'approve'})
    
    @api.multi
    @api.depends('payment_date')
    def onchange_payment_date(self):
        for bulk in self:
            bulk.transfer_ids.filtered(lambda t: t.state in ['outgoing']).write({'payment_date':bulk.payment_date})
    
    @api.multi
    def cancel(self):
        self.write({'state':'cancel'})
    
    @api.multi
    def transfer_funds(self):
        for bulk in self:
            if bulk.transfer_ids:
                bulk.transfer_ids.transfer_funds()
                bulk.env.cr.commit()
                states = bulk.transfer_ids.mapped('state')
                states_dict = {x:states.count(x) for x in states}
                #print(states_dict)
                states, frequency = list(states_dict.keys()), list(states_dict.values())
                self.write({'state':states[frequency.index(max(frequency))]})
                
            else:
                raise Warning('Nothing to transfer!')


class BankTransfer(models.Model):
    _name = 'ninas.bank.transfer'
    _description = 'NiNAS Bank Transfer'
    _inherit = ['mail.thread']
    _order = 'name DESC'
    _sql_constraints = [('check_amount', 'CHECK (amount > 0)', 'Amount must be greater than zero!')]


    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id', track_visibility='onchange')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', required=True, track_visibility='onchange')
    payment_date = fields.Date(string='Payment Date', default=lambda *a: time.strftime("%Y-%m-%d"), required=True, track_visibility='onchange')
    name = fields.Char(string='Reference', track_visibility='onchange', required=False, copy=False)
    remarks = fields.Char(string='Remarks', track_visibility='onchange')
    communication = fields.Char(string='Memo', track_visibility='onchange')
    vendor_code = fields.Char(related='partner_id.code', string='Vendor Code', store=True, track_visibility='onchange')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', track_visibility='onchange', required=True)
    vendor_name = fields.Char(related='partner_id.name', string='Vendor Name', store=True, track_visibility='onchange')
    partner_bank = fields.Many2one(comodel_name='res.bank',string='Bank', track_visibility='onchange', required=False)
    vendor_acct_id = fields.Many2one(comodel_name='res.partner.bank',string='Vendor Account Number', required=False, track_visibility='onchange')
    vendor_acctnumber = fields.Char(related='vendor_acct_id.acc_number', track_visibility='onchange', store=True)
    vendor_bankcode = fields.Char(related='partner_bank.bic', string='Vendor Bank Code', store=True, track_visibility='onchange')
    state = fields.Selection(TRANSFER_STATUS,string='Status',track_visibility='onchange', default='outgoing', copy=False)
    log_ids = fields.One2many(comodel_name='ninas.bank.transfer.logs', inverse_name='bank_transfer_id', string='Log(s)', copy=False)
    bulk_transfer_id = fields.Many2one(comodel_name='ninas.bulk.transfer', string='Bulk Transfer', track_visibility='onchange')
    debit_account_id = fields.Many2one(comodel_name='account.journal', string='Debit Account', required=False, track_visibility='onchange', domain=[('type','=','bank')])
    debit_acctnumber = fields.Char(related='debit_account_id.bank_account_id.acc_number', track_visibility='onchange', store=True)
    bank_ids = fields.Many2many(comodel_name='res.bank', compute='_get_banks', track_visibility='onchange')

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('ninas.bank.transfer')
        return super(BankTransfer, self).create(values)
    
    @api.multi
    def mark_outgoing(self):
        self.write({'state':'outgoing'})
    
    @api.multi
    def approve(self):
        self.write({'state':'approve'})
    
    @api.multi
    def cancel(self):
        self.write({'state':'cancel'})
    

    @api.multi
    def _get_banks(self):
        for transfer in self:
           if transfer.currency_id and transfer.partner_id:
                bank_ids = transfer.partner_id.bank_ids.filtered(lambda b: b.currency_id.id == transfer.currency_id.id)
                transfer.bank_ids = [(6, 0, bank_ids.ids)]
    
    
    @api.multi
    @api.onchange('currency_id','partner_id', 'partner_bank')
    def get_default_account(self):
        for transfer in self:
            if transfer.currency_id and transfer.partner_id:
                bank_ids = transfer.partner_id.bank_ids.filtered(lambda b: b.currency_id.id == transfer.currency_id.id)
                if bank_ids:
                    transfer.partner_bank = bank_ids[0].bank_id.id

                if transfer.partner_bank:
                    vendor_acct_id = self.env['res.partner.bank'].search(
                        [('currency_id','=',transfer.currency_id.id),
                        ('partner_id','=',transfer.partner_id.id),
                        ('bank_id','=',transfer.partner_bank.id)],
                        limit=1).id
                    transfer.vendor_acct_id = vendor_acct_id
    
    @api.multi
    @api.onchange('currency_id')
    def get_default_debit_account(self):
        for transfer in self:
            if transfer.currency_id:
                debit_account_id = self.env['account.journal'].search(
                    [('currency_id','=',transfer.currency_id.id),
                     ('type','=','bank')],
                    limit=1).id
                transfer.debit_account_id = debit_account_id

    
    def _cron_check_status(self):
        transfer_list = self.search([('state','=','sent')])
        transfer_list.check_status()
        return True
    
    def _cron_mark_outgoing(self):
        transfer_list = self.search([('state','=','exception')])
        transfer_list.mark_outgoing()
        transfer_list.approve()
        self.env.cr.commit()
        for transfer in transfer_list:
            transfer.transfer_funds()
        return True
    
    def _cron_transfer_funds(self):
        transfer_list = self.search([('state','=','approve')])
        for transfer in transfer_list:
            transfer.transfer_funds()
        return True
    


    @api.multi
    def check_status(self):
        gateway = self.env['gateway.config'].sudo().search([], limit=1)
        accesscode = gateway.access_code
        username = gateway.username
        password = gateway.password
        url = gateway.url

        for transfer in self:
            tr = escape("<TransactionRequeryRequest><TransRef>%s</TransRef></TransactionRequeryRequest>"%(transfer.name))
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
            #print(body)
            
            headers = {'content-type': 'text/xml'}
                    
            response = requests.post(url,data=body,headers=headers)
            message = code = False
            #print(response.text)
            if response.status_code == 200:            
                soup = BeautifulSoup(response.text, "lxml")
                try:
                    transactionrequeryresult = soup.transactionrequeryresult.string
                    result = BeautifulSoup(transactionrequeryresult, "lxml")
                    code = result.code.string
                    message = result.message.string
                except Exception as e:
                    message = e
        
            self.env['ninas.bank.transfer.logs'].sudo().create({
                'status_code':response.status_code,
                'response':response.text,
                'message':message,
                'code': code,
                'bank_transfer_id':transfer.id
            })

            if code in ['1006', '1009']:
                self.write({'state':'sent'})
            elif code in ['1000']:
                self.write({'state':'received'})
            else:
                self.write({'state':'exception'})
        return
    
    @api.multi
    def transfer_funds(self):
        transactions = {}
        transactions = '<transactions>'
        transfer_list = self.filtered(lambda a: a.state == 'approve')
        date = time.strftime("%Y/%m/%d")
        #print(date)
        for transfer in transfer_list:
            transactions += '<transaction>'

            transactions += """
                            <amount>%s</amount>
                            <paymentdate>%s</paymentdate>
                            <reference>%s</reference>
                            <remarks>%s</remarks>
                            <vendorcode>%s</vendorcode>
                            <vendorname>%s</vendorname>
                            <vendoracctnumber>%s</vendoracctnumber>
                            <vendorbankcode>%s</vendorbankcode>
                            <customeracctnumber>%s</customeracctnumber>
                            """%(transfer.amount or 0,
                                 date or '',
                                 transfer.name or '',
                                 transfer.remarks or '',
                                 transfer.vendor_code or '',
                                 transfer.vendor_name or '',
                                 transfer.vendor_acctnumber or '',
                                 transfer.vendor_bankcode or '',
                                 transfer.debit_acctnumber or '',)
            transactions += '</transaction>'
        transactions += '</transactions>'
        filtered_transactions = filter(transactions)
        #print(filtered_transactions)

        transfer_request = self.get_transfer_request(filtered_transactions)
        #print(transfer_request)
        transfer_type = self.env.context.get('transfer_type', 'single')
        if transfer_type == 'bulk' and len(self) <= 1:
            transfer_type = 'single'
        transfer_list.transfers(transfer_request, transfer_type)
        transfer_list.write({'payment_date':time.strftime("%Y-%m-%d")})
        return


    def get_transfer_request(self, transactions):   
        gateway = self.env['gateway.config'].sudo().search([], limit=1)
        transdetails = '<transdetails>%s</transdetails>'%escape(transactions)
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
    
    
    
    def transfers(self, transfer_request, transfer_type):
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
        
        if transfer_type == 'single':
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
            #print(body)
        elif transfer_type == 'bulk':
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
            #print(body)
                    
        response = requests.post(url,data=body,headers=headers)
        message = code = False

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            try:
                if transfer_type == 'single':
                    singletransfersresult = soup.singletransfersresult.string
                    result = BeautifulSoup(singletransfersresult, "lxml")
                elif transfer_type == 'bulk':
                    bulktransfersresult = soup.bulktransfersresult.string
                    result = BeautifulSoup(bulktransfersresult, "lxml")
                code = result.code.string
                message = result.message.string
            except Exception as e:
                message = e
        
        for transfer in self:
            self.env['ninas.bank.transfer.logs'].sudo().create({
                'status_code':response.status_code,
                'response':response.text,
                'message':message,
                'code': code,
                'bank_transfer_id':transfer.id
            })
        if self.env.context.get('transfer_type', 'False') == 'bulk':
            bulk_transfer_id = self.env.context.get('active_id', False)
            if bulk_transfer_id:
                self.env['ninas.bank.transfer.logs'].sudo().create({
                    'status_code':response.status_code,
                    'response':response.text,
                    'message':message,
                    'code': code,
                    'bulk_transfer_id':bulk_transfer_id
                })

        if transfer_type == 'single':
            if code in ['1100','1009']:
                self.write({'state':'sent'})
            elif code in ['1000']:
                self.write({'state':'received'})
            else:
                self.write({'state':'exception'})
        elif transfer_type == 'bulk':
            if code in ['1009']:
                self.write({'state':'sent'})
            elif code in ['1000']:
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
    bulk_transfer_id = fields.Many2one(comodel_name='ninas.bulk.transfer', string='Bulk Transfer')


class AllAccountBalance(models.Model):
    _name = 'ninas.account.balance'
    _description = 'NiNAS Account Balances'
    _order = 'create_date DESC'

    name = fields.Char(string='Reference', required=True)
    account_number = fields.Char(string='Account Number')
    code = fields.Char(string='Response Code')
    message = fields.Char(string='Response Description')
    response = fields.Char(string='Full Response')
    count = fields.Char(string='No. of Accounts')
    balance_line_ids = fields.One2many(comodel_name='ninas.account.balance.line', inverse_name='balance_id', string='Balance Lines')

    @api.multi
    def get_balance(self):
        self.ensure_one()
        gateway = self.env['gateway.config'].sudo().search([], limit=1)
        accesscode = gateway.access_code
        username = gateway.username
        password = gateway.password
        url = gateway.url
        headers = {'content-type': 'text/xml'}
        hash = hashlib.sha512()
    
        if self.account_number:
            hash.update((accesscode+username+password+self.account_number).encode('utf-8'))
            hash = hash.hexdigest().upper()

            tr = """<customerid>%s</customerid>
                    <username>%s</username>
                    <password>%s</password>
                    <accountnumber>%s</accountnumber>
                    <hash>%s</hash>"""%(accesscode,username, password, self.account_number, hash)
            
            body = """<?xml version="1.0" encoding="utf-8"?>
                        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fil="http://tempuri.org/GAPS_Uploader/FileUploader">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <fil:AccountBalanceRetrieval>
                                <!--Optional:-->
                                <fil:xmlString>
                                <![CDATA[<AccountBalanceRetrievalRequest>%s</AccountBalanceRetrievalRequest>]]>
                                </fil:xmlString>
                            </fil:AccountBalanceRetrieval>
                        </soapenv:Body>
                        </soapenv:Envelope>"""%(tr)
            
        else:
            hash.update((accesscode+username+password).encode('utf-8'))
            hash = hash.hexdigest().upper()

            tr = """<customerid>%s</customerid>
                    <username>%s</username>
                    <password >%s</password>
                    <hash>%s</hash>"""%(accesscode, username, password, hash)
            
            body = """<?xml version="1.0" encoding="utf-8"?>
                        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fil="http://tempuri.org/GAPS_Uploader/FileUploader">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <fil:AllAccountBalancesRetrieval>
                                <!--Optional:-->
                                <fil:xmlString>
                                <![CDATA[<AllAccountBalancesRetrievalRequest>%s</AllAccountBalancesRetrievalRequest>]]>
                                </fil:xmlString>
                            </fil:AllAccountBalancesRetrieval>
                        </soapenv:Body>
                        </soapenv:Envelope>"""%(tr)
                    
        response = requests.post(url,data=body,headers=headers)
        #print(response)
        soup = BeautifulSoup(response.text, "lxml")
        #print(soup)
        message = code = count = False
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            try:
                if self.account_number:
                    try:
                        accountbalanceretrievalresult = soup.accountbalanceretrievalresult.string
                        #print('Message', accountbalanceretrievalresult)
                        result = BeautifulSoup(accountbalanceretrievalresult, "lxml")
                        message = result.message.string
                        #print('Message 2', message)
                        accountbalanceretrievalresponse = BeautifulSoup(message, "lxml")
                        #print('Message 3', accountbalanceretrievalresponse)
                        code = accountbalanceretrievalresponse.responsecode.string
                        message = accountbalanceretrievalresponse.responsedesc.string
                        balance_line_obj = self.env['ninas.account.balance.line']
                        accountnumber = accountbalanceretrievalresponse.accountnumber.string
                        ledger_bal = accountbalanceretrievalresponse.ledger_bal.string.replace(',','')
                        avail_bal = accountbalanceretrievalresponse.avail_bal.string.replace(',','')
                        curr = accountbalanceretrievalresponse.curr.string
                        currency_id = self.env['res.currency'].sudo().search([('name','=',curr)],limit=1).id

                        balance_line = balance_line_obj.search([('balance_id','=',self.id),('name','=',accountnumber)],limit=1)
                        if balance_line:
                            balance_line.write({
                                'legder_balance':ledger_bal,
                                'available_balance':avail_bal,
                                'currency_id':currency_id,
                            })
                        else:
                            balance_line_obj.create({
                                'balance_id':self.id,
                                'legder_balance':ledger_bal,
                                'available_balance':avail_bal,
                                'currency_id':currency_id,
                                'name':accountnumber
                            })
                    except:
                        accountbalanceretrievalresult = soup.accountbalanceretrievalresult.string
                        result = BeautifulSoup(accountbalanceretrievalresult, "lxml")
                        code = result.rescode.string
                        message = result.message.string
                else:
                    try:
                        #print('here1')
                        allaccountbalancesretrievalresult = soup.allaccountbalancesretrievalresult.string
                        #print('Message', allaccountbalancesretrievalresult)
                        result = BeautifulSoup(allaccountbalancesretrievalresult, "lxml")
                        message = result.message.string
                        #print('Message 2', message)
                        allcccountbalancesretrievalresponse = BeautifulSoup(message, "lxml")
                        #print('Message 3', allcccountbalancesretrievalresponse)
                        code = allcccountbalancesretrievalresponse.responsecode.string
                        message = allcccountbalancesretrievalresponse.responsedesc.string
                        count = allcccountbalancesretrievalresponse.count.string
                        accounts = allcccountbalancesretrievalresponse.find_all('account')
                        balance_line_obj = self.env['ninas.account.balance.line']
                        if accounts:
                            for account in accounts:
                                #print(account)
                                accountnumber = account.accountnumber.string
                                ledger_bal = account.ledger_bal.string.replace(',','')
                                avail_bal = account.avail_bal.string.replace(',','')
                                curr = account.curr.string
                                currency_id = self.env['res.currency'].sudo().search([('name','=',curr)],limit=1).id

                                balance_line = balance_line_obj.search([('balance_id','=',self.id),('name','=',accountnumber)],limit=1)
                                if balance_line:
                                    balance_line.write({
                                        'legder_balance':ledger_bal,
                                        'available_balance':avail_bal,
                                        'currency_id':currency_id,
                                    })
                                else:
                                    balance_line_obj.create({
                                        'balance_id':self.id,
                                        'legder_balance':ledger_bal,
                                        'available_balance':avail_bal,
                                        'currency_id':currency_id,
                                        'name':accountnumber
                                    })
                    except:
                        allaccountbalancesretrievalresult = soup.allaccountbalancesretrievalresult.string
                        result = BeautifulSoup(allaccountbalancesretrievalresult, "lxml")
                        code = result.rescode.string
                        message = result.message.string
            except Exception as e:
                message = e
        self.write({'code':code, 'message':message, 'count':count, 'response':response.text})
        #print(body)
        #print(response.text)


class AccountBalanceLine(models.Model):
    _name = 'ninas.account.balance.line'
    _description = 'NiNAS Account Balance Lines'
    _order = 'create_date DESC'
    _inherit = ['mail.thread']

    name = fields.Char(string='Account Number', track_visibility='onchange')
    legder_balance = fields.Monetary(string='Ledger Balance', currency_field='currency_id',track_visibility='onchange')
    available_balance = fields.Monetary(string='Available Balance', currency_field='currency_id',track_visibility='onchange')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency',track_visibility='onchange')
    balance_id = fields.Many2one(comodel_name='ninas.account.balance', string='Balance',track_visibility='onchange')