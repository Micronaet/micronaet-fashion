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


class fashion_duplication(osv.osv_memory):
    '''Table that manages the duplication
    '''
    _name = 'fashion.duplication'
    _description = 'Duplication'

    def _get_error(self, cr, uid, context=None):
        ''' 
        '''
        if context is None:
            context = {}

        res = False
        form_id = context.get('active_id')
        if form_id:
            form_proxy = self.pool.get('fashion.form').browse(cr, uid, form_id, context=context)            
            if form_proxy.old_model: # test only old models
                start = int(form_proxy.start or '0')
                size_base = int(form_proxy.size_base or '0')
                if not start: # default start  # TODO testare meglio l'errore se manca start
                    start = 40
                col_ref = 1 + (size_base - start) / 2
                if col_ref != form_proxy.col_ref:
                    res = "Non conforme la gestione colonne:\nColonna base: %s\nColonna di partenza: %s\nColonna di riferimento: %s\nValore corretto %s (reimpostarlo e poi duplicare)\n" % (
                        size_base,
                        start,
                        form_proxy.col_ref,
                        col_ref,
                    )
        return res
        
    _columns = {
         'duplication': fields.selection([
             ('version', 'New Revision'),
             ('form', 'New Form'),
         ], 'Duplication', select=True),
         'code': fields.char('New code', size=10),
         'error': fields.text('Error'),
    }

    _defaults = {
         'duplication': lambda *a: 'version',
         'error': lambda s, cr, uid, ctx: s._get_error(cr, uid, ctx),
    }

    def duplication (self, cr, uid, ids, context=None):
        ''' Button event for duplication
        '''
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
        form_pool = self.pool.get('fashion.form')
        product_pool = self.pool.get('product.product')
        form_proxy = form_pool.browse(cr, uid, context.get('active_id', 0), context=context) #TODO comunicare errore nel caso non ci sia active_id
        if wiz_proxy.duplication == 'version':
            model = form_proxy.model
        else:
            model = wiz_proxy.code

        cr.execute("SELECT max(review) FROM fashion_form WHERE model='%s'" % (model, ))
        max_value = (cr.fetchone()[0] or 0)
        if not max_value and wiz_proxy.duplication == 'form':
            review = 0 
        else:
            review = max_value + 1
        original = '%s.%s' % (form_proxy.model,form_proxy.review)
        data = {'name': form_proxy.name, }
        product_id = product_pool.create(cr, uid, data, context=context)
        col_split = 0
        if form_proxy.col_ref != 3:
            try:
                col_split = 3 - form_proxy.col_ref
                #size_base = int(form_proxy.size_base) + (3 - form_proxy.col_ref) * 2
            except:
                # TODO segnalare errore
                pass
        #else:
        #size_base = form_proxy.size_base
            
        data = {
             'model': model,
             # extra model elements calculated during create / write
             'size_base': form_proxy.size_base,
             'size_measure': form_proxy.size_measure,
             'review': review,
             'date': datetime.now().strftime('%Y-%m-%d'),
             'original': form_proxy.original,
             'base_id': form_proxy.id,
             'base_name': form_proxy.name,
             'h_lining': form_proxy.h_lining,
             'mt_lining': form_proxy.mt_lining,
             'cost_lining': form_proxy.cost_lining,
             'conformed': form_proxy.conformed,
             'start': form_proxy.start,
             'ironing': form_proxy.ironing,
             'area': form_proxy.area,
             'user_id': uid,
             'cut': form_proxy.cut,
             'size': form_proxy.size,
             'colors': form_proxy.colors,
             'article_id': form_proxy.article_id.id,
             'season_id': form_proxy.season_id.id,
             'draw_image_a': form_proxy.draw_image_a,
             'draw_image_b': form_proxy.draw_image_b,
             'draw_image_c': form_proxy.draw_image_c,
             'draw_image_d': form_proxy.draw_image_d,
             'product_id': product_id,
             'state': 'draft',
             'col_ref': 3,
             
             'old_model': False, # New duplication became new model, problem: col_ref not 2
             }             
        form_id = form_pool.create(cr, uid, data, context=context)
        
        # one2many fields:
        # Partner - Fabric:
        for item in form_proxy.partner_rel_ids:
            self.pool.get('fashion.form.partner.rel').create(cr, uid, {
                'code': item.code,
                'partner_id': item.partner_id.id or False,
                'season_id': item.season_id.id or False,
                'fabric_id': item.fabric_id.id or False,
                'symbol_fabric': item.symbol_fabric,
                'desc_fabric': item.desc_fabric,
                'perc_fabric': item.perc_fabric,
                'corr_fabric': item.corr_fabric,
                'weight': item.weight,
                #'mt_fabric': item.mt_fabric,
                #'h_fabric': item.h_fabric,
                'wholesale': item.wholesale,
                'note_fabric': item.note_fabric,
                'cost': item.cost,
                'gerber_name': item.gerber_name,
                'gerber_l': item.gerber_l,
                'gerber_h': item.gerber_h,
                'gerber_desc': item.gerber_desc,
                'perc_reload': item.perc_reload,
                'perc_margin': item.perc_margin,
                'sale': item.sale,
                'supplier_id': item.supplier_id.id,
                'article_code': item.article_code,
                'article_description': item.article_description,

                'form_id': form_id,

                #'detail': item.detail,
                #'department_store': item.department_store,
                #'h_lining': item.h_lining,
                #'mt_lining': item.mt_lining,
                #'cost_tot': item.cost_tot,
                #'fabric_tot': item.fabric_tot,
                #'lining_tot': item.lining_tot,
                #'tot_cost': item.tot_cost,                
            }, context=context)

        # Characteristic:
        for item in form_proxy.characteristic_rel_ids:
            self.pool.get('fashion.form.characteristic.rel').create(cr, uid, {
                'name': item.name,
                'characteristic_id': item.characteristic_id.id or False,
                'lenght': item.lenght,
                'stitch_type_id': item.stitch_type_id.id if item.stitch_type_id else False,
                'stitch_cut_id': item.stitch_cut_id.id if item.stitch_cut_id else False,
                'stitch_top_id': item.stitch_top_id.id if item.stitch_top_id else False,
                'bindello': item.bindello,
                'form_id': form_id,                
            }, context=context)

        # Stitch (only for old models):
        if form_proxy.old_model: # only if parent is an old model:
            # Copy all stich in characteristic elements (fashion.form.stitch.rel):
            for item in form_proxy.stitch_rel_ids:
                characteristic_id = False
                if item.stitch_id:
                    characteristic_pool = self.pool.get('fashion.form.characteristic')
                    characteristic_ids = characteristic_pool.search(cr, uid, [('name', '=', item.stitch_id.name)], context=context)
                    if characteristic_ids:
                        characteristic_id = characteristic_ids[0]
                    else:
                        characteristic_id = characteristic_pool.create(cr, uid, {'name': item.stitch_id.name}, context=context)   
                name = "%s%s" % (item.name, "(IMPUNTURE: %s)" % item.topstitch if item.topstitch else "")
                self.pool.get('fashion.form.characteristic.rel').create(cr, uid, {
                    'name': name.upper(),
                    'characteristic_id': characteristic_id,
                    'form_id': form_id,
                }, context=context)

        # Accessory:
        for item in form_proxy.accessory_rel_ids:
            # Reload price if pricelist/fabric present:
            if item.fabric_id:
                fabric_id = item.fabric_id.id
                pricelist_id = False
                currency = item.fabric_id.cost # unit price
                tot_cost = currency * item.quantity
                    
            elif item.pricelist_id:
                fabric_id = False
                pricelist_id = item.pricelist_id.id
                currency = item.pricelist_id.cost # unit price
                tot_cost = currency * item.quantity
                
            else:
                fabric_id = False
                pricelist_id = False
                currency = item.currency
                tot_cost = item.tot_cost
                    
            unit_price = item.pricelist_id.cost
            self.pool.get('fashion.form.accessory.rel').create(cr, uid, {
                'name': item.name,
                'accessory_id': item.accessory_id.id if item.accessory_id else False,
                'sequence': item.sequence,
                'code': item.code,
                'extra': item.extra,
                'fabric_id': fabric_id,
                'pricelist_id': pricelist_id,
                'supplier_id': item.supplier_id.id if item.supplier_id else False,
                'um': item.um,
                'quantity': item.quantity,
                'currency': currency,
                'tot_cost': tot_cost,
                'color': item.color,
                'tone': item.tone,
                'note': item.note,
                'gerber_name': item.gerber_name,
                'gerber_desc': item.gerber_desc,
                'gerber_h': item.gerber_h,
                'gerber_l': item.gerber_l,
                'form_id': form_id,
                'h': item.h,
            }, context=context)

        # Measure:
        base_column = int(form_proxy.col_ref)
        for item in form_proxy.measure_rel_ids:
            if item.header:
                continue
                
            data_measure = {
                'header': item.header,
                'name': item.name,
                'measure_id': item.measure_id.id or False,
                'size_3': item.__getattr__('size_%s' % (3 - col_split)),
                'visible': item.visible,
                #'real': item.real,
                'form_id': form_id,
            }
            if wiz_proxy.duplication == 'version':
                for i in (1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13): # all column except 3 (13 is hide for now)
                    if i - col_split >= 1 and i - col_split <= 13:
                        data_measure['size_%s' % (i)] = item.__getattr__('size_%s' % (i - col_split))

            self.pool.get('fashion.form.measure.rel').create(cr, uid, data_measure, context=context)

        # header line
        if form_id:
            form_pool.create_update_header(cr, uid, [form_id], context=context)
        
        # Comment:        
        if wiz_proxy.duplication == 'version': # comment only for version dup.
            for item in form_proxy.comment_rel_ids:
                self.pool.get('fashion.form.comment.rel').create(cr, uid, {
                    'name': item.name,
                    'reference': item.reference,
                    'user_id': item.user_id.id or False,
                    'date': item.date,
                    'form_id': form_id,
                }, context=context)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fashion.form', # object linked to the view
            'domain': [('id', '=', form_id)],
            'type': 'ir.actions.act_window',
            'res_id': form_id,  # IDs selected
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
