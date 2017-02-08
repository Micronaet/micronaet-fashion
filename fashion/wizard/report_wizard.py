#|/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
from datetime import datetime
import pdb

class fashion_report_wizard(osv.osv_memory):
    ''' Manage report parameter (before printing)
    '''
    _name = 'fashion.report.wizard'
    _description = 'Report wizard'

    def get_form_id(self, cr, uid, context=None):
        return context.get('active_id', False)
    
    def get_partner_fabric_id(self, cr, uid, context=None):
        form_id = context.get('active_id', False)
        if form_id:
            form_proxy = self.pool.get('fashion.form').browse(cr, uid, form_id, context=context)
            if len(form_proxy.partner_rel_ids) == 1:
                return form_proxy.partner_rel_ids[0].id
        return False
    
    def onchange_type(self, cr, uid, ids, report_type, context=None):
        ''' Set default in report A
        '''
        res = {}
        res['value'] = {}
        res['value']['summary'] = report_type == 'a' # True only for A
        return res
    
    _columns = {
         'type': fields.selection([
             ('a', 'A - Scheda Storica'),
             ('b', 'B - Scheda Commerciale'),
             ('c', 'C - Scheda Tecnica'),
             ('d', 'Riscontro'),
             ('e', 'Lanciato'),
         ], 'Type of report', select=True),
         #'prototipe': fields.bolean('Prototipe'),
         'form_id': fields.many2one('fashion.form', 'Form'),
         'partner_fabric_id': fields.many2one('fashion.form.partner.rel', 'Partner Fabric'),
         'accessory_id': fields.many2one('fashion.form.accessory.rel', 'Accessory'),
         'summary': fields.boolean('Summary'), #TODO Inserire i gruppi
         'total': fields.boolean('Total'),
         'image': fields.boolean('Image'),
    }

    _defaults = {
        'type': 'a',
        'form_id': lambda s,cr,uid,ctx: s.get_form_id(cr, uid, ctx),
        'summary': True,
        'total': False,
        'image': True,
        'partner_fabric_id': lambda s,cr,uid,ctx: s.get_partner_fabric_id(cr, uid, ctx),
        #'prototipe': False,
    }

    def print_report(self, cr, uid, ids, context=None):
        ''' Print report passing parameter dictionary
        '''
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        datas = {}
        datas['from_wizard'] = True
        datas['active_ids'] = context.get('active_ids', [])
        datas['active_id'] = context.get('active_id', False)
        datas['partner_fabric_id'] = wiz_proxy.partner_fabric_id.id if wiz_proxy.partner_fabric_id else False
        datas['accessory_id'] = wiz_proxy.accessory_id.id if wiz_proxy.accessory_id else False
        datas['summary'] = wiz_proxy.summary
        datas['total'] = wiz_proxy.total
        datas['image'] = wiz_proxy.image
        #datas['note_fabric'] = wiz_proxy.partner_fabric_id.note_fabric if wiz_proxy.partner_fabric_id else ''
        #datas['partner_fabric_id'] = wiz_proxy.partner_fabric_id.id if wiz_proxy.partner_fabric_id else False
        
        if wiz_proxy.type == 'a':
            report = "fashion_form_A"
        elif wiz_proxy.type == 'b':
            report = "fashion_form_B"
        elif wiz_proxy.type == 'c':
            report = "fashion_form_C"
        elif wiz_proxy.type == 'd':
            report = "fashion_form_D"
        elif wiz_proxy.type == 'e':
            report = "fashion_form_E"
        else: # default
            report = "fashion_form_A"        
            
        return {
            'model': 'fashion.form',
            'type': 'ir.actions.report.xml',
            'report_name': report,
            'datas': datas,
            }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
