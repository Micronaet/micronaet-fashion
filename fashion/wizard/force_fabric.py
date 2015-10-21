#|/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class fashion_force_fabric(osv.osv_memory):
    '''Force reload of information in all forms that use this particular 
       fabric
    '''
    _name = 'fashion.force.fabric'
    _description = 'Force fabric'
    
    # -----------------
    # default function:
    # -----------------
    def get_washing_test(self, cr, uid, context=None):
        ''' Test if there's some symbol replaced
        '''
        if context is None:
            context = {}

        res = ''
        fabric_pool = self.pool.get('fashion.form.fabric')
        rel_pool = self.pool.get('fashion.form.partner.rel')
        
        # Read current fabric:
        active_id = context.get('active_id', 0)
        fabric_proxy = fabric_pool.browse(cr, uid, active_id, 
            context=context)
        
        # Search washing symbol changed:
        rel_ids = rel_pool.search(cr, uid, [
            ('fabric_id', '=', active_id),
            ('symbol_fabric', '!=', fabric_proxy.symbol),
            ], context=context)
        for item in rel_pool.browse(cr, uid, rel_ids, context=context):
            res += _('<br />Form: %s different symbol: %s') % (
                item.form_id.name,
                item.symbol_fabric,
                )
        if res:
            res = _('''<p>
                Found replaced symbols:<br />
                - Choose "Replace" for force update all elements<br />
                - Choose "Only empty" for change only element not setted<br />
                List:<br />
                %s</p>''') % res,
        
        return res
        
    _columns = {
        'replace_washing': fields.selection([
            ('replace', 'Replace'),
            ('only', 'Only empty'),
            ], 'Replace wash symbol', required=True),
        'name': fields.text('Info'),
        'washing': fields.text('Washing symbol check'),
        }
        
    _defaults = {
        'replace_washing': lambda *x: 'replace', # defautl also if invisible
        'name': lambda *x: _('''
            <p><b>Wizard force fabric</b><br/>
               This wizard force fabric property on all forms that use 
               this particular article. The event will be logged in form.
               In all form will be replaced:<br/>
               Code (also supplier code), Cost (and total), Composition
               Wash symbol (depend on wizard), Height, Weight and Supplier
            </p>
            '''),
        'washing': lambda s, cr, uid, ctx: s.get_washing_test(cr, uid, ctx),
        }    

    def force_fabric(self, cr, uid, ids, context=None):
        ''' Button event for force reload of characteristics
        '''
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        
        active_id = context.get('active_id', False)
        if not active_id:
            return False # TODO raise error

        fabric_proxy = self.pool.get('fashion.form.fabric').browse(
            cr, uid, active_id, context=context)
        
        rel_pool = self.pool.get('fashion.form.partner.rel')
        rel_ids = rel_pool.search(cr, uid, [
            ('fabric_id', '=', active_id)], context=context)

        data = {
            'h_fabric': fabric_proxy.h_fabric,
            'supplier_id': fabric_proxy.supplier_id.id, 
            'article_code': fabric_proxy.article_code,            
            'perc_fabric': fabric_proxy.perc_composition,
            'cost': fabric_proxy.cost,
            # TODO 
            #'article_description': fabric_proxy.article_description,
            #'note_fabric': fabric_proxy.note_fabric,                        
            }
        if wiz_proxy.replace_washing == 'only':
            # Search this fabric and no washing symbol
            empty_ids = rel_pool.search(cr, uid, [
                ('fabric_id', '=', active_id), 
                ('symbol_fabric', '=', False), 
                ], context=context)
            # Update only this records:    
            rel_pool.write(cr, uid, empty_ids, {
                'symbol_fabric': fabric_proxy.symbol,
                }, context=context)
            _logger.warning('Update empty items: %s with symbol %s' % (
                empty_ids, fabric_proxy.symbol))
        else: # replace all            
            data['symbol_fabric'] = fabric_proxy.symbol

        # Replace all elements (symbol are parametic)
        rel_pool.write(cr, uid, rel_ids, data, context=context)
        _logger.info('Update all record: %s with: %s' % (
            rel_ids, data))
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
