

from odoo import http
from odoo.http import request

class Accreditation(http.Controller):
    @http.route('''/helpdesk/<model("helpdesk.team", "[('use_website_helpdesk_form','=',True)]"):team>/submit''', type='http', auth="user", website=True)
    
    def index(self, **kw):
        default_values = {}
        assessment_type_id = http.request.env['assessment.type'].sudo().search([])
        lab_state_id = http.request.env['res.country.state'].sudo().search([])
        lab_country_id = http.request.env['res.country'].sudo().search([('name','=','Nigeria')])
        mail_state_id = http.request.env['res.country.state'].sudo().search([])
        mail_country_id = http.request.env['res.country'].sudo().search([('name','=','Nigeria')])
        account = http.request.env['helpdesk.ticket'].sudo().search([])
        test = http.request.env['helpdesk.ticket'].sudo().search([])
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
        return http.request.render("ninasmain.ninas_website_helpdesk_form_ticket_submit", {
            'default_values': default_values, 'assessment_type_id':assessment_type_id, 'account':account, 'test':test
            , 'lab_state_id':lab_state_id, 'lab_country_id':lab_country_id, 'mail_state_id':mail_state_id, 'mail_country_id':mail_country_id})
        


"""

from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm

class WebsiteForm(http.Controller):

    @http.route('''/helpdesk/<model("helpdesk.team", "[('use_website_helpdesk_form','=',True)]"):team>/submit''', type='http', auth="public", website=True)
    def website_helpdesk_form(self, team, **kwargs):
        default_values = {}
        assessment_type_id = request.env['assessment.type'].sudo().search([])

        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
            
        #return request.render("website_helpdesk_form.ticket_submit", {'team': team, 'default_values': default_values, 'assessment_type_id':assessment_type_id})

    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        if request.params.get('partner_email'):
            Partner = request.env['res.partner'].sudo().search([('email', '=', kwargs.get('partner_email'))], limit=1)
            if Partner:
                request.params['partner_id'] = Partner.id
        return super(WebsiteForm, self).website_form(model_name, **kwargs)


"""