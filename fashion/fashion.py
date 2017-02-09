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
import openerp 
import logging
import base64
from openerp.osv import osv, fields
from datetime import datetime
from openerp.tools import (DEFAULT_SERVER_DATETIME_FORMAT, 
    DEFAULT_SERVER_DATE_FORMAT)
from openerp import tools
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)

# --------
# Utility:
# --------
# TODO eliminare le funzioni, non devono stare qui!
def _get_image(self, cr, uid, ids, name, args, context=None):
    ''' Read image from file
    '''
    result = dict.fromkeys(ids, False)
    for obj in self.browse(cr, uid, ids, context=context):
        result[obj.id] = tools.image_get_resized_images(
            obj.image, avoid_resize_medium=True)
    return result

def _set_image(self, cr, uid, item_id, name, value, args, context=None):
    ''' Store image from file
    '''
    return self.write(cr, uid, [item_id], {
        'image': tools.image_resize_image_big(value)}, context=context)

def get_temp_filename(filename):
    ''' Get temp path for copy and paste functions
    '''
    return os.path.join(
        openerp.__path__[0], 'addons', 'fashion', 'temp', filename)

class fashion_season(osv.osv):
    '''Table that manages the seasons
    '''
    _name = 'fashion.season'
    _description = 'Season'
    _order = 'sequence,name'

    def set_obsolete(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'obsolete': context.get('obsolete',True)})
        return True
        
    def set_not_obsolete(self, cr, uid, ids, context=None):
        self.set_obsolete(cr, uid, ids, {'obsolete':False})
        return True
        
    _columns = {
         'sequence': fields.integer('Sequence'),
         'code': fields.char('Cod', size=10, required=True, 
             help='Code used in fabric for join in the name'),
         'name': fields.char('Name', size=40, required=True),
         'note': fields.text('Note'),
         'obsolete':fields.boolean('Obsolete'),
         
         # Link di importazione:
         'access_id': fields.integer(
             'Access ID', help="ID Importazione che tiene il link"),
    }

class fashion_article(osv.osv):
    '''Table that manages the articles
    '''
    _name = 'fashion.article'
    _description = 'Article'
    _order = 'name'

    _columns = {
         'name': fields.char('Name', size=40, required=True),
         'note': fields.text('Note'),
         'code': fields.char('Code', size=1),
         #'measure_ids': fields.many2many(
         #    'fashion.form.measure', 'fashion_form_article_rel',
         #    'article_id', 'measure_id', 'Measures', readonly = False),
         
         # Link di importazione:
         'access_id': fields.integer(
             'Access ID', help="ID Importazione che tiene il link"),
    }

class fashion_form_characteristic(osv.osv):
    '''Table that manages the characteristic
    '''
    _name = 'fashion.form.characteristic'
    _description = 'Characteristic'
    _order = 'sequence,name'

    _columns = {
         'name': fields.char('Name', size = 40, required = True),
         'note': fields.text('Note'),
         'sequence': fields.integer('Sequence'),

         # Link di importazione:
         'access_id': fields.integer(
             'Access ID', help="ID Importazione che tiene il link"),
    }

class fashion_form_cost(osv.osv):
    '''Table that manages the cost
    '''
    _name = 'fashion.form.cost'
    _description = 'Cost'
    _order = 'sequence,name'

    _columns = {
        'name': fields.char('Name', size = 40, required=True),
        'note': fields.text('Note'),
        'sequence': fields.integer('Sequence'),
        'cost': fields.float('Cost', digits=(12, 4)),
        'default': fields.boolean('Default'),
    
         # Link di importazione:
         'access_id': fields.integer(
             'Access ID', help="ID Importazione che tiene il link"),
     }

    _defaults = {
        'default': False,
    }

class fashion_form_accessory(osv.osv):
    '''Table that manages the accessory
    '''
    _name = 'fashion.form.accessory'
    _description = 'Accessory'
    _order = 'sequence,name'

    _columns = {
         'name': fields.char('Name', size = 40, required = True),
         'gerber_char': fields.char('Gerber char', size = 1, required = False),
         'note': fields.text('Note'),
         'sequence': fields.integer('Sequence'),
         'type': fields.selection([
                ('t', 'Cut'),
                ('a', 'Accessory'),
                ], 'Type', select=True),

         # Link di importazione:
         'access_id': fields.integer('Access ID', help="ID Importazione che tiene il link"),
    }
    _defaults = {
        'sequence': lambda *x: 1000, # normal accessory have high number
    }

class fashion_form_accessory_pricelist(osv.osv):
    '''Table that manages the accessory pricelist
    '''
    _name = 'fashion.form.accessory.pricelist'
    _description = 'Accessory pricelist'
    _order = 'supplier_id,create_date desc'

    # ------------------
    # Override function:
    # ------------------
    def name_get(self, cr, uid, ids, context=None):
        ''' Add customer-fabric ID to name
        '''
        res = []
        for item in self.browse(cr, uid, ids, context = context):
            res.append((item.id, "%s %s" % (item.name or '', item.extra_info or '')))
        return res        

    _columns = {
        'name': fields.char('Article', size=70, required=False),
        'accessory_id':fields.many2one('fashion.form.accessory', 'Accessory', 
            required=False, ondelete='cascade'),
        'supplier_id':fields.many2one('res.partner', 'Supplier', 
            required=True, domain=[('supplier','=',True)]),
        'create_date': fields.datetime('Date', readonly=True),
        'um': fields.char('U.M.', size=5, required=False),
        'extra_info': fields.char('Extra info', size=40, required=False),
        'note': fields.text('Note'),
        'cost': fields.float('Cost', digits=(12, 4)),

        # Link di importazione:
        'access_id': fields.integer(
            'Access ID', help="ID Importazione che tiene il link"),
        }

class fashion_form_accessory(osv.osv):
    '''Table that manages the accessory relation *2many
    '''
    _inherit = 'fashion.form.accessory'

    _columns = {
        'pricelist_ids':fields.one2many('fashion.form.accessory.pricelist', 
            'accessory_id', 'Pricelist', required=False),
        }

class fashion_form_fabric_composition(osv.osv):
    '''Table that manages the fabric composition
    '''

    _name = 'fashion.form.fabric.composition'
    _description = 'Fabric'
    _rec_name = 'code'
    _order = 'code'

    _columns = {
        'code': fields.char('Code', size = 15, required=True),
        'perc_composition': fields.char('Percentage composition', size=60),
        'note': fields.text('Note'),
        'symbol': fields.char('Wash symbol', size=10),
        'season_id': fields.many2one('fashion.season', 'Season'),
        }

class fashion_form_fabric(osv.osv):
    '''Table that manages the fabric
    '''
    _name = 'fashion.form.fabric'
    _description = 'Fabric'
    _rec_name = 'code'
    _order = 'code'

    # -------
    # Button:
    # -------
    def search_form_fabric(self, cr, uid, ids, context=None):
        ''' Search in rel customer-form the forms that use this fabric
            and return a tree view with it
        '''
        fabric_id = ids[0]
        rel_pool = self.pool.get('fashion.form.partner.rel')
        cr.execute("""
            SELECT distinct form_id 
            FROM fashion_form_partner_rel
            WHERE fabric_id = %s
            """ % fabric_id)
        form_ids = [i[0] for i in cr.fetchall()]    
        
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'fashion.form', # object linked to the view
            'domain': [('id', '=', form_ids)],
            'type': 'ir.actions.act_window',
            #'res_id': form_id,
            }             
        
    def search_form_fabric_symbol(self, cr, uid, ids, context=None):
        ''' Search in rel customer-form the forms that use this fabric
            and return a tree view with it
            Difference: symbol are changed 
        '''
        # Read current fabric:
        current_proxy = self.browse(cr, uid, ids, context=context)[0]
        
        fabric_id = ids[0]
        rel_pool = self.pool.get('fashion.form.partner.rel')
        cr.execute("""
            SELECT distinct form_id 
            FROM fashion_form_partner_rel
            WHERE 
                fabric_id = %s AND
                symbol_fabric != '%s'                
            """ % (
                fabric_id,
                current_proxy.symbol,
                ))
        form_ids = [i[0] for i in cr.fetchall()]    
        
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'fashion.form', # object linked to the view
            'domain': [('id', '=', form_ids)],
            'type': 'ir.actions.act_window',
            #'res_id': form_id,
            }             
        
    def load_from_composition(self, cr, uid, ids, context=None):
        ''' Search last part of code in composition and override 
            elements on fabric
            Code >> XXX-CCC  (CCC = composition)
        '''
        # TODO maybe better as onchange?
        fabric_proxy = self.browse(cr, uid, ids, context=context)[0]
        code = fabric_proxy.code.split('-')[-1] # 3 final char after "-"
        composition_pool = self.pool.get('fashion.form.fabric.composition')
        composition_ids = composition_pool.search(cr, uid, [
            ('season_id', '=', fabric_proxy.season_id.id),
            ('code', '=', code),
            ], context=context)
        
        if not composition_ids: # search without season (last from accounting)
            composition_ids = composition_pool.search(cr, uid, [
                ('code', '=', code)], context=context)
            
        if composition_ids:
            composition_proxy = composition_pool.browse(
                cr, uid, composition_ids, context=context)[0]
            self.write(cr, uid, ids, {
                'perc_composition': composition_proxy.perc_composition,
                'symbol': composition_proxy.symbol,
                }, context=context)
        else:
            raise osv.except_osv(_('Error'), _("Season and code not found!"))        
        return True        
    
    #Override:
    def name_get(self, cr, uid, ids, context=None):
        ''' Add season ID to name
        '''
        res = []
        for fabric in self.browse(cr, uid, ids, context=context):
            res.append((fabric.id, "%s-[%s]" % (
                fabric.code, 
                fabric.season_id.code if fabric.season_id else "", 
                #fabric.note or ''
                )))
        return res

    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Fabric Supplier'),
        'article_code': fields.char('Fabric Article code', size=50),
        'code': fields.char('Articolo', size=30, required=True),
        #'name': fields.char('Name', size = 20),
        #'composition': fields.char('Composition', size = 60),
        'perc_composition': fields.char('Percentage composition', size=60),
        #'note': fields.text('Note'),
        'note': fields.char('Note', size=100),
        'symbol': fields.char('Wash symbol', size=10),
        'season_id': fields.many2one('fashion.season', 'Season'),
        'test': fields.boolean('Test fabric', 
            help="This fabric is used for a model testing, maybe it won't be produced!"),
        'um': fields.char('U.M.', size=5),
        'cost': fields.float('Cost', digits=(10, 4)),
         
        # Manage from accounting employe:
        'weight': fields.float('Weight', digits=(10, 2)),
        'h_fabric': fields.float('H.', digits=(10, 2)),
        'range_supplier_cost': fields.char('Range Costo', size=50),
        'range_final_cost': fields.char('Prezzo base', size=50),
        'preferred_fabric': fields.char('Preferred fabric', size=50),
        'tag': fields.char('Cartellino', size=50),

        # Link di importazione:
        'access_id': fields.integer(
            'Access ID', help="ID Importazione che tiene il link"),
    }
    _defaults = {
        'um': lambda *x: 'MT'
    }

