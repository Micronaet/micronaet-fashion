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
import base64
import xmlrpclib
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

class FashionForm(orm.Model):
    """ Model name: FashionForm
    """
    
    _inherit = 'fashion.form'

    # -------------------------------------------------------------------------
    # Utility XMLRPC call:
    # -------------------------------------------------------------------------
    def generate_report_xls_photo_pdf(
            self, cr, uid, item_code, context=None):
        ''' Generate PDF report for product passed and save in folder
        '''
        if context is None:
            context = {}
        
        current_user = self.pool.get('res.users').browse(
            cr, uid, uid, context=context)
        context['tz'] = current_user.tz
            
        # Pool used:
        form_pool = self.pool.get('fashion.form')
        action_pool = self.pool.get('ir.actions.report.xml')
        
        # ---------------------------------------------------------------------
        # Read model from CSV file and get model list:
        # ---------------------------------------------------------------------
        active_ids = []
        not_found = []
        for model in item_code:            
            form_ids = form_pool.search(cr, uid, [
                ('model', '=', model), # XXX last review!
                ], order='review desc', context=context)    
            if form_ids:
                active_ids.append(form_ids[0])
            else:
                _logger.error('Code not found: %s' % model)    
                not_found.append(model)
                
        # ---------------------------------------------------------------------
        # Generate PDF report:     
        # ---------------------------------------------------------------------
        if not active_ids:
            return False
            
        # Parameter:
        report_name = 'fashion_xls_photo_report'        
        report_service = 'report.%s' % report_name
        service = netsvc.LocalService(report_service)
        
        # Call report:            
        (result, extension) = service.create(
            cr, uid, active_ids, {'model': 'fashion.form'}, context=context)        
        return xmlrpclib.Binary(result), not_found
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
