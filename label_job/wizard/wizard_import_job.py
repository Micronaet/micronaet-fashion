# -*- coding: utf-8 -*-
# Copyright 2019  Micronaet SRL (<http://micronaet.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import logging
import base64
import openerp
import xlrd
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
    DATETIME_FORMATS_MAP,
    float_compare)

_logger = logging.getLogger(__name__)


class ReportJobImportWizard(orm.TransientModel):
    """ Import label job from excel
    """
    _name = 'report.job.import.wizard'
    _description = 'Import label job wizard'

    # --------------
    # Button events:
    # --------------
    def action_import_file(self, cr, uid, ids, context=None):
        """ Event for button done force update lead lot
        """
        if context is None:
            context = {}

        # Pool used:
        job_pool = self.pool.get('label.job')

        # ---------------------------------------------------------------------
        # Save file passed:
        # ---------------------------------------------------------------------
        wizard = self.browse(cr, uid, ids, context=context)[0]
        if not wizard.file:
            raise osv.except_osv(
                _('No file:'),
                _('Please pass a XLSX file for import order'),
                )
        b64_file = base64.decodestring(wizard.file)
        now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        filename = '/tmp/tx_%s.xlsx' % now.replace(':', '_').replace('-', '_')
        f = open(filename, 'wb')
        f.write(b64_file)
        f.close()

        try:
            wb = xlrd.open_workbook(filename)
        except:
            raise osv.except_osv(
                _('Error XLSX'),
                _('Cannot read XLS file: %s' % filename),
                )

        # ---------------------------------------------------------------------
        # Loop on all pages:
        # ---------------------------------------------------------------------
        row_start = 0
        for ws_name in WB.sheet_names():
            ws = wb.sheet_by_name(ws_name)
            _logger.warning('Read page: %s' % ws_name)

            for row in range(row_start, ws.nrows):
                default_code = ws.cell(row, 0).value
                _logger.info('Find material: %s' % default_code)

                data = {
                    'name': '',
                }
                job_pool.create(cr, uid, data, context=context)

    _columns = {
        'xlsx_file': fields.binary('File XLSX', required=True),
        'note': fields.text('Note'),
        }

    _defaults = {
        }