class fashion_form_stitch(osv.osv):
    '''Table that manages the stitch
    '''
    _name = 'fashion.form.stitch'
    _description = 'Stitch' #cuciture
    _order = 'sequence,name'

    _columns = {
         'name': fields.char('Name', size = 40, required = True),
         'note': fields.text('Note'),
         'sequence': fields.integer('Sequence'),
    
         # Link di importazione:
         'access_id': fields.integer('Access ID', 
             help="ID Importazione che tiene il link"),
    }

class fashion_form_measure(osv.osv):
    '''Table that manages the measure
    '''
    _name = 'fashion.form.measure'
    _description = 'Measure'
    _order = 'name'

    _columns = {
         'letter': fields.char('Letter', size=1),
         'name': fields.char('Description', size=40, required=True),
         'note': fields.text('Note'),

         # Link di importazione:
         'access_id': fields.integer('Access ID', 
             help="ID Importazione che tiene il link"),
    }

class fashion_form(osv.osv):
    ''' Table that manages the form
    '''
    _name = 'fashion.form'
    _inherits = {'product.product': 'product_id', }
    #_inherit = 'mail.thread' # link to messages
    _order = 'model_article,model_number desc,model_customer,model,review desc'
    _rec_name = 'model'

    _default_extension = 'jpg'
    
    # --------------------
    # On change functions:
    # --------------------
    def on_change_model(self, cr, uid, ids, model, review, context=None):
        ''' Split model code in all the part 
        '''
        res = {'value': {}}
        if not model:
            return res
        if not review:
            review = 0

        model = model.upper()
        res['value']['model'] = model
        res['value']['name'] = "%s.%s" % (model, review)
        
        if model[0:1].isalpha():
            if model[1:2].isalpha():
                model_customer = model[0:1]
                model_article = model[1:2]
            else:
                model_customer = False
                model_article = model[0:1]
        else:
            res['warning'] = {
                'title': _('warning'),
                'message': _('Error: Model must start with letter'),
            }
        res['value']['model_customer'] = model_customer
        res['value']['model_article'] = model_article
        model_number = ''
        i = 2 if model_customer else 1
        for c in model[2 if model_customer else 1:]:
            if c.isdigit():
                i += 1
                model_number += c
            else:
                break
                
        res['value']['model_number'] = int(
            model_number) if model_number.isdigit() else 0
        if res['value']['model_number'] and len(model)>i and model[i] == 'C':
            res['value']['conformed'] = True
            i += 1
        else:
            res['value']['conformed'] = False
        res['value']['model_revision'] = model[i:] or False            
        return res

    # ------------------
    # Utility functions:
    # ------------------
    # Naming function:
    def _get_form_name(self, model, review):
        ''' Return name of form element
        '''
        return "%s.%s" % (model, review)
    
    def _get_draw_image_name(self, obj):
        ''' Return name of image from browese obj passed
        '''
        return ("%s.%s" % (self._get_form_name(
            obj.model, obj.review), self._default_extension)).lower()
        
    # Image function:
    def _get_draw_image_type(self, field_name):
        ''' Return type of image depend on draw field name
        '''
        return field_name[-1].lower()

    def _load_image(self, name, type_image):
        ''' Load image from file:
        '''
        path = os.path.expanduser(os.path.join(
            "~/etl/fashion/image", type_image)) # TODO parametrize
        filename = os.path.join(path, name)
        try:
            f = open(filename, 'rb')
            img = base64.encodestring(f.read())
            f.close()
        except:
            img = False
        return img

    def _unload_image(self, name, value, type_image):
        ''' Unload image to file:
        '''
        path = os.path.expanduser(os.path.join(
            "~/etl/fashion/image", type_image)) # TODO parametrize
        filename = os.path.join(path, name)
        try:
            f = open(filename, 'wb')
            f.write(base64.decodestring(value))
            f.close()
            try: # Set parameter for update
                os.chmod(filename, 0777)
                os.chown(filename, -1, 1000)
            except:
                return True    
        except:
            return False
        return True
    
    def log_activity(self, cr, uid, ids, name, context=None): 
        ''' Add in activity list the change of state         
        '''
        if type(ids) not in (list, tuple):
            ids = [ids] # integer 
        log_pool = self.pool.get('fashion.form.comment.rel')
        log_pool.create(cr, uid, {
            'reference': False,
            'name': name,
            'user_id': uid,
            'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'hide_in_report': True,
            'form_id': ids[0],
            }, context=context)
        return True
    # ------------------
    # Override function:
    # ------------------
    def create(self, cr, uid, vals, context=None):
        """
        Create a new record for a model ModelName
        @param cr: cursor to database
        @param uid: id of current user
        @param vals: provides a data for new record
        @param context: context arguments, like lang, time zone
        
        @return: returns a id of new record
        """
        # Explode model element ("name" created in onchange "model.review")
        vals.update(self.on_change_model(
            cr, uid, 0, 
            vals.get('model', False), 
            vals.get('review', 0), 
            context=context)['value'])     
        return super(fashion_form, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Update record(s) comes in {ids}, with new value comes as {vals}
        return True on success, False otherwise
    
        @param cr: cursor to database
        @param uid: id of current user
        @param ids: list of record ids to be update
        @param vals: dict of new values to be set
        @param context: context arguments, like lang, time zone
        
        @return: True on success, False otherwise
        """
        # Test if one is modified, take data from database for other value 
        if 'model' in vals or 'review' in vals: # change also name and explode
            form_proxy = self.browse(cr, uid, ids, context = context)[0]
            
            # Explore model element:
            vals.update(self.on_change_model(
                cr, uid, 0, 
                vals.get('model', form_proxy.model), 
                vals.get('review', form_proxy.review), 
                context=context)['value'])
        return super(fashion_form, self).write(
            cr, uid, ids, vals, context=context)
            
    # ------------
    # Button event
    # ------------
    def open_form_item(self, cr, uid, ids, context=None):
        ''' Button for open detail in kanban view
        '''
        return {
            'name': _('Form detail'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fashion.form',
            'res_id': ids[0],
            'view_id': False,
            'views': [(False, 'form')],
            'target': 'new',
            'domain': [('id','=',ids[0])],
            'context': {},
            'type': 'ir.actions.act_window',
            }                

    def reset_duplicate_characteristic(self, cr, uid, ids, context=None):
        ''' Remove file used for copy paste operations
        '''
        fn = get_temp_filename("%s.car.dat" % uid) 
        try:
            os.remove(fn)
        except:
            return False    
        return True

    def paste_duplicate_characteristic(self, cr, uid, ids, context=None):
        ''' Paste operation in form
        '''
        fn = get_temp_filename("%s.car.dat" % uid) 
        try:
            f = open(fn, "r")
        except:
            # TODO Comunicate error?
            return False
        item_ids = [int(item) for item in f]
        f.close()
        
        characteristic_pool = self.pool.get('fashion.form.characteristic.rel')
        for item in characteristic_pool.browse(
                cr, uid, item_ids, context=context):
            characteristic_pool.create(cr, uid, {
                'name': item.name,
                'sequence': item.sequence,
                'form_id': ids[0],
                'characteristic_id': item.characteristic_id.id if item.characteristic_id else False,
                'lenght': item.lenght,
                'old_name': item.old_name,
                'stitch_type_id': item.stitch_type_id.id if item.stitch_type_id else False,
                'stitch_verse_id': item.stitch_verse_id.id if item.stitch_verse_id else False,
                'stitch_cut_id': item.stitch_cut_id.id if item.stitch_cut_id else False,
                'stitch_top_id': item.stitch_top_id.id if item.stitch_top_id else False,
                'stitch_top_type_id': item.stitch_top_type_id.id if item.stitch_top_type_id else False,
                'bindello': item.bindello,
                }, context=context)
        self.reset_duplicate_characteristic(cr, uid, ids, context=context)
        return True

    def reset_duplicate_accessory(self, cr, uid, ids, context=None):
        ''' Remove file used for copy paste operations
        '''
        fn = get_temp_filename("%s.acc.dat" % uid) 
        try:
            os.remove(fn)
        except:
            return False    
        return True

    def paste_duplicate_accessory(self, cr, uid, ids, context=None):
        ''' Paste operation in form
        '''
        fn = get_temp_filename("%s.acc.dat" % uid) 
        try:
            f = open(fn, "r")
        except:
            # TODO Comunicate error?
            return False
        item_ids = [int(item) for item in f]
        f.close()
        
        accessory_pool = self.pool.get('fashion.form.accessory.rel')
        for item in accessory_pool.browse(cr, uid, item_ids, context=context):
            accessory_pool.create(cr, uid, {
                'form_id': ids[0],
                'sequence': item.sequence,
                'accessory_id': item.accessory_id.id if item.accessory_id else False,
                'fabric_id': item.fabric_id.id if item.fabric_id else False,
                'name': item.name,
                'code': item.code,
                'um': item.um,
                'quantity': item.quantity,
                'currency': item.currency,
                'note': item.note,
                'gerber_name': item.gerber_name,
                'gerber_desc': item.gerber_desc,
                'gerber_h': item.gerber_h,
                'gerber_l': item.gerber_l,
                'supplier_id': item.supplier_id.id if item.supplier_id else False,
                'pricelist_id': item.pricelist_id.id if item.pricelist_id else False,
                'tot_cost': item.tot_cost,
                'color': item.color,
                'h': item.h,
                }, context=context)
        self.reset_duplicate_accessory(cr, uid, ids, context=context)
        return True
            
    def set_not_cost_model(self, cr, uid, ids, context=None):
        ''' Set form for no manage costs
        '''
        return self.write(cr, uid, ids, {
            'model_for_cost': False}, context=context)

    def set_cost_model(self, cr, uid, ids, context=None):
        ''' Set form for no manage costs
        '''
        # Set default fixed cost in list:
        form_proxy = self.browse(cr, uid, ids, context=context)[0]
        cost_list_ids = [item.cost_id.id for item in form_proxy.cost_rel_ids]
        
        cost_pool = self.pool.get('fashion.form.cost')
        default_ids = cost_pool.search(cr, uid, [
            ('default','=',True)], context=context)
        for cost in cost_pool.browse(cr, uid, default_ids, context=context):
            if cost.id not in cost_list_ids:
                # Create cost and pricelist:
                self.pool.get('fashion.form.cost.rel').create(cr, uid, {
                    'form_id': ids[0],
                    'cost_id': cost.id,
                    'value': cost.cost or 0.0
                }, context=context)
        return self.write(cr, uid, ids, {
            'model_for_cost': True}, context=context)
        
    def button_refresh(self, cr, uid, ids, context=None):
        ''' Dummy action for refresh form
        '''
        return True
        
    def create_update_header(self, cr, uid, ids, context=None):
        ''' Create a particular line for header (tg. values)
            > fashion.form.measure.rel
        '''
        try:
            # test if there's yet a header line
            found_id = False
            form_proxy = self.browse(cr, uid, ids, context=context)[0]
            for measure in form_proxy.measure_rel_ids:
                if measure.header:
                    found_id = measure.id
                    break
                
            start = int(form_proxy.size_base or '42') - 2 * (
                (form_proxy.col_ref or 3) - 1)
            data = {
                'header': True,
                'sequence': 0,
                'form_id': form_proxy.id,
                'measure_id': False,
                'name': _('Header'),
                'size_1': "Tg.%s" % (start),
                'size_2': "Tg.%s" % (start + 2),
                'size_3': "Tg.%s" % (start + 4),
                'size_4': "Tg.%s" % (start + 6),
                'size_5': "Tg.%s" % (start + 8),
                'size_6': "Tg.%s" % (start + 10),
                'size_7': "Tg.%s" % (start + 12),
                'size_8': "Tg.%s" % (start + 14),
                'size_9': "Tg.%s" % (start + 16),
                'size_10': "Tg.%s" % (start + 18),
                'size_11': "Tg.%s" % (start + 20),
                'size_12': "Tg.%s" % (start + 22),
                'size_13': "Tg.%s" % (start + 24),
                'visible': False,
                'real': False,
            }        
            measure_pool = self.pool.get('fashion.form.measure.rel')
            if found_id: # Update
                measure_pool.write(cr, uid, found_id, data, context=context)
            else:     # Create a header elements:
                measure_pool.create(cr, uid, data, context=context)
        except: 
            return False # if error no creation        
        return True

    def insert_article(self, cr, uid, ids, context=None):
        '''Insert the measure of article 
           Delete all lines before and recreate
        '''
        form_proxy = self.browse(cr, uid, ids, context=context)[0]
        # test if article is selected:
        if not form_proxy.article_id:
            return True

        # Delete all items:
        res_pool = self.pool.get('fashion.form.measure.rel')
        res_ids = res_pool.search(
            cr, uid, [('form_id', '=', ids[0])], context=context)
        res_pool.unlink(cr, uid, res_ids, context=context)    

        # create header line:
        self.create_update_header(cr, uid, ids, context=context)
        
        # after load article item list:
        for item_id in [
                l.measure_id.id for l in form_proxy.article_id.fashion_measure_ids]:
            res_pool.create(cr, uid, {
                'measure_id': item_id, 
                'form_id': ids[0],
                'visible': True, 
                }, context=context)
        return True

    def empty_article(self, cr, uid, ids, context=None):
        ''' Keep current list but empty all measure
        '''
        form_proxy = self.browse(cr, uid, ids, context=context)[0]
        for item in form_proxy.measure_rel_ids:
            if item.header: # jump header
                continue
            data = {}
            for col in range(1, 13):                
                if col == 3:
                    continue
                data["size_%s" % col] = False
            self.pool.get('fashion.form.measure.rel').write(
                cr, uid, item.id, data, context=context)
                
        return True
    
    def reload_measure(self, cr, uid, ids, context=None):
        ''' Delete all measure list 
            Create empyt list depend on type of article selected
        '''
        # Get current record:
        form_proxy = self.browse(cr, uid, ids, context=context)[0]

        if not form_proxy.article_id:
            return False # TODO comunicare l'errore perchè non è presente l'art.
        
        # delete all elements:
        measure_pool = self.pool.get('fashion.form.measure.rel')
        measure_ids = measure_pool.search(cr, uid, [
            ('form_id','=',ids[0])], context = context)
        measure_pool.unlink(cr, uid, measure_ids, context = context)
        
        # Loop in all measure of the article selected:
        for measure in form_proxy.article_id.measure_ids: 
            measure_pool.create(cr, uid, 
                {'form_id': ids[0],
                 'measure_id': measure.id,
                }, context = context)
        return True

    def modify_draw_image(self, cr, uid, item_id, context=None):
        ''' Call url if format: 
                fashion://name of image (in format model.version.extension)
            item_id: ID of the image selected
            context: 'side': 'A' or 'side': 'B'
        '''        
        form_proxy = self.browse(cr, uid, item_id, context=context)[0]

        final_url = (r"fashion://%s/%s.%s.%s" % (
            context.get('side', 'A'),
            form_proxy.model,
            form_proxy.review,
            self._default_extension, 
        )).lower()

        return {
            'type': 'ir.actions.act_url', 
            'url':final_url, 
            'target': 'new'
        }
        
    def reset_image(self, cr, uid, ids, context=None):
        ''' Reset form image
        '''        
        try:
            self.write(cr, uid, ids, {'draw_image_%s' % (context.get(
                'side').lower()):False},context=context)
        except:
            pass    
        return True

    #============================#
    # Workflow Activity Function #
    #============================#
    def form_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
 
    def form_sample(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'sample'}, context=context)

    def form_ok(self, cr, uid, ids, context=None):
        # Log activity:
        self.log_activity(cr, uid, ids, _('CAMBIO STATO: OK PRODURRE'), 
            context=context)  
        return self.write(cr, uid, ids, {'state': 'ok'}, context=context)

    def form_produced(self, cr, uid, ids, context=None):
        # Log activity:
        self.log_activity(cr, uid, ids, _('CAMBIO STATO: PRODOTTO'), 
            context=context)          
        return self.write(cr, uid, ids, {'state': 'produced'}, context=context)

    def form_discarded(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {
            'state': 'discarded'}, context=context)
    
    # ----------------
    # Fields functions
    # ----------------
    def _get_sum_items(self, cr, uid, ids, name, args, context=None):
        ''' Calculate total sum for costs (cost list and accessory)
        '''
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = {}
            res[obj.id]['sum_accessory'] = 0.0
            res[obj.id]['sum_cost'] = 0.0
            if obj.model_for_cost: # calculate only if it's a model (for speed)
                for accessory in obj.accessory_rel_ids:
                    res[obj.id]['sum_accessory'] += accessory.tot_cost
                for cost in obj.cost_rel_ids:
                    res[obj.id]['sum_cost'] += cost.value          
                res[obj.id]['sum_extra_cost'] = res[obj.id][
                    'sum_cost'] + res[obj.id]['sum_accessory']
                             
            else:
                res[obj.id]['sum_extra_cost'] = 0.0

        return res
        
    def _get_draw_image(self, cr, uid, ids, name, args, context=None):
        ''' Read image from file according to name and version format:
            MODEL.VERSION.ext
        '''
        res = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = self._load_image(
                self._get_draw_image_name(obj), 
                self._get_draw_image_type(name)) # TODO parametrize
        return res

    def _set_draw_image(self, cr, uid, item_id, name, value, args, context=None):
        ''' Write image passed to file
        '''
        obj_proxy = self.browse(cr, uid, item_id, context=context)
        self._unload_image(
            self._get_draw_image_name(obj_proxy), value, 
            self._get_draw_image_type(name)) # TODO test return value
    
    # Resizing function:
    def _get_resized_image(self, cr, uid, ids, name, args, context=None):
        ''' Resize defaulf draw_image_a
        '''
        type_of_image = name.split("_")[-1] # from field name (last block)
        if type_of_image == 'medium':
            width = 800
        elif type_of_image == 'small':
            width = 200
        else:
            width = 64
            
        res = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = tools.image_resize_image(
                obj.draw_image_a, size=(width, None), encoding='base64', 
                filetype=self._default_extension, avoid_if_small=True) # 'PNG'
        return res

    def _set_resized_image(self, cr, uid, item_id, name, value, args, context=None):
        ''' Store image in original field: draw_image_a 
            (call field function for file image)
        '''
        return self.write(cr, uid, [item_id], {'draw_image_a': value, }, context=context)
        
            
    def invoice_print(self, cr, uid, ids, context=None):
        ''' This function prints the invoice and mark it as sent, so that we 
            can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
            'ids': ids,
            'model': 'account.invoice',
            'form': self.read(cr, uid, ids[0], context=context)
            }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.invoice',
            'datas': datas,
            'nodestroy' : True
        }
    
    def set_obsolete(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'obsolete': context.get('obsolete',True)})
        return True
        
    def set_not_obsolete(self, cr, uid, ids, context=None):
        self.set_obsolete(cr, uid, ids, {'obsolete':False})
        return True

    # Detail information functions:
    def _get_detail_informations(self, cr, uid, ids, fields, args, context=None):
        ''' Get detail information about fabric and customer
        '''
        res = {}
        for form in self.browse(cr, uid, ids, context=context):
            res[form.id] = {}
            res[form.id]['detail_info_partner'] = ''
            res[form.id]['detail_info_fabric'] = ''
            res[form.id]['detail_partner'] = False # only for search
            res[form.id]['detail_fabric'] = False  # only for search
            
            for detail in form.partner_rel_ids:
                res[form.id]['detail_info_partner'] += "%s\n" % (
                    detail.partner_id.name if detail.partner_id else "?",
                    )
                res[form.id]['detail_info_fabric'] += "%s\n" % (
                    detail.fabric_id.code if detail.fabric_id else "?",
                    )
        return res
        
    def _search_detail_info(self, cr, uid, obj, name, args, context=None):
        ''' Search in detail information seeking partner
        '''
        if name == 'detail_partner':
            field_name = 'partner_id'
        else: # detail_fabric
            field_name = 'fabric_id' 

        try:
            search_id = args[0][2]
            cr.execute("""
                SELECT DISTINCT form_id 
                FROM fashion_form_partner_rel 
                WHERE %s = %s;
                """ % (field_name, search_id))
            return [('id', 'in', 
                [item[0] for item in cr.fetchall()])]
        except:        
            return [('id', 'in', [])] # if error
            
    _columns = {
         'model': fields.char('Model', size=10, required=True),
         'customer_code': fields.char('Customer code', size=18),
         'size_base': fields.char('Size', size=30, 
             help='Basic size reference, ex:42', required=True),
         'size_measure': fields.char('Column for feedback', size=30, 
             help='Size basis for the measurement'),
         'review': fields.integer('Review', help='Revision of the main model',
             required=True),
         'date': fields.date('Date', help='Date of revision'),
         'create_date': fields.datetime('Create date', readonly=True),
         'write_date': fields.datetime('Date Last modify', readonly=True),
         'write_uid': fields.many2one('res.users', 'by User', readonly=True),
         'original': fields.char('Original', size=80),
         'base_id': fields.many2one('fashion.form', 'Base form', 
             help="Duplicated from"),
         'base_name': fields.char('Duplicated form', size=40),
         'h_lining': fields.char('Height lining', size=10),
         'mt_lining': fields.char('Meters lining', size=10),
         'cost_lining': fields.float('Cost lining', digits=(10,2)),
         'conformed': fields.boolean('Conformed', 
             help='Indicates that the model uses standardized sizes'),
         'start': fields.integer('Start size', 
             help='Departure for the standardized sizes'),
         'ironing': fields.text('Ironing'),
         'area': fields.char('Area', size=30, help='Link the table Gerber'),
         'user_id': fields.many2one('res.users', 'User'),
         'cut': fields.char('Size n.', size=40),
         'size': fields.text('Sizes'),
         'colors': fields.char('Colors', size=40),
         'article_id': fields.many2one('fashion.article', 'Article'),
         'season_id': fields.many2one('fashion.season', 'Season'),
         'obsolete': fields.boolean('Obsolete', 
             help='Indicates that the form is old'),
         'reactivate': fields.boolean('Not Obsolete', 
             help='Indicates that the form is not old'),
         'old_model': fields.boolean('Old Model'),
         'show_old_model': fields.boolean('Show old model'),
         'washing': fields.text('Washing'),
         'model_for_cost': fields.boolean('Model for cost', 
             help='Indicates that this form is use for create a pricelist'
                 ' elements'),
         'col_ref': fields.selection([
             (1,'col 1'), (2,'col 2'), (3,'col 3'), (4,'col 4'), (5,'col 5'),
             (6,'col 6'), (7,'col 7'), (8,'col 8'), (9,'col 9'), (10,'col 10'),
             (11,'col 11'), (12,'col 12'),
             ], 'Column reference', select=True, required=True),
         
         # Function for totals:
         'sum_accessory': fields.function(_get_sum_items, 
             string="Total accessory", 
             type="float", digits=(10, 2), store=False, multi='totals',
             help="Sum of the accessory list (see page Accessory for details)",
             ),
         'sum_cost': fields.function(_get_sum_items, string="Total cost list", 
             type="float", digits=(10, 2), store=False, multi='totals',
             help="Sum of costs in the list on the left"),
         'sum_extra_cost': fields.function(_get_sum_items, 
             string="Total extra cost", 
             type="float", digits=(10, 2), store=False, multi='totals',
             help="Sum of accessory cost and cost list "
                 "(no fabric in this total)"),
         
         # Image:
         'draw_image_a': fields.function(_get_draw_image, 
             fnct_inv=_set_draw_image,
             string="Draw Image A", type="binary",
             help="Image for draw side A. Usual size:"\
                  "1024 x 768"\
                  "The image is printed in report form and, in small size"\
                  "in kanban report views"),
         'draw_image_b': fields.function(_get_draw_image, 
             fnct_inv=_set_draw_image,
             string="Draw Image B", type="binary",
             help="Image for draw side B. Usual size:"\
                  "1024 x 768"\
                  "The image is printed in report form and, in small size"\
                  "in kanban report views"),
         
         # Photos:
         'draw_image_c': fields.function(_get_draw_image, 
             fnct_inv=_set_draw_image,
             string="Photo", type="binary",
             help="Image for draw side B. Usual size:"\
                  "1024 x 768"\
                  "The image is printed in report form and, in small size"\
                  "in kanban report views"),
         'draw_image_d': fields.function(_get_draw_image, 
             fnct_inv=_set_draw_image,
             string="Photo", type="binary",
             help="Image for draw side B. Usual size:"\
                  "1024 x 768"\
                  "The image is printed in report form and, in small size"\
                  "in kanban report views"),

        # Resize dinamically images:
        'draw_image_a_medium': fields.function(_get_resized_image, 
            fnct_inv=_set_resized_image,
            string="Medium-sized image", type="binary",
            help="Medium-sized image of the product. It is automatically "
                 "resized as a 800px large image, with aspect ratio preserved "
                 "only when the image exceeds one of those sizes. Use this "
                 "field in form views or some kanban views."),
                 
        'draw_image_a_small': fields.function(_get_resized_image, 
            fnct_inv=_set_resized_image,
            string="Small-sized image", type="binary",
            help="Small-sized image of the product. It is automatically"
                 "resized as a 128px large image, with aspect ratio preserved."
                 "Use this field anywhere a small image is required."),

         # Inherit fields:
         'product_id': fields.many2one('product.product', 'Product',
              ondelete = "restrict", required=True,
              help="Inherits value for link form to a product"),

         # Details fields (and search)
         'detail_info_partner': fields.function(
             _get_detail_informations, method=True, type='text', 
             string='Detail customer', store=False, multi='detail_info'), 
         'detail_info_fabric': fields.function(
             _get_detail_informations, method=True, type='text', 
             string='Detail fabric', store=False, multi='detail_info'), 
         'detail_partner': fields.function(
             _get_detail_informations, method=True, 
             type='many2one', relation='res.partner',
             string='Detail partner', 
             fnct_search=_search_detail_info,
             store=False, multi='detail_info'),
         'detail_fabric': fields.function(
             _get_detail_informations, method=True,
             type='many2one', relation='fashion.form.fabric',
             string='Detail fabric', 
             fnct_search=_search_detail_info,
             store=False, multi='detail_info'), 

         # Explosion of model (on change setted)
         'model_customer': fields.char('Sigla cliente', size=1), 
         'model_article': fields.char('Sigla articolo', size=1),
         'model_number': fields.integer('Numero modello'),
         'model_revision': fields.char('Revisione', size=3),

         # Workflow fields:     
         'state': fields.selection([
             ('draft', 'Draft'),
             ('sample', 'Sample'),
             ('ok', 'Ok production'),
             ('produced', 'Produced'),
             ('discarded', 'Discarded'),
             ], 'State', select=True),

         # Link di importazione:
         'access_id': fields.integer('Access ID', 
             help="ID Importazione che tiene il link"),
             }

    _defaults = {
        'date': lambda *a: datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
        'state': lambda *a: 'draft',
        'user_id': lambda s, cr, uid, ctx: uid,
        'old_model': lambda *x: False,
        'show_old_model': lambda *x: False,
        'col_ref': lambda *a: 3,
        'model_for_cost': False,
        }

# -----------------------------------------------------------------------------
#                               Object relations  
# -----------------------------------------------------------------------------
class fashion_form_measure_rel(osv.osv):
    '''Table that manage the relation measure/form
    '''
    _name = 'fashion.form.measure.rel'
    _description = 'Measure relation'
    _order = 'header desc,sequence,id'
        
    def clean_measure(self, cr, uid, ids, context=None):
        ''' Clean only measure in this line passed
        '''        
        return self.write(cr, uid, ids, {
            'size_1': False,
            'size_2': False,
            'size_3': False,
            'size_4': False,
            'size_5': False,
            'size_6': False,
            'size_7': False,
            'size_8': False,
            'size_9': False,
            'size_10': False,
            'size_11': False,
            'size_12': False,
            'size_13': False,
            'real': False,
            }, context=context)
            
    _columns = {
        'header': fields.boolean('Header'),
        'sequence': fields.integer('Seq.'),
        'form_id': fields.many2one('fashion.form', 'Form'),
        'measure_id': fields.many2one('fashion.form.measure', 'Measure'),
        'name': fields.text('Description'),
        'size_1': fields.char('Size 1', size = 10),
        'size_2': fields.char('Size 2', size = 10),
        'size_3': fields.char('[Size 3]', size = 10),
        'size_4': fields.char('Size 4', size = 10),
        'size_5': fields.char('Size 5', size = 10),
        'size_6': fields.char('Size 6', size = 10),
        'size_7': fields.char('Size 7', size = 10),
        'size_8': fields.char('Size 8', size = 10),
        'size_9': fields.char('Size 9', size = 10),
        'size_10': fields.char('Size 10', size = 10),
        'size_11': fields.char('Size 11', size = 10),
        'size_12': fields.char('Size 12', size = 10),
        'size_13': fields.char('Size 13', size = 10),
        'visible': fields.boolean('Visible', size = 10, 
            help='Indicates is the size is visible in the form reply'),
        'real': fields.char('Real', size = 10),

        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        }
    
    _defaults = {
        'header': lambda *x: False,
        'sequence': lambda *x: 0,
        }

class fashion_form_characteristic_rel(osv.osv):
    '''Table that manage the relation characteristic/form
    '''
    _name = 'fashion.form.characteristic.rel'
    _description = 'Form characteristic relation'
    _order = 'sequence,id'

    # ----------------
    # On change event:
    # ----------------
    def on_change_upper_characteristic(self, cr, uid, ids, name, context=None):
        ''' Manages the capital of the fields in the form Characteristic
        '''
        res = {'value': {}}
        if name:
            res['value']['name'] = name.upper()
        return res

    def on_change_upper_lenght(self, cr, uid, ids, lenght, context=None):
        ''' Manages the capital of the fields in the form Characteristic
        '''
        res = {'value': {}}
        if lenght:
            res['value']['lenght'] = lenght.upper()
        return res
    
    # -------------
    # Button event:
    # -------------    
    def duplicate_characteristic(self, cr, uid, ids, context=None):
        ''' Duplicate characteristic element
        '''
        fn = get_temp_filename("%s.car.dat" % uid) 
        f = open(fn, "a")
        f.write("%s\n" % ids[0])
        f.close()
        return True

    _columns = {
        'sequence': fields.integer('Seq.'),    
        'form_id': fields.many2one('fashion.form', 'Form'),
        'characteristic_id': fields.many2one('fashion.form.characteristic', 
            'Characteristic'),
        'name': fields.text('Description'),
        'lenght': fields.char('Lenght', size=30),         
        'old_name': fields.char('Old name', size=30),
        'stitch_type_id': fields.many2one(
            'fashion.form.characteristic.rel.specific', 'Stitch type', 
            domain=[('type','=','1')]),
        'stitch_verse_id': fields.many2one(
            'fashion.form.characteristic.rel.specific', 'Stitch verse', 
            domain=[('type','=','2')]),
        'stitch_cut_id': fields.many2one(
            'fashion.form.characteristic.rel.specific', 'Stitch cut', 
            domain=[('type','=','3')]),
        'stitch_top_id': fields.many2one(
            'fashion.form.characteristic.rel.specific', 'Stitch top', 
            domain=[('type','=','4')]),
        'stitch_top_type_id': fields.many2one(
            'fashion.form.characteristic.rel.specific', 'Stitch top type', 
            domain=[('type','=','5')]),
        'bindello': fields.boolean('Bindello'),
         
        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        }
    _defaults = {
        'sequence': lambda *x: 1,
        }

class fashion_form_characteristic_rel_specific(osv.osv):
    '''Table that manage the specific of characteristic
    '''
    _name = 'fashion.form.characteristic.rel.specific'
    _description = 'Specific'
    _order = 'type,name'

    def create(self, cr, uid, vals, context=None):
        """
        Create a new record for a model ModelName
        @param cr: cursor to database
        @param uid: id of current user
        @param vals: provides a data for new record
        @param context: context arguments, like lang, time zone
        
        @return: returns a id of new record
        """
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        #return osv.osv.create(self, cr, uid, ids, context=context)
        return super(fashion_form_characteristic_rel_specific, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Update redord(s) comes in {ids}, with new value comes as {vals}
        return True on success, False otherwise
    
        @param cr: cursor to database
        @param uid: id of current user
        @param ids: list of record ids to be update
        @param vals: dict of new values to be set
        @param context: context arguments, like lang, time zone
        
        @return: True on success, False otherwise
        """
    
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        #return osv.osv.create(self, cr, uid, ids, context=context)
        return super(fashion_form_characteristic_rel_specific, self).create(
            cr, uid, ids, vals, context=context)
    
    _columns = {
        'name': fields.text('Description'),
        'type': fields.selection([
            ('1', 'Col1'),
            ('2', 'Col2'),
            ('3', 'Col3'),
            ('4', 'Col4'),
            ('5', 'Col5'), ], 'Type', select=True),

        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        }

class fashion_form_cost_rel(osv.osv):
    '''Table that manage the relation cost/form
    '''
    _name = 'fashion.form.cost.rel'
    _description = 'Relation'
    _rec_name = 'note'

    _columns = {
        'form_id': fields.many2one('fashion.form', 'Form'),
        'cost_id': fields.many2one('fashion.form.cost', 'Cost', required=True),
        'value': fields.float('Value'),
        'note': fields.text('Note'),

        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        }

class fashion_form_cost_rel_pricelist(osv.osv):
    '''Table that manage the pricelist elements for signle cost
    '''
    _name = 'fashion.form.cost.rel.pricelist'
    _description = 'Pricelist'
    _rec_name = 'value'

    _columns = {
        'current': fields.boolean('Current', required=False),
        'cost_rel_id': fields.many2one('fashion.form.cost.rel', 'Cost'),
        'supplier_id': fields.many2one('res.partner', 'Supplier', 
            domain=[('supplier','=',True)]),
        'value': fields.float('Value', required=True),
        'order': fields.char('Order ref.', size=64),
        'reference': fields.char('Reference', size=64),
        'note': fields.text('Note'),

        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        }
    
    _defaults = {
        'current': False,
        }

class fashion_form_cost_rel(osv.osv):
    '''Table that manage the relation cost/form
    '''
    _name = 'fashion.form.cost.rel'
    _inherit = 'fashion.form.cost.rel'
    
    _columns = {
        'pricelist_ids':fields.one2many('fashion.form.cost.rel.pricelist', 
            'cost_rel_id', 'Pricelist', required=False),
        }
    
class fashion_form_accessory_rel(osv.osv):
    '''Table that manage the relation accessory/form
    '''
    _name = 'fashion.form.accessory.rel'
    _description = 'Relation accessory'
    _order = 'sequence,id'
    
    # -------------
    # Button event:
    # -------------    
    def duplicate_accessory(self, cr, uid, ids, context=None):
        ''' Duplicate accessory element
        '''        
        fn = get_temp_filename("%s.acc.dat" % uid)         
        f = open(fn, "a")
        f.write("%s\n" % ids[0])
        f.close()
        return True 
    
    # ----------
    # On change:
    # ----------    
    def on_change_calcolate_cost(self, cr, uid, ids, quantity, currency, context=None):
        '''Calcolate the total cost of the accessory
        '''
        res = {'value': {}}
        if quantity and currency:
            res['value']['tot_cost'] = quantity * currency
        else:
            res['value']['tot_cost'] = 0.0
        return res


    def onchange_accessory(self, cr, uid, ids, accessory_id, context=None):
        ''' Read gerber letter and write in code
        '''
        res = {'value': {}, }
        if accessory_id:
            accessory_pool = self.pool.get('fashion.form.accessory')
            accessory_proxy = accessory_pool.browse(
                cr, uid, accessory_id, context=context)
            if accessory_proxy.gerber_char:
                res['value']['code'] = accessory_proxy.gerber_char
                res['value']['sequence'] = accessory_proxy.sequence
            else:    
                res['value']['code'] = accessory_proxy.gerber_char
            #res['domain']['pricelist_id'] = [('accessory_id','=',accessory_id)]
                
        else:
            res['value']['code'] = False                    
            #res['domain']['pricelist_id'] = []
        return res
            
    def on_change_upper_code(self, cr, uid, ids, code, context=None):
        ''' Manages the capital of the fields in the form Accessory
        '''
        res = {'value': {}}
        if code:
            res['value']['code'] = code.upper()
        return res
    
    def on_change_upper_accessory(self, cr, uid, ids, name, context=None):
        ''' Manages the capital of the fields in the form Accessory
        '''
        res = {'value': {}}
        if name:
            res['value']['name'] = name.upper()
        return res

    def on_change_upper_um(self, cr, uid, ids, um, context=None):
        ''' Manages the capital of the fields in the form Accessory
        '''
        res = {'value': {}}
        if um:
            res['value']['um'] = um.upper()
        return res

    def on_change_upper_color(self, cr, uid, ids, note, context=None):
        ''' Manages the capital of the fields in the form Accessory
        '''
        res = {'value': {}}
        if note:
            res['value']['note'] = note.upper()
        return res
    
    def onchange_fabric(self, cr, uid, ids, fabric_id, context=None):
        ''' On change fabric 
            search supplier and description from PC
        '''
        res = {'value': {'supplier_id': False, 'name': False}}
        if fabric_id:
            fabric_pool = self.pool.get('fashion.form.fabric')
            try:
                fabric_proxy = fabric_pool.browse(
                    cr, uid, fabric_id, context=context)
                res['value']['supplier_id'] = fabric_proxy.supplier_id and fabric_proxy.supplier_id.id or False
                res['value']['currency'] = fabric_proxy.cost or 0.0
                res['value']['name'] = "%s - %s" % (
                    fabric_proxy.code or "", 
                    fabric_proxy.perc_composition or "")
            except:
                return res    
        return res
        
    def onchange_pricelist(self, cr, uid, ids, pricelist_id, context=None):
        ''' Save pricelist info in accessory rel        
        '''    
        res = {}
        res['value'] = {}
        if pricelist_id:
            pricelist_proxy = self.pool.get(
                "fashion.form.accessory.pricelist").browse(
                    cr, uid, pricelist_id, context=context)
            res['value']['supplier_id'] = pricelist_proxy.supplier_id.id if pricelist_proxy.supplier_id else False
            res['value']['currency'] = pricelist_proxy.cost or 0.0
            res['value']['h'] = pricelist_proxy.extra_info or False
            res['value']['um'] = pricelist_proxy.um or False
            res['value']['name'] = pricelist_proxy.name or False
            #res['value']['article_id'] = pricelist_proxy.article_id.id if pricelist_proxy.article_id else False
        else: 
            res['value']['supplier_id'] = False
            res['value']['currency'] = 0.0
            res['value']['h'] = False
            res['value']['um'] = False
            res['value']['name'] = False
        return res

    _columns = {
        'form_id': fields.many2one('fashion.form', 'Form'),
        'sequence': fields.integer('Seq.'),
        'accessory_id': fields.many2one('fashion.form.accessory', 'Accessory'),
        'fabric_id': fields.many2one('fashion.form.fabric', 'Fabric'),
        'name': fields.text('Description'),
        'code': fields.char('Code', size=1),   # TODO farlo diventare related (di fatto non viene modificato dalla videata ma prende sempre quello dell'articolo
        'um': fields.char('U.M.', size=5),
        'quantity': fields.float('Quantity', digits=(10, 4)),
        'currency': fields.float('Cost', digits=(10, 4)),
        'note': fields.text('Color'),
        'gerber_name': fields.char('Gerber name', size=10),
        'gerber_desc': fields.char('Gerber description', size=10),
        'gerber_h': fields.char('Gerber height', size=10),
        'gerber_l': fields.char('Gerber length', size=10),
        'supplier_id': fields.many2one('res.partner', 'Supplier', 
            domain=[('supplier','=',True)]),         
        'pricelist_id': fields.many2one('fashion.form.accessory.pricelist', 
            'Pricelist'),
        'tot_cost': fields.float('Total cost', digits=(10, 4)),
        'color': fields.char('Color', size=20), # TODO eliminare
        #'h': fields.float('H'),
        'h': fields.char('H', size=15),

        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        }
        
    _defaults = {
        'sequence': lambda *x: 1000, # high number so letter are lower
        }

class fashion_form_stitch_rel(osv.osv):
    '''Table that manage the relation stitch/form
    '''
    _name = 'fashion.form.stitch.rel'
    _description = 'Stitches'

    _columns = {
        'sequence': fields.integer('Seq.'),
        'form_id': fields.many2one('fashion.form', 'Form'),
        'stitch_id': fields.many2one('fashion.form.stitch', 'Stitch'),
        'name': fields.char('Name', size = 50),
        'topstitch': fields.char('Topstitching', size = 60),

        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        }

class fashion_form_comment_rel(osv.osv):
    '''Table that manages the comment/form
    '''
    _name = 'fashion.form.comment.rel'
    _description = 'Comments'
    _order = 'date,id'

    # -------------------
    # On change function:
    # -------------------    
    def on_change_upper_comment(self, cr, uid, ids, name, context=None):
        ''' #Manages the capital of the fields in the form Comment
        '''
        res = {'value': {}}
        if name:
            res['value']['name'] = name.upper()
        return res

    def on_change_upper_reference(self, cr, uid, ids, reference, context=None):
        ''' #Manages the capital of the fields in the form Comment
        '''
        res = {'value': {}}
        if reference:
            res['value']['reference'] = reference.upper()
        return res

    _columns = {
         'print_invisible': fields.boolean('Print invisible'),
         'name': fields.text('Changes'),
         'form_id': fields.many2one('fashion.form', 'Form'),
         'date': fields.date('Date'),
         'user_id': fields.many2one('res.users', 'User', 
             help="User that insert comment"),
         'reference': fields.char('Reference', size=50, 
             help="If it is not the user or is an external reference write "
                 "here the name."),
         'hide_in_report':fields.boolean('Hide in report'),        

         # Link di importazione:
         'access_id': fields.integer('Access ID', 
             help="ID Importazione che tiene il link"),
         }

    _defaults = {
        'date': lambda *a: datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT), 
        'user_id': lambda s, cr, uid, ctx: uid
        }

