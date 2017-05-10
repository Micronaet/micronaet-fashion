# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2011 company (http://www.micronaet.it) All Rights Reserved.
#                    General contacts <riolini@micronaet.it>
#                    General contacts <anna@micronaet.it>
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
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
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

{
    'name': 'Fashion',
    'version': '0.1',
    'category': 'Fashion',
    'description': """ Module for manager fashion
                   """,
    'author': 'Micronaet s.r.l.',
    'website': 'http://www.micronaet.it',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'product',
        'knowledge',
        'report_aeroo',
        'report_aeroo_ooo',
        'l10n_it',
        'fashion-kanban',
        'fashion_sheet_wide',
        'web_washing_symbol',
        #'web_m2x_options', # lock create in m2o XXX sometimes gives problem!
        ],
    'init_xml': [],
    'demo_xml': [],
    'data': [
            # Security:
            'security/fashion_group.xml',
            'security/ir.model.access.csv',

            # Report:
            'report/form_report.xml',

            # Wizard:
            'wizard/duplication_fashion_view.xml',
            'wizard/report_wizard.xml',
            'wizard/force_fabric_view.xml',
            'wizard/partner_unique_view.xml',

            # View:
            'fashion_view.xml',
            
            'wizard/extract_xls_view.xml',
             
            # Workflow:
            'fashion_form_workflow.xml',

            #'scheduler.xml', 
            #'data/list.xml',
            ],
    'active': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
