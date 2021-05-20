#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019  Micronaet SRL (<http://micronaet.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import pdb
import sys
import logging
from openerp.osv import fields, osv, expression, orm
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
    DATETIME_FORMATS_MAP,
    float_compare)

_logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):
    counters = {}
    last_record = 0

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_line_label': self.get_line_label,
        })

    def get_line_label(self, data):
        """ Selected object + print object
        """

        cr = self.cr
        uid = self.uid
        context = {'lang': 'IT_it'}
        label1 = {}
        label2 = {}
        label3 = {}

        pdb.set_trace()
        return [
            (2, (label1, label2, label3)),
            (1, (label1, label2, label3)),
            (1, (label1, label2, label3)),
            (1, (label1, label2, label3)),
            (1, (label1, label2, label3)),
            (1, (label1, label2, label3)),
            (1, (label1, label2, label3)),
            (2, (label1, label2, label3)),
        ]

