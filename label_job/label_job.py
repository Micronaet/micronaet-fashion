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

    _columns = {
        'name': fields.char(
            'Name', size=64, required=True,
            ),
        'import_date': fields.date('Import', required=True),

    }

    _defaults = {
        #   'name': lambda *a: None,
        }