class fashion_measure_rel(osv.osv):
    '''Table that manages the measure/article
    '''
    _name = 'fashion.measure.rel'
    _description = 'Relation'
    _rec_name = 'article_id'

    _columns = {
         'article_id': fields.many2one('fashion.article', 'Article'),
         'measure_id': fields.many2one('fashion.form.measure', 'Measure'),

         # Link di importazione:
         'access_id': fields.integer('Access ID', 
             help="ID Importazione che tiene il link"),
         }

class fashion_article(osv.osv):
    '''
    '''
    _name = 'fashion.article'
    _inherit = 'fashion.article'
    
    _columns = {
        'fashion_measure_ids': fields.one2many(
            'fashion.measure.rel', 'article_id', 'Measure'),
        }
            
class fashion_form_partner_rel(osv.osv):
    ''' Form relation with partner, this object contain much elements useful
        for cost determination and caracteristic of model (ex. fabric)
    '''
    _name = 'fashion.form.partner.rel'
    _description = 'Relation'
    _rec_name = 'partner_id'
    _order = 'model_article,model_number desc,model_customer,model,review desc'
    
    # --------------------
    # Override ORM method:
    # --------------------
    def name_get(self, cr, uid, ids, context = None):
        ''' Add customer-fabric ID to name
        '''
        res = []
        for item in self.browse(cr, uid, ids, context = context):
            res.append((item.id, "%s [%s]" % (
                item.partner_id.name,
                item.fabric_id.code if item.fabric_id else "???")))
        return res
        
    #--------------
    # Button event:
    #--------------
    def wizard_print_a(self, cr, uid, ids, context=None):
        ''' Print directyl report C with totals (instead of wizard)        
        '''
        record_proxy = self.browse(cr, uid, ids, context=context)[0]
        datas = {}
        datas['active_ids'] = [record_proxy.form_id.id]
        datas['active_id'] = record_proxy.form_id.id
        datas['partner_fabric_id'] = ids[0]
        datas['summary'] = True
        datas['image'] = True

        return {
            'model': 'fashion.form',
            'type': 'ir.actions.report.xml',
            'report_name': "fashion_form_A",
            'datas': datas,
            }

    def wizard_print_b(self, cr, uid, ids, context=None):
        ''' Print directyl report C with totals (instead of wizard)        
        '''
        record_proxy = self.browse(cr, uid, ids, context=context)[0]
        datas = {}
        datas['active_ids'] = [record_proxy.form_id.id]
        datas['active_id'] = record_proxy.form_id.id
        datas['partner_fabric_id'] = ids[0]
        datas['total'] = True
        datas['image'] = True
        
        return {
            'model': 'fashion.form',
            'type': 'ir.actions.report.xml',
            'report_name': 'fashion_form_B',
            'datas': datas,
            }

    def wizard_print_b_minus(self, cr, uid, ids, context=None):
        ''' Print directyl report C without totals (instead of wizard)        
        '''
        res = self.wizard_print_b(cr, uid, ids, context=context)
        res['datas']['total'] = False
        res['datas']['from_wizard'] = True
        return res
        
    def wizard_print_c(self, cr, uid, ids, context=None):
        ''' Print directyl report C with totals (instead of wizard)        
        '''
        record_proxy = self.browse(cr, uid, ids, context=context)[0]
        datas = {}
        datas['active_ids'] = [record_proxy.form_id.id]
        datas['active_id'] = record_proxy.form_id.id
        datas['partner_fabric_id'] = ids[0]
        datas['image'] = True
        
        return {
            'model': 'fashion.form',
            'type': 'ir.actions.report.xml',
            'report_name': "fashion_form_C",
            'datas': datas,
            }

    #---------------------
    # On change functions:
    #---------------------
    def on_change_symbol_fabric(self, cr, uid, ids, fabric_id, symbol_fabric, article_code, supplier_id, perc_fabric, context=None):
        ''' Load default wash symbol, maybe in the form are changed
        '''
        res = {'value': {}}
        if not fabric_id: # nothing if no fabric selected or wash symbol jet present
            res['value']['symbol_fabric'] = False
            res['value']['article_code'] = False
            res['value']['supplier_id'] = False
            res['value']['perc_fabric'] = False
            res['value']['cost'] = False
            res['value']['note_fabric'] = False            
            return res

        fabric_proxy = self.pool.get('fashion.form.fabric').browse(
            cr, uid, fabric_id, context=context)
        res['value']['symbol_fabric'] = fabric_proxy.symbol
        res['value']['article_code'] = fabric_proxy.article_code
        res['value']['supplier_id'] = fabric_proxy.supplier_id.id
        res['value']['perc_fabric'] = fabric_proxy.perc_composition
        res['value']['cost'] = fabric_proxy.cost
        res['value']['note_fabric'] = "%s%s %s" % (
            fabric_proxy.supplier_id.name if fabric_proxy.supplier_id else "", 
            " ART %s" % (
                fabric_proxy.article_code) if fabric_proxy.article_code else "", 
            fabric_proxy.note or '')
        return res
        
    def onchange_cost_computation(self, cr, uid, ids, mt_fabric, cost, retail, wholesale, sale, sum_extra_cost, context=None):
        ''' Master event for calculate sale price with all variables
            mt_fabric * cost = cost_tot * (100 + retail) * (100 + wholesale) = sale
        '''
        res = {'value': {}}
        res['value']['total_fabric'] = (mt_fabric or 0.0) * (cost or 0.0)
        res['value']['sale'] = (res['value']['total_fabric'] + sum_extra_cost or 0.0) * (100.0 + (retail or 0.0)) * (100.0 + (wholesale or 0.0)) / 10000.0        
        return res
        
    #def onchange_sale(self, cr, uid, sale, context=None):
    #    ''' Find % of margin for all 
    #    '''    
    #    res = {}
    #    return res

    #------------------
    # Fields functions:
    #------------------
    def _get_total_fabric(self, cr, uid, ids, name, args, context=None):
        ''' Calculate total fabric (cost * mt)
            Total costs (fabric, list, accessory)
            Info for margine and recharge
        '''
        res = {}        
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = {}
            res[obj.id]['total_fabric'] = obj.cost * obj.mt_fabric
            res[obj.id]['total_cost'] = res[obj.id]['total_fabric'] + obj.form_id.sum_extra_cost # TODO + cost list + accessory totale
            profit = obj.sale - res[obj.id]['total_cost']
            res[obj.id]['margin_note'] = _("%5.2f%s(Mar.)\n%5.2f%s(Ric.)\n%10.2f€(Ut.)") % (
                (profit * 100.0 / res[obj.id]['total_cost']) if res[obj.id]['total_cost'] else 0.0,
                "%",
                (profit * 100.0 / obj.sale) if obj.sale else 0.0,
                "%",
                profit,
            )            
        return res
    
    def _store_update_model_customer(self, cr, uid, ids, context=None):
        ''' Recalculate store season in client when change in partner
        '''
        res = []
        rel_pool = self.pool.get('fashion.form.partner.rel')

        # Note: reset all:
        #return rel_pool.search(cr, uid, [], context=context)
        for item_id in ids:
            res.extend(rel_pool.search(cr, uid, [
                ('form_id', '=', item_id)], context=context))
        return res

    # -------------------
    # Field store method:
    # -------------------
    def _change_group_in_partner(self, cr, uid, ids, context=None):
        ''' When change group in partner change in all forms for that partner
        '''
        _logger.warning('Update form for partner group change!')
        return self.pool.get('fashion.form.partner.rel').search(cr, uid, [
            ('partner_id', 'in', ids)], context=context)

    def _change_partner_in_fashion(self, cr, uid, ids, context=None):
        ''' When change partner in form change also group
        '''
        _logger.warning('Update group partner from fashion form!')
        return ids

    _columns = {
        'form_id': fields.many2one('fashion.form', 'Form'),
        'partner_id': fields.many2one('res.partner', 'Partner', 
            domain=[('customer','=',True)], required=True),
        'group_id': fields.related(
            'partner_id', 'group_id', type='many2one', relation='res.partner', 
            string='Partner group', store = {
                'res.partner': (
                    _change_group_in_partner, ['group_id'], 50),
                'fashion.form.partner.rel': (
                    _change_partner_in_fashion, ['partner_id'], 50),
                }),
        'fabric_id': fields.many2one('fashion.form.fabric', 'Fabric', 
            #required=True  # TODO reimportare quando elimimato righe vuote
            ),
        'desc_fabric': fields.char('Description', size=80),
        'perc_fabric': fields.char('Composition', size=40),
        'corr_fabric': fields.char('Additional description', size=80),
        'symbol_fabric': fields.char('Symbols', size=80),
        'note_fabric': fields.text('Fabric note'),
        'note_cost': fields.text('Cost note'),
        'weight': fields.float('Weight', digits=(10, 2)),
        
        'h_fabric': fields.float('H.', digits=(10, 2)),
        'mt_fabric': fields.float('Mt.', digits=(10, 2)),
        
        'cost': fields.float('Cost', digits=(10, 4), 
            help="Unit price for fabric"),
        'retail': fields.float('Retail', digits=(10, 4)),
        'wholesale': fields.float('Wholesale', digits=(10, 4)),
        'sale': fields.float('Selling price', digits=(10, 4)),
        
        # Calculated fields:
        'total_fabric': fields.function(_get_total_fabric, 
            string="Total fabric", 
            type="float", digits=(10, 2), store=False, multi='totals'),  # m_lining * cost
        'total_cost': fields.function(_get_total_fabric, string="Total cost", 
            type="float", digits=(10, 2), store=False, multi='totals'),  # total_fabric + cost list + accessory
        'margin_note': fields.function(_get_total_fabric, string="Balance", 
            type="char", size=100, store=False, multi='totals'),  # margin information

        
        'code': fields.char('Customer Code', size=10),
        'gerber_name': fields.char('Name', size=10),
        'gerber_desc': fields.char('Description', size=10),
        'gerber_h': fields.char('Height', size=10),
        'gerber_l': fields.char('Length', size=10),
                        
        'article_code': fields.char('Article', size=60),
        #'article_description': fields.char('Description', size=60),
        'article_description': fields.related(
            'fabric_id', 'note', type='char', size=100, string='Description', 
            readonly=True), 
        'supplier_id': fields.many2one('res.partner', 'Supplier', 
            domain=[('supplier','=',True)]),

        'perc_reload': fields.float('Reloading percentage', digits=(10, 2)),
        'perc_margin': fields.float('Margin percentage', digits=(10, 2)),
        
        # TODO eliminare appena vengono tolte dalle viste (kanban)
        #'image': fields.related('form_id', 'image', type='binary', string='Image', readonly=True),
        'draw_image_a': fields.related('form_id', 'draw_image_a', 
            type='binary', string='Image', readonly=True),
        #'image_large': fields.related('form_id', 'image_large', type='binary', string='Image', readonly=True),

        'cost_id': fields.many2one('fashion.form.cost', 'Cost'),
        'value': fields.float('Value', digits=(10, 2)),
        'note': fields.text('Note'),
        'article_id': fields.related('form_id', 'article_id', type='many2one',
            relation='fashion.article', string='Article', readonly=True, 
            store=True),

        'season_id': fields.related('form_id','season_id', type='many2one', 
            relation='fashion.season', string='Season', store=True),

        # Store function on related fields (for search):
        'model': fields.related('form_id', 'model', type='char', 
            string='Modello', size=14, 
            store={
                'fashion.form': (
                    _store_update_model_customer, ['model'], 10), }), 
        'model_customer': fields.related('form_id', 'model_customer', 
            type='char', string='Sigla cliente', size=1, 
            store={
                'fashion.form': (
                    _store_update_model_customer, ['model'], 10), }), 
        'model_article': fields.related('form_id', 'model_article', 
            type='char', string='Sigla articolo', size=1, 
            store={
                'fashion.form': (
                    _store_update_model_customer, ['model'], 10), }),
        'model_number': fields.related('form_id', 'model_number', 
            type='integer', string='Numero modello', 
            store={
                'fashion.form': (
                    _store_update_model_customer, ['model'], 10), }),
        'model_revision': fields.related('form_id', 'model_revision', 
            type='char', string='Revisione', size=3, 
            store={
                'fashion.form': (
                    _store_update_model_customer, ['model'], 10), }),
        'review': fields.related('form_id', 'review', type='integer', 
            string='Revisione', 
            store={
                'fashion.form': (
                    _store_update_model_customer, ['model'], 10), }),
        'conformed': fields.related('form_id', 'conformed', type='boolean', 
            string='Conformato', 
            store={
                'fashion.form': (
                    _store_update_model_customer, ['model'], 10), }),
                
        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        'access_2_id': fields.integer('Access 2 ID', 
            help="ID Importazione che tiene il link con partner costi"),
        }

