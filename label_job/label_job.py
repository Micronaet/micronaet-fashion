# -*- coding: utf-8 -*-
# Copyright 2019  Micronaet SRL (<http://micronaet.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
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

_logger = logging.getLogger(__name__)


class LabelJob(orm.Model):
    """ Model name: LabelJob
    """

    _name = 'label.job'
    _description = 'Label job'
    _rec_name = 'name'
    _order = 'import_date desc'

    def wkf_print(self, cr, uid, ids, context=None):
        """ Print label
        """
        datas = {}
        report_name = 'label_job_report'

        self.write(cr, uid, ids, {
            'state': 'printed',
        }, context=context)

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

    _columns = {
        'batch': fields.char('Lotto', size=80),
        'name': fields.char('Modello cliente', size=80, required=True),
        'internal': fields.char('Modello interno', size=80),
        'style': fields.char('Style number', size=40),
        'color': fields.char('Colore', size=40),
        'size': fields.char('Taglia', size=20),
        'barcode': fields.char('Codice EAN13', size=20),
        'total': fields.integer('Totale'),

        'import_date': fields.datetime('Importazione'),
        'state': fields.selection([
            ('new', 'Nuova'),
            ('printed', 'Stampata'),
            ('closed', 'Chiusa'),
        ], 'Stato'),
    }

    _defaults = {
        'import_date': lambda *a: datetime.now().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT),
        'state': lambda *x: 'new',
        }
