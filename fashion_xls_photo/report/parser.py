##############################################################################
#
# Copyright (c) 2008-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import os
import sys
import logging
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse

_logger = logging.getLogger(__name__)


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_row_objects': self.get_row_objects,
        })
        
    def get_row_objects(self, objects):
        ''' Put in row of 3 elements the data
        '''
        # Readability:
        cr = self.cr
        uid = self.uid
        context = {}

        res = []
        row = [False, False, False]

        i = 0  # Line goes from 0 to 2
        _logger.info('Print %s images' % len(objects))

        for o in objects:
            if i == 3:
                res.append(row)
                row = [False, False, False]
                i = 0
            row[i] = o
            i += 1
                
        if i != 0: # write last
            res.append(row) # TODO test
        return res

