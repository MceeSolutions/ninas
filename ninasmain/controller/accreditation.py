

from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm

class Accreditation(http.Controller):
    @http.route('''/accreditation/<model("helpdesk.team", "[('use_website_helpdesk_form','=',True)]"):team>/submit''', type='http', auth="user", website=True)
    def index(self, **kw):
        default_values = {}
        assessment_type_id = http.request.env['assessment.type'].sudo().search([])
        lab_state_id = http.request.env['res.country.state'].sudo().search([])
        lab_country_id = http.request.env['res.country'].sudo().search([('name','=','Nigeria')])
        mail_state_id = http.request.env['res.country.state'].sudo().search([])
        mail_country_id = http.request.env['res.country'].sudo().search([])
        account = http.request.env['helpdesk.ticket'].sudo().search([])
        test = http.request.env['helpdesk.ticket'].sudo().search([])
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
        return http.request.render("ninasmain.ninas_website_helpdesk_form_ticket_submit", {
            'default_values': default_values, 'assessment_type_id':assessment_type_id, 'account':account, 'test':test
            , 'lab_state_id':lab_state_id, 'lab_country_id':lab_country_id, 'mail_state_id':mail_state_id, 'mail_country_id':mail_country_id})
        

class WebsiteHelpdesk(http.Controller):

    def get_helpdesk_team_data(self, team, search=None):
        return {'team': team}

    @http.route(['/accreditation/', '/accreditation/<model("helpdesk.team"):team>'], type='http', auth="public", website=True)
    def website_helpdesk_teams(self, team=None, **kwargs):
        search = kwargs.get('search')
        # For breadcrumb index: get all team
        teams = request.env['helpdesk.team'].search(['|', '|', ('use_website_helpdesk_form', '=', True), ('use_website_helpdesk_forum', '=', True), ('use_website_helpdesk_slides', '=', True)], order="id asc")
        if not request.env.user.has_group('helpdesk.group_helpdesk_manager'):
            teams = teams.filtered(lambda team: team.website_published)
        if not teams:
            return request.render("website_helpdesk.not_published_any_team")
        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        result['teams'] = teams
        return request.render("website_helpdesk.team", result)

'''  
class WebForms(http.Controller):
    @http.route('/ninas/codeofconduct', auth="public", website=True)
    def index(self, **kw):
        name = http.request.env['hr.employee'].sudo().search([])
        Sections = http.request.env['ninas.code.conduct']
        return http.request.render("ninasmain.index", {
            'sections':Sections.search([])})
    
    @http.route('/test/path', type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def test_path(self, **kw):
        #here in kw you can get the inputted value
        print (kw['name'])
        
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        return super(WebForms, self).website_form(model_name, **kwargs)
      
class WebForms(http.Controller):

    @http.route('/ninas/codeofconduct', type='http', auth="public", website=True)
    def index(self, **kw):
        name = http.request.env['hr.employee'].sudo().search([])
        return http.request.render("ninasmain.index",{ 'name':name})

class WebsiteForm(WebsiteForm):

    # Check and insert values from the form on the model <model>
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def index(self, model_name, **kwargs):
        return super(WebsiteForm, self).website_form(model_name, **kwargs)
'''
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