# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import os
import sys
import logging
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)


class ResPartnerUniqueNameWizard(orm.TransientModel):
    ''' Wizard for unify partner with name
    '''
    _name = 'res.partner.unique.name.wizard'

    # --------------------
    # Wizard button event:
    # --------------------
    def unify_all(self, cr, uid, ids, context=None):
        ''' Search partner not used
            Try to unify other
        '''
        _logger.info('Start unify partner:')
        partner_pool = self.pool.get('res.partner')
        partner_ids = partner_pool.search(cr, uid, [], order='id', 
            context=context)
        
        partner_double = {}
        unify_name = []
        exclude = [u'User', u'Accounting', u'Production']
        _logger.info('Create database of double:')
        for partner in partner_pool.browse(
                cr, uid, partner_ids, context=context):
            if partner.name in exclude:
                continue    
            if partner.name in partner_double:
                # DB (name) = (keep id, remove ids)
                partner_double[partner.name][1].append(partner.id)
                if partner.name not in unify_name:
                    unify_name.append(partner.name)
            else:    
                partner_double[partner.name] = [partner.id, []]

        _logger.info('Correct query data:')
        query_db = (
            ('account_analytic_account', 'partner_id'),
            ('account_bank_statement_line', 'partner_id'),
            ('account_invoice', 'commercial_partner_id'),
            ('account_invoice_line', 'partner_id'),
            ('account_invoice', 'partner_id'),
            ('account_model_line', 'partner_id'),
            ('account_move_line', 'partner_id'),
            ('account_move', 'partner_id'),
            ('account_partner_reconcile_process', 'next_partner_id'),
            ('account_voucher', 'partner_id'),
            ('fashion_form_accessory_pricelist', 'supplier_id'),
            ('fashion_form_accessory_rel', 'supplier_id'),
            ('fashion_form_cost_rel_pricelist', 'suplier_id'),
            ('fashion_form_cost_rel_pricelist', 'supplier_id'),
            ('fashion_form_fabric', 'supplier_id'),
            ('fashion_form', 'group_id'),
            ('fashion_form_partner_rel', 'group_id'),
            ('fashion_form_partner_rel', 'partner_id'),
            ('fashion_form_partner_rel', 'supplier_id'),
            ('mail_compose_message', 'author_id'),
            ('mail_compose_message_res_partner_rel', 'partner_id'),
            ('mail_followers', 'partner_id'),
            ('mail_message', 'author_id'),
            ('mail_message_res_partner_rel', 'res_partner_id'),
            ('mail_notification', 'partner_id'),
            ('mail_wizard_invite_res_partner_rel', 'res_partner_id'),
            ('portal_wizard_user', 'partner_id'),
            ('product_supplierinfo', 'name'),
            ('res_company', 'partner_id'),
            ('res_partner_bank', 'partner_id'),
            ('res_partner', 'group_id'),
            ('res_partner', 'parent_id'),
            ('res_partner_res_partner_category_rel', 'partner_id'),
            ('res_partner_unique_name_wizard', 'partner_id'),
            ('res_request', 'ref_partner_id'),
            ('res_users', 'partner_id'),
            ('sale_order_line', 'address_allotment_id'),
            ('sale_order_line', 'order_partner_id'),
            ('sale_order', 'partner_id'),
            ('sale_order', 'partner_invoice_id'),
            ('sale_order', 'partner_shipping_id'),
            )
        deactivate_ids = []        
        for name in unify_name:
            keep_id, remove_ids = partner_double[name]
            
            for table, field in query_db:
                query = 'UPDATE %s SET %s = %s WHERE %s in %s;' % (
                    table, field, keep_id, field, tuple(remove_ids), 
                    )
                query = query.replace(',)', ')')    
                try:    
                    _logger.info(query)
                    cr.execute(query)                
                except:
                    _logger.error('%s %s' % (table, field))
                    import pdb; pdb.set_trace()
            deactivate_ids.extend(remove_ids)
        
        partner_pool.write(cr, uid, deactivate_ids, {
            'active': False,
            }, context=context)    
        return True
        
    def action_done(self, cr, uid, ids, context=None):
        ''' Event for button done
        '''
        if context is None: 
            context = {}        
        
        wiz_browse = self.browse(cr, uid, ids, context=context)[0]
        
        return {
            'type': 'ir.actions.act_window_close'
            }

    _columns = {
        'partner_id': fields.many2one(
            'res.partner', 'Keep this', help='Keep this partner'),
        'partner_note': fields.text('Note', readonly=True),    
        }
        
    _defaults = {
        #'partner_id': lambda s, cr, uid, c: s.default_product_id(cr, uid, context=c),
        
        }    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


