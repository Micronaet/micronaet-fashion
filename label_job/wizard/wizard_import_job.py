# -*- coding: utf-8 -*-
# Copyright 2019  Micronaet SRL (<http://micronaet.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import logging
import openerp
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
    _description = 'Sale multiorder wizard'

    # --------------
    # Button events:
    # --------------
    def print_report(self, cr, uid, ids, context=None):
        """ Redirect to report passing parameters
        """
        wiz_proxy = self.browse(cr, uid, ids)[0]

        datas = {}
        datas['wizard'] = True  # started from wizard

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

