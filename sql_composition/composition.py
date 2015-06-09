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
import netsvc
import logging
from openerp.osv import osv, orm, fields
from datetime import datetime, timedelta
from openerp.tools import (
    DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)

class FashionFormFabricComposition(orm.Model):
    ''' Extend composition obj
    '''    
    _inherit = 'fashion.form.fabric.composition'
    
    _columns = {
        'sql_import': fields.boolean('SQL import', required=False),
        }
    
    _defaults = {
        'sql_import': lambda *a: False,
        }

    # -------------------------------------------------------------------------
    #                                  Scheduled action
    # -------------------------------------------------------------------------
    def schedule_sql_composition_import(self, cr, uid, verbose_log_count=100, 
            context=None):
        ''' Import product from external DB
        '''
        accounting_pool = self.pool.get('micronaet.accounting')
        try:
            cursor = accounting_pool.get_composition( 
                cr, uid, context=context) 
            if not cursor:
                _logger.error(
                    "Unable to connect no importation of composition!")
                return False

            i = 0
            
            for record in cursor:
                try:
                    i += 1
                    if verbose_log_count and i % verbose_log_count == 0:
                        _logger.info('Import %s: record import/update!' % i)                             

                    data = {
                        'code': record['CDS_ART'],
                        'perc_composition': record['CKY_ART'],
                        'symbol': record['CKY_ART'],
                        'season_id': False,
                        'sql_import': True,
                    }
                        
                    product_ids = product_proxy.search(cr, uid, [
                        ('default_code', '=', record['CKY_ART'])])
                    if product_ids:
                        product_id = product_ids[0]
                        product_proxy.write(cr, uid, product_id, data, 
                            context=context)
                    else:
                        product_id = product_proxy.create(cr, uid, data, 
                            context=context)

                except:
                    _logger.error('Error import composition [%s], jump: %s' % (
                        record['CDS_ART'], sys.exc_info(), ))
                        
            _logger.info('All composition is updated!')
        except:
            _logger.error('Error generic import product: %s' % (
                sys.exc_info(), ))
            return False
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
