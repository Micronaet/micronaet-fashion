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
import xlsxwriter # XLSX export


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
        form_pool = self.get('fashion.form')
        form_ids = form_pool.search(cr, uid, [
            ('season_id', '=', currenct_proxy.season_id.id)], context=context)
        
        for form in form_pool.browse(cr, uid, form_ids, context=context)[0]
            for cost in form.pricelist_ids:
                for pricelist in cost.pricelist_ids:
                    res.append((
                        pricelist.supplier_id.name
                        form.type_id.name, # or first (second) char
                        form.model,
                        cost.cost_id.name,
                        #cost.value,
                        pricelist.value,
                        pricelist.order,
                        pricelist.reference,                        
                        ))    
        res = sorted(res, key=lambda x: (0, 1, 2, 4))

        # ---------------------------------------------------------------------
        #                        XLS log export:        
        # ---------------------------------------------------------------------
        path = os.path.expanduser('~/output')
        os.system ('mkdir -p %s' % path)
        filename = os.path.join(path, 'export_season.xlsx')
        
        WB = xlsxwriter.Workbook(filename)
        
        # Create element for empty category:        
        old_supplier = False
        for supplier, category, cost, value, order, reference in res:
            if not old_supplier or supplier != old_supplier:
                ols_supplier = supplier
                
                # Create new XLS tab:
                WS = WB.add_worksheet(supplier)
                write_header(WS, header)
                counter = 1
                write_xls_line(WS, (
                    'Tipo', 'Costo', 'Importo', 'Ordine', 'Lanciato'), 0)
            
            write_xls_line(WS, (
                category, cost, value, order, reference), counter)
            counter += 1
            
        return True
        
    _columns = {
         'season_id': fields.many2one(
             'fashion.season', 'Season', required=True),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
