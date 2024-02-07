#|/usr/bin/python
# -*- coding: utf-8 -*-
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
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse

counters = {}  # total counters


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_objects': self.get_objects,
            'get_partner_fabric_proxy': self.get_partner_fabric_proxy,
            'get_wash_symbol': self.get_wash_symbol,
            'browse_in_cols': self.browse_in_cols,
            'set_counter': self.set_counter,
            'get_counter': self.get_counter,
            'how_much_zero': self.how_much_zero,
            'context': context,
            'is_last': self.is_last,
            'get_fabric': self.get_fabric,
        })

    def get_fabric(self, fabric):
        """ generate name
        """
        if not fabric:
            return ''
        return '%s [%s] (%s) %s' % (
                fabric.code,
                fabric.season_id.code if fabric.season_id else '',
                fabric.article_code or '',
                fabric.perc_composition or '',
                )

    def is_last(self, item_id):
        """ Check if ID passed is last
        """
        return item_id == self.last

    def how_much_zero(self, accessory):
        """ Test if there's accessory without price
        """
        zero = 0
        for item in accessory:
            if not item.currency:
                zero += 1
        return zero

    def get_counter(self, name):
        """ Return value of passed counter, if empty create with 0 value
        """
        global counters
        if name not in counters:
            counters[name] = 0.0
        return counters[name]

    def set_counter(self, name, value, with_return=False):
        """ Set up counter with name passed with the value
            if with return the method return setted value
        """
        global counters
        counters[name] = value
        if with_return:
            return counters[name]
        else:
            return '' # Write nothing (not False)

    def get_partner_fabric_proxy(self, data=None):
        if data is None or not data.get('partner_fabric_id', False):
            return False

        return self.pool.get('fashion.form.partner.rel').browse(
            self.cr, self.uid, data.get('partner_fabric_id', False))

    def get_wash_symbol(self, data=None):
        """ Return wash symbol for passed partner-fabric element)
        """
        # todo verificare se è il caso di testare il cliente oppure è già
        #  indicata nell'accessorio
        return ""

    def get_objects(self, data=None, context=None):
        if data is None:
            data = {}
        if context is None:
            context = {}

        form_ids = data.get('active_ids', [])
        if not form_ids:
            form_ids = context.get('active_ids', [])

        self.last = form_ids[-1]  # for new page
        return self.pool.get('fashion.form').browse(
            self.cr, self.uid, form_ids)

    def browse_in_cols(self, obj_proxy, cols=2):
        """ Browse in N cols passed browse obj
        """
        res = []
        row = 0
        col = 0
        for record in obj_proxy:
            if not record.code:
                if col == 0:
                    res.append([False for i in range(0, cols)])  # Create an empty record
                res[row][col] = record
                if col == cols - 1:  # last column
                    row += 1
                    col = 0
                else:
                    col += 1
        return res

