# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class FashionForm(orm.Model):
    """ Model name: FashionForm
    """
    
    _inherit = 'fashion.form'

    # -------------------------------------------------------------------------
    # Utility XMLRPC call:
    # -------------------------------------------------------------------------
    def generate_report_xls_photo_pdf(
            self, cr, uid, ids, file_csv, file_pdf, context=None):
        ''' Generate PDF report for product passed and save in folder
            file_csv: name for csv input file
            file_pdf: name for pdf output file
        '''
        # Pool used:
        form_pool = self.pool.get('fashion.form')
        action_pool = self.pool.get('ir.actions.report.xml')
        
        # ---------------------------------------------------------------------
        # Read model from CSV file and get model list:
        # ---------------------------------------------------------------------
        f_csv = open(file_csv, 'r')
        i = 0
        code_ids = []
        for row in f_csv:
            i += 1
            if i <= 4: # Start article line
                continue
            row = row.split(';')
            model = row[1]
            if not model:
                break
            model = model[:7].replace('-', '')
            
            form_ids = form_pool.search(cr, uid, [
                ('code', '=', model),
                # TODO get correct version
                ], context=context)    
                
        # ---------------------------------------------------------------------
        # Generate PDF report:     
        # ---------------------------------------------------------------------
        # Parameter:
        report_name = 'fashion_xls_photo_report'        
        report_service = 'report.%s' % report_name
        service = netsvc.LocalService(report_service)
        
        # Call report:            
        (result, extension) = service.create(
            cr, uid, [1], {'model': 'fashion.form'}, context=context)
        # TODO pass data list parameters                
        file_pdf = open(file_pdf, 'w')
        file_pdf.write(result)
        file_pdf.close()
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
