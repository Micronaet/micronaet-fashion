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
import xlsxwriter # XLSX export
from openerp.osv import osv, fields
from datetime import datetime

_logger = logging.getLogger(__name__)


class fashion_extract_cost_xls(osv.osv_memory):
    ''' Extract cost XLS
    '''
    _name = 'fashion.extract.cost.xls'
    _description = 'Extract Cost XLS'

    def extract_cost_xls(self, cr, uid, ids, context=None):
        ''' Extract XLS file
        '''
        # Utility:
        def write_xls_line(WS, line, counter):
            ''' Write XLS line
            '''
            col = 0
            for field in line:   
                WS.write(counter, col, field)
                col += 1                
            return 
            
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        
        res = []
        form_pool = self.pool.get('fashion.form')
        form_ids = form_pool.search(cr, uid, [
            ('season_id', '=', current_proxy.season_id.id)], context=context)
        
        for form in form_pool.browse(cr, uid, form_ids, context=context):
            for cost in form.cost_rel_ids:
                for pricelist in cost.pricelist_ids:
                    if not pricelist.supplier_id:
                        _logger.error('No supplier name!')
                        continue
                        
                    supplier = pricelist.supplier_id.name.upper()
                    res.append((
                        supplier,
                        form.article_id.name, # or first (second) char
                        form.model,
                        cost.cost_id.name.upper(),
                        #cost.value,
                        pricelist.value,
                        pricelist.order or '',
                        pricelist.reference or '',                        
                        ))    
        res = sorted(res, key=lambda x: (x[0], x[1], x[2], x[3]))

        # ---------------------------------------------------------------------
        #                        XLS log export:        
        # ---------------------------------------------------------------------
        path = os.path.expanduser('~/output')
        os.system ('mkdir -p %s' % path)
        filename = os.path.join(path, 'export_season.xlsx')
        
        WB = xlsxwriter.Workbook(filename)
        
        # Create element for empty article:        
        old_supplier = '?' # for empty value management
        old_article = '?' # for empty value management
        
        for supplier, article, form, cost, value, order, reference in res:
            if old_supplier == '?' or supplier != old_supplier:
                old_supplier = supplier
                
                # Create new XLS tab:
                WS = WB.add_worksheet(supplier)
                counter = 0
                old_article = '?'
                
            if old_article == '?' or old_article != article:
                old_article = article
                 
                if counter: # not 0
                    counter +=1 # keep distance from previous block
                
                # Write block name:
                WS.write(counter, 0, article) 
                counter += 1
                
                # Write header for data:
                write_xls_line(WS, (
                    'Scheda', 'Costo', 'Importo', 'Ordine', 'Lanciato'), 
                    counter)
                counter += 1
            
            write_xls_line(WS, (
                form, cost, value, order, reference), counter)
            counter += 1            
        return True
        
    _columns = {
         'season_id': fields.many2one(
             'fashion.season', 'Season', required=True),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
