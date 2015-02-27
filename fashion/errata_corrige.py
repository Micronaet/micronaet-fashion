#!/usr/bin/python
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
import os
import sys
import csv
import base64
from openerp.osv import osv, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import tools
import pdb
from openerp.tools.translate import _


# Utility:
def Prepare(valore):
    # For problems: input win output ubuntu; trim extra spaces
    #valore=valore.decode('ISO-8859-1')
    valore=valore.decode('cp1252')
    valore=valore.encode('utf-8')
    return valore.strip()

def format_date(valore,date=True):
    ''' Formatta nella data di PG
    '''
    try:
        if date:
            gma = valore.split(' ')[0].split('/')
            return '%s-%02d-%02d' % (gma[2], int(gma[1]), int(gma[0]))
    except:
        return False

def format_currency(valore):
    ''' Formatta nel float per i valori currency
    '''
    try:
        return float(valore.split(' ')[-1].replace(',','.'))
    except:
        return 0.0

def format_search_float(valore):
    ''' Formatta nel float per i valori currency
    '''
    try:        
        valore = valore.replace(',', '.')
        tmp = ""
        for i in valore:
            if i.isdigit() or i == ".":
                tmp += i
            else:
                break # at first not number    
        return float(tmp)        
    except:
        return 0.0

class fashion_form_utility(osv.osv):
    ''' Utility procedure for errata corrige
    '''
    _name = 'fashion.form'
    _inherit = 'fashion.form'

    def correct_supplier_code(self, cr, uid, context=None):
        ''' test partner and find access_id + 1000 
        '''
        partner_pool = self.pool.get('res.partner')
        accessory_pool = self.pool.get('fashion.form.accessory.rel')
        accessory_ids = accessory_pool.search(cr, uid, [], context=context)
        for item in accessory_pool.browse(cr, uid, accessory_ids, context=context):        
            if item.supplier_id:
                access_id = item.supplier_id.access_id
                if access_id < 1000: # wrong supplier
                    partner_ids = partner_pool.search(cr, uid, [('access_id', '=', access_id + 1000)], context=context)
                    if partner_ids and len(partner_ids) == 1:
                        accessory_pool.write(cr, uid, item.id, {'supplier_id': partner_ids[0], }, context=context)                          
                        print "[INFO] Rel [%s] Update supplier_id %s with %s" % (item.id, item.supplier_id.id, partner_ids[0])
                    else:
                        print "[ERR] find partner_ids", partner_ids    
        return True
        
    def set_customer_code_in_form(self, cr, uid, context=None):
        ''' Read all customer code in customer and set if correct and present 
            in form if there's the same customer
        '''
        codes = {}
        form_pool = self.pool.get('fashion.form')
        form_ids = form_pool.search(cr, uid, [], context=context)
        form_proxy = form_pool.browse(cr, uid, form_ids, context=context)
        for item in form_proxy:
            partner_id = False
            code = False
            update = True
            for customer in item.partner_rel_ids:
                if customer.partner_id:
                    if not partner_id:
                        partner_id = customer.partner_id.id
                    if partner_id != customer.partner_id.id:
                        update = False
                        break
                    if customer.code: # take if present
                        code = customer.code    
            if update and code:
                codes[item.id] = code
        for key in codes:
            form_pool.write(cr, uid, key, {'customer_code': codes[key], }, context=context)                
        return True

    def set_correct_accessory_price(self, cr, uid, context=None):
        ''' Read files with price in rel and update only price
        '''
        print "Start import fashion.form.accessory.rel"
        file_input = os.path.expanduser('~/etl/fashion/SchXacc.txt')
        separator = '\t'
        lines = csv.reader(open(file_input,'rU'),delimiter=separator)
        max_col = False
        tot = 0
        accessory_pool = self.pool.get('fashion.form.accessory.rel')
        try:
            for line in lines:
                tot += 1
                if not max_col:
                    max_col = len(line)

                if len(line)!=max_col:
                    print "[ERROR]", tot, "Column error! "
                    continue

                access_id = line[0]
                #form = Prepare(line[1])
                #accessory = Prepare(line[2])
                #name = Prepare(line[3])
                #um = Prepare(line[4])
                quantity = format_currency(Prepare(line[5]))        
                #supplier = Prepare(line[6])
                currency = format_currency(Prepare(line[7]))
                #note = Prepare(line[8]) # TODO mettere nel database
                #gerber_name = Prepare(line[9])
                #gerber_desc = Prepare(line[10])
                #gerber_h = Prepare(line[11])
                #gerber_l = Prepare(line[12])
                tot_cost = currency * quantity if currency and quantity else 0.0
                
                #form_id = form_converter.get(form, False)
                #accessory_id = accessory_converter.get(form, False)
                #if not form_id or not accessory_id:
                #    print "[WARN] %s: Form %s (%s) or Accessory %s (%s) not found!!" % (
                #        tot, form, form_id, accessory, accessory_id)
                #    continue
                    
                accessory_ids = accessory_pool.search(cr, uid, [('access_id', '=', access_id)], context=context)
                if accessory_ids and (quantity or currency):
                    if len(accessory_ids) != 1:
                        print "Errore accessory must be 1"
                        continue
                    accessory_pool.write(cr, uid, accessory_ids[0], {
                        'quantity': quantity,
                        'currency': currency,
                        'tot_cost': tot_cost,
                    #'supplier_id': supplier_id,                            
                    }, context=context)
                    print "[INFO] Line %s Update %s {%s}!" % (tot, access_id, line)
                else:
                    #print "[WARN] Line %s Jumped Access_id %s!" % (tot, access_id)
                    pass
        except:
            print '[ERROR] Error importing data!'
        return True
        
    def set_user_comment(self, cr, uid, context=None):
            ''' Try to search user for comment
            '''
            print "Start association user comment"

            # Read all users:
            user_error = []
            users = {}
            user_pool = self.pool.get('res.users')
            user_ids = user_pool.search(cr, uid, [], context = context)
            user_proxy = user_pool.browse(cr, uid, user_ids, context = context)
            for item in user_proxy:
                users[item.login.lower()] = item.id
 
            # Find user for comment:
            comment_pool = self.pool.get('fashion.form.comment.rel')
            comment_ids = comment_pool.search(cr, uid, [('user_id', '=', 1)], context=context) # only admin
            for comment in comment_pool.browse(cr, uid, comment_ids, context=context):
                try:
                    login = comment.reference.lower() # can generate error
                    login = login.replace("-", " ")
                    login = login.replace("+", " ")
                    login = login.split(" ")[0] # take first                
                    if login in users:
                        comment_pool.write(cr, uid, comment.id, {
                            'user_id': users[login]
                        }, context=context)
                        print "[INFO] Update reference %s with user %s!" % (login, users[login])
                    else:
                        if login not in user_error:
                            user_error.append(login)
                except:
                    pass            
            print "User not found: %s" % (user_error)            
            return True
        
    def set_mt(self, cr, uid, context=None):
        ''' Try to search user for comment
        '''
        print "Start MT importation for partner"
        # Find user for comment:
        file_input = os.path.expanduser('~/etl/fashion/SchXcli.txt')
        separator = '\t'
        lines = csv.reader(open(file_input,'rU'), delimiter=separator)
        max_col = False
        tot = 0
        partner_pool = self.pool.get('fashion.form.partner.rel')
        jump = False
        try:
            for line in lines:
                tot += 1

                if jump and tot < jump: # jump first block yet imported
                    continue
                
                if tot % 500 == 0:
                    print "[INFO] %s Record read" % (tot)
                if not max_col:
                    max_col = len(line)

                if len(line) != max_col:
                    print "[ERROR]", tot, "Column error! "
                    continue

                access_id = line[0]
                if access_id < '16252':
                    continue
                h = format_search_float(line[9])
                mt = format_search_float(line[10])

                partner_ids = partner_pool.search(cr, uid, [('access_id', '=', access_id)], context=context)
                if partner_ids and (h or mt):
                    if len(partner_ids) != 1:
                        print "Errore accessory must be 1"
                        continue
                    try:    
                        partner_pool.write(cr, uid, partner_ids[0], {
                            'h_fabric': h,
                            'mt_fabric': mt,
                        }, context=context)
                    except:
                        print "[ERR] Error update!! Line %s Update H%s Mt%s {%s}!" % (tot, h, mt, line)
                        continue    
                    print "[INFO] Line %s Update H%s Mt%s {%s}!" % (tot, h, mt, line)
                else:
                    pass
        except:
            print '[ERROR] Error importing data!'
        return True

    def set_header(self, cr, uid, context=None):
        ''' Press button for generate header
        '''
        form_ids = self.search(cr, uid, [], context=context)        
        i = 0
        for form in self.browse(cr, uid, form_ids, context=context):
            i += 1
            if i % 500 == 0:
                print "[INFO] %s record updated" % (i)
            self.create_update_header(cr, uid, [form.id], context=context)
        return True

    def set_colors(self, cr, uid, context=None):
        ''' Read files with price in rel and update only price
        '''
        print "Start import fashion.form.accessory.rel"
        file_input = os.path.expanduser('~/etl/fashion/SchXacc.txt')
        separator = '\t'
        lines = csv.reader(open(file_input,'rU'),delimiter=separator)
        max_col = False
        tot = 0
        accessory_pool = self.pool.get('fashion.form.accessory.rel')
        try:
            for line in lines:
                tot += 1
                if not max_col:
                    max_col = len(line)

                if len(line)!=max_col:
                    print "[ERROR]", tot, "Column error! "
                    continue

                access_id = line[0]
                note = Prepare(line[8]) # colore
                if not note:
                    continue
                    
                accessory_ids = accessory_pool.search(cr, uid, [('access_id', '=', access_id)], context=context)
                if not accessory_ids or not note:
                    continue
                    
                if len(accessory_ids) != 1:
                    print "Errore accessory must be 1"
                    continue
                    
                accessory_pool.write(cr, uid, accessory_ids[0], {
                    'note': note,
                }, context=context)
                
                print "[INFO] Line %s Update %s Note/Colore: %s!" % (tot, access_id, note)
        except:
            print '[ERROR] Error importing data!'
        return True

    def explode_model(self, cr, uid, context=None):
        ''' Explode all model correctly
        '''
        print "Start exploding model in part of code"
        form_ids = self.search(cr, uid, [], context=context)
        i = 0
        for item in self.browse(cr, uid, form_ids, context=context):
            i += 1
            if i % 100 == 0:
                print "Record aggiornati: %s" % (i)
                
            # Force rewrite of model for raise write recalculatin of explosion:
            self.write(cr, uid, [item.id], {
                'model': item.model}, context=context)
        return True

    def explode_model_partner(self, cr, uid, context=None):
        ''' Explode all model correctly for partner
        '''
        print "Start exploding model in part of code"
        partner_pool = self.pool.get('fashion.form.partner.rel')
        partner_ids = partner_pool.search(cr, uid, [], context=context)
        i = 0
        for item in partner_pool.browse(cr, uid, partner_ids, context=context):
            i += 1
            if i % 100 == 0:
                print "Record aggiornati: %s" % (i)
                
            # Force rewrite of model for raise write recalculatin of explosion:
            partner_pool.write(cr, uid, [item.id], {
                #'model': item.model
                'model_customer': item.form_id.model_customer,
                'model_article': item.form_id.model_article,
                'model_number': item.form_id.model_number,
                'model_revision': item.form_id.model_revision,
                'review': item.form_id.review,                
            }, context=context)
            #print item.model, ">", item.form_id.model_customer, item.form_id.model_article, item.form_id.model_number, item.form_id.model_revision, item.form_id.review
        return True

    def force_all_recalculation(self, cr, uid, context=None):
        ''' Recompute all divided element depend on "model" value
            Use onchange function
        '''
        form_pool = self.pool.get('fashion.form')
        form_ids = form_pool.search(cr, uid, [], context=context)
        for form in form_pool.browse(cr, uid, form_ids, context=context):        
            res = form_pool.on_change_model(
                cr, uid, [form.id], 
                form.model, 
                form.review, 
                context=context)
            if 'warning' not in res and 'value' in res:
                form_pool.write(cr, uid, [form.id], res['value'], context=context)
                #print res['value']
            else:
                print "Errore su calcolando il modello: %s" % form.model
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