class fashion_form_photo(osv.osv):
    ''' Table that manages the form photo
    '''
    _name = 'fashion.form.photo'
    _description = 'Fashion photo'
    _order = 'create_date,name'
    
    _path = '~/etl/fashion/photo'
    _extension = 'png'

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    def open_form_item(self, cr, uid, ids, context=None):
        ''' Button for open detail in kanban view
        '''
        return {
            'name': _('Photo detail'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fashion.form.photo',
            'res_id': ids[0],
            'view_id': False,
            'views': [(False, 'form')],
            'target': 'new',
            'domain': [('id', '=', ids[0])],
            'context': {},
            'type': 'ir.actions.act_window',
            }                

    # -------------------------------------------------------------------------
    # Function field:
    # -------------------------------------------------------------------------
    def _get_photo_image(self, cr, uid, ids, name, args, context=None):
        ''' Read photo with ID.extension
        '''
        res = {}
        if name.split('_')[-1] == 'medium':
            width = 400
        else:
            width = False # no resize    
              
        path = os.path.expanduser(self._path)        
        for photo in self.browse(cr, uid, ids, context=context):
            # Read original image
            filename = os.path.join(path, '%s.%s' % (
                photo.id, self._extension))
            try:
                f = open(filename, 'rb')
                img = base64.encodestring(f.read())
                f.close()
            except:
                img = False
            if width and img:
                res[photo.id] = tools.image_resize_image(
                    img, size=(width, None), encoding='base64', 
                    filetype=self._extension.upper(), avoid_if_small=True)
            else:                        
                res[photo.id] = img
        return res       

    def _set_photo_image(self, cr, uid, item_id, name, value, args, 
            context=None):
        ''' Write image passed to file
        '''
        path = os.path.expanduser(self._path)        
        filename = os.path.join(path, '%s.%s' % (item_id, self._extension))
        try: # save as a file:
            f = open(filename, 'wb')
            f.write(base64.decodestring(value))
            f.close()
            #try: # Set parameter for update
            #    os.chmod(filename, 0777)
            #    os.chown(filename, -1, 1000)
            #except:
            #    pass # nothing
        except:
            return False
        return True

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'datetime': fields.date('Create date', readonly=True),        
        'user_id': fields.many2one('res.users', 'Create user', 
            readonly=True),
        'note': fields.text('Note'),
        'form_id': fields.many2one('fashion.form', 'Form'),
        'photo': fields.function(_get_photo_image, 
            fnct_inv=_set_photo_image, string='Photo', type='binary'),            
        'photo_medium': fields.function(_get_photo_image, 
            fnct_inv=_set_photo_image, string='Photo', type='binary'),
        }

    _defaults = {
        'datetime': lambda *a: datetime.now().strftime(
            DEFAULT_SERVER_DATE_FORMAT),
        'user_id': lambda s, cr, uid, ctx: uid,
        }
