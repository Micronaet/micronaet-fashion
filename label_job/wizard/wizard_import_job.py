# -*- coding: utf-8 -*-
###############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
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

class ReportJobImportWizard(orm.TransientModel):
    ''' Import label job from excel
    '''    
    _name = 'report.job.import.wizard'
    _description = 'Sale multiorder wizard'
    
    # --------------
    # Button events:
    # --------------
    def print_report(self, cr, uid, ids, context=None):
        ''' Redirect to report passing parameters
        ''' 
        wiz_proxy = self.browse(cr, uid, ids)[0]
            
        datas = {}
        datas['wizard'] = True # started from wizard
        
        report_name = 'label_job_report' 
               

        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            }

    _columns = {
        'xlsx_file': fields.binary('File XLSX', required=True),
        'note': fields.text('Note'),        
        }
        
    _defaults = {
        }

