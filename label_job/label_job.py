# -*- coding: utf-8 -*-
# Copyright 2019  Micronaet SRL (<http://micronaet.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import os
import pdb
import sys
import logging
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
    DATETIME_FORMATS_MAP,
    float_compare)
# import barcode

_logger = logging.getLogger(__name__)


class LabelJob(orm.Model):
    """ Model name: LabelJob
    """

    _name = 'label.job'
    _description = 'Label job'
    _rec_name = 'name'
    _order = 'import_date desc, sequence'

    def wkf_print(self, cr, uid, ids, context=None):
        """ Print label
        """
        datas = {}
        report_name = 'label_job_report'

        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
            }

    def wkf_close(self, cr, uid, ids, context=None):
        """ Print label
        """
        return self.write(cr, uid, ids, {
            'state': 'closed',
        }, context=context)

    def wkf_restart(self, cr, uid, ids, context=None):
        """ Print label
        """
        return self.write(cr, uid, ids, {
            'state': 'new',
        }, context=context)

    """def _get_image_ean13_field(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for job in self.browse(cr, uid, ids, context=context):
            ean = job.barcode
            fullname = os.path.join('/tmp', ean)  # Auto svg ext.
            fullname_ext = os.path.join('/tmp', '%s.svg' % ean)
            if not os.path.isfile(fullname_ext):
                code = barcode.get_barcode(
                    'ean13', ean,
                    # {'includetext': True, 'height': 0.4, 'margin': 1},
                )
                pdb.set_trace()
                code.save(fullname)  #, {'type': 'PNG'})

            try:
                fullname = os.path.join(fullname_ext)
                f = open(fullname, 'rb')
                img = base64.encodebytes(f.read())
                f.close()
            except:
                img = ''

            res[job.id] = img
        return res"""

    _columns = {
        'batch': fields.char('Lotto', size=80),
        'sequence': fields.integer('Riga'),
        'name': fields.char('Modello cliente', size=80, required=True),
        'internal': fields.char('Modello interno', size=80),
        'style': fields.char('Style number', size=40),
        'color': fields.char('Colore', size=40),
        'size': fields.char('Taglia', size=20),
        'barcode': fields.char('Codice EAN13', size=20),
        'total': fields.integer('Totale'),
        #'ean13_image': fields.function(
        #    _get_image_ean13_field, type='binary', method=True),

        'import_date': fields.datetime('Importazione'),
        'state': fields.selection([
            ('new', 'Nuova'),
            ('printed', 'Stampata'),
            ('closed', 'Chiusa'),
        ], 'Stato'),
    }

    _defaults = {
        'state': lambda *x: 'new',
        }