class res_partner(osv.osv):
    ''' Extra fields for partner
    '''
    _inherit = 'res.partner'

    _columns = {
        'start': fields.integer('Start size', 
            help='Departure for the standardized sizes'),
        'group_id': fields.many2one('res.partner', 'Partner group'),    

        # Link di importazione:
        'access_id': fields.integer('Access ID', 
            help="ID Importazione che tiene il link"),
        }
    
class fashion_form_extra_relations(osv.osv):
    '''Table that manage the relation forms
    '''
    _inherit = 'fashion.form'

    _columns = {
        'characteristic_rel_ids': fields.one2many(
            'fashion.form.characteristic.rel', 'form_id', 
            'Characteristic Relation'),
        'cost_rel_ids': fields.one2many('fashion.form.cost.rel', 'form_id', 
            'Cost Relation'),
        'accessory_rel_ids': fields.one2many('fashion.form.accessory.rel', 
            'form_id', 'Accessory Relation'),
        # 'fabric_rel_ids': fields.one2many('fashion.form.fabric.rel', 'form_id', 'Relation'), #TODO
        'stitch_rel_ids': fields.one2many('fashion.form.stitch.rel', 
            'form_id', 'Stitch Relation'),
        'partner_rel_ids': fields.one2many('fashion.form.partner.rel', 
            'form_id', 'Partner Relation'),
        'measure_rel_ids': fields.one2many('fashion.form.measure.rel', 
            'form_id', 'Measure Relation'),
        'comment_rel_ids': fields.one2many('fashion.form.comment.rel', 
            'form_id', 'Comment Relation'),
        'photo_ids': fields.one2many('fashion.form.photo', 'form_id', 'Photo'),
        }

class product_template(osv.osv):
    ''' Remove translation from product name
    '''
    _inherit = 'product.template'
    
    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        }    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
