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

    def get_line_label(self, objects, data):
        """ Selected object + print object
        """
        label_pool = self.pool.get('label.job')

        cr = self.cr
        uid = self.uid
        context = {'lang': 'IT_it'}

        # Layour sheet:
        cols = 3
        rows = 8

        label1 = {}
        label2 = {}
        label3 = {}
        pdb.set_trace()

        lines = []
        for label in objects:
            label_id = label.id
            total = label.total

            row = 0
            current_col = current_label = 0
            for col in range(0, total, cols):
                # Choose label mode:
                current_col += 1
                if col in (1, 8):
                    mode = 2
                    if col == 8:
                        current_col = 0  # Reset countet
                else:
                    mode = 1

                # Prepare label line:
                line = [mode, []]
                for row in range(cols):
                    current_label += 1
                    if current_label <= total:
                        line[mode].append(label)
                    else:
                        line[mode].append(False)  # No more label
                lines.append(line)
            # Complete all the sheet? (for multilabel)

            # Update label as printed:
            label_pool.write(cr, uid, [label_id], {
                'state': 'printed',
            }, context=context)

        return lines

