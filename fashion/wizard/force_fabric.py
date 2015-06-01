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
from openerp.osv import osv, fields
from datetime import datetime


class fashion_force_fabric(osv.osv_memory):
    '''Force reload of information in all forms that use this particular 
       fabric
    '''
    _name = 'fashion.force.fabric'
    _description = 'Force fabric'
    
    _columns = {
        'name': fields.text('Info')
        }
    _defaults = {
        'name': lambda *x: """
            <p><b>Wizard force fabric</b><br/>
               This wizard force fabric property on all forms that use 
               this particular article. 
               In all form will be replaced:
               <ul>
                   <li>Code</li>
                   <li>Composition</li>
                   <li>Wash symbol</li>
                   <li>Height</li>
                   <li>Weight</li>
                   <li>Supplier</li>
               </ul>     
            </p>
            """,# cost product
        }    

    def force_fabric(self, cr, uid, ids, context=None):
        ''' Button event for force reload of characteristics
        '''
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        rel_pool = self.pool.get('fashion.form.partner.rel')
        rel_ids = res_pool.search(cr, uid, [
            ('fabric_id', '=', wiz_proxy.id)], context=context)

        data = {
            'h_fabric': wiz_proxy.h_fabric,
            'supplier_id': wiz_proxy.supplier_id.id, 
            'article_code': wiz_proxy.article_code,
            'article_description': wiz_proxy.arcicle_description,
            'perc_fabric': wiz_proxy.perc_fabric,
            'symbol_fabric': wiz_proxy.symbol,
            'note_fabric': wiz_proxy.note_fabric,            
            }
        res_pool.write(cr, uid, rel_ids, data, context=context)    

        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
