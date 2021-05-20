# -*- coding: utf-8 -*-
# Copyright 2019  Micronaet SRL (<http://micronaet.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import pdb
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
        if not wizard.xlsx_file:
            raise osv.except_osv(
                _('No file:'),
                _('Please pass a XLSX file for import order'),
                )
        b64_file = base64.decodestring(wizard.xlsx_file)
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
        ws_name = wb.sheet_names()[0]
        ws = wb.sheet_by_name(ws_name)
        _logger.warning('Read page: %s' % ws_name)

        imported_ids = []
        data = {}  # Setup for old
        for row in range(row_start, ws.nrows):
            total = ws.cell(row, 7).value
            if type(total) not in (int, float):
                _logger.info('%s. Not imported job' % (row + 1))
                continue

            sequence = row + 1
            name = ws.cell(row, 0).value or data.get('name')
            internal = ws.cell(row, 1).value or data.get('internal')
            style = ws.cell(row, 2).value or data.get('style')
            color = ws.cell(row, 3).value or data.get('color')
            size = ws.cell(row, 4).value
            barcode = ws.cell(row, 5).value

            # Correct:
            if type(style) == float:
                style = int(style)
            if type(size) == float:
                size = int(size)

            data = {
                'sequence': sequence,
                'import_date': now,
                'batch': ws_name,
                'name': name,
                'internal': internal,
                'style': style,
                'color': color,
                'size': size,
                'barcode': barcode,
                'total': total,
            }
            imported_ids.append(job_pool.create(cr, uid, data, context=context))
            _logger.info('%s. Imported job: %s' % (sequence, name))

        form_view_id = tree_view_id = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Job importati'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'label.job',
            'view_id': tree_view_id,
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('id', 'in', imported_ids)],
            'context': context,
            'target': 'current',
            'nodestroy': False,
            }

    _columns = {
        'xlsx_file': fields.binary('File XLSX', required=True),
        'note': fields.text('Note'),
        }

    _defaults = {
        }

