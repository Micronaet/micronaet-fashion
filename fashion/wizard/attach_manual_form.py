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
import os
import base64
import tempfile
import logging
import shutil
from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime
import pdb

_logger = logging.getLogger(__name__)


class FashionFormAttachment(osv.osv):
    """ Form attachment
    """
    _name = 'fashion.form.attachment'
    _description = 'Collega scheda manuale'
    _store_folder = '~/Store'

    def open_attachment_wizard(self, cr, uid, ids, context=None):
        """ Button from Form
        """
        form_pool = self.pool.get('fashion.form')
        attachment_id = ids[0]
        attachment = self.browse(cr, uid, attachment_id, context=context)
        form_id = attachment.form_id.id

        return form_pool.open_attachment_detailed(
            cr, uid, form_id, attachment_id, context=context)

    def open_file(self, cr, uid, ids, fields, args, context=None):
        """ Fields function for calculate
        """
        attachment = self.browse(cr, uid, ids, context=context)[0]
        origin = attachment.filename
        tmp = tempfile.NamedTemporaryFile()
        extension = origin.split('.')[-1]
        if len(extension) > 6:  # XXX max extension length
            extension = ''
        destination = '%s.%s' % (tmp.name, extension)
        tmp.close()

        # Copy current file in temp destination
        try:
            shutil.copyfile(origin, destination)
        except:
            raise osv.except_osv(
                _('File non trovato'),
                _(u'File non trovato nella gest. documentale!\n%s' % origin),
            )

        name = 'fashion_download.%s' % extension

        # Return link for open temp file:
        return self._get_php_return_page(
            cr, uid, destination, name, context=context)

    def _get_php_return_page(self, cr, uid, fullname, name, context=None):
        """ Generate return object for pased files
        """
        config_pool = self.pool.get('ir.config_parameter')
        key = 'web.base.url.fahsion'
        config_ids = config_pool.search(cr, uid, [
            ('key', '=', key)], context=context)
        if not config_ids:
            raise osv.except_osv(
                _('Errore'),
                _('Avvisare amministratore: configurare parametro: %s' % key),
            )
        config_proxy = config_pool.browse(
            cr, uid, config_ids, context=context)[0]
        base_address = config_proxy.value
        _logger.info('URL parameter: %s' % base_address)

        return {
            'type': 'ir.actions.act_url',
            'url': '%s/save_as.php?filename=%s&name=%s' % (
                base_address,
                fullname,
                name
            ),
            # 'target': 'new',
        }

    def _get_filename(self, cr, uid, ids, fields, args, context=None):
        """ Fields function for calculate
        """
        res = {}
        root = os.path.expanduser(self._store_folder)
        for attachment in self.browse(cr, uid, ids, context=context):
            attach_id = attachment.id
            res[attach_id] = os.path.join(
                root,
                '%s.%s' % (attachment.id, attachment.pdf),
                )
        return res

    _columns = {
        'name': fields.char('Descrizione', size=60),
        'form_id': fields.many2one('fashion.form', 'Scheda'),
        'filename': fields.function(
            _get_filename, method=True,
            type='text', string='Nome file',
            ),
        'extension': fields.char('Estensione', size=5),
    }

    _defaults = {
        'extension': lambda *x: 'pdf'
    }


class FashionForm(osv.osv):
    """ Form form button
    """
    _inherit = 'fashion.form'

    def open_attachment_wizard(self, cr, uid, ids, context=None):
        """ Button from Form
        """
        form_id = ids[0]
        return self.open_attachment_detailed(
            cr, uid, form_id, False, context=context)

    def open_attachment_detailed(
            self, cr, uid, form_id, attachment_id, context=None):
        """ Open wizard wit 2 mode:
        """
        attach_pool = self.pool.get('fashion.form.attachment')
        model_pool = self.pool.get('ir.model.data')
        view_id = model_pool.get_object_reference(
            cr, uid,
            'micronaet-fashion', 'view_fashion_attach_manual_form_form')[1]

        res_id = attach_pool.create(cr, uid, {
            'form_id': form_id,
            'attachment_id': attachment_id,
        }, context=context)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Importa allegati'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': res_id,
            'res_model': 'fashion.form.attachment',
            'view_id': view_id,
            'views': [(False, 'form')],
            'domain': [],
            'context': context,
            'target': 'new',
            'nodestroy': False,
            }

    _columns = {
        'attachment_ids': fields.one2many(
            'fashion.form.attachment', 'form_id', 'Allegati')
    }


class FashionAttachManualFormWizard(osv.osv_memory):
    """ Attach manual form
    """
    _name = 'fashion.attach.manual.form'
    _description = 'Collega scheda manuale'


    def add_attachment(self, cr, uid, ids, context=None):
        """ Add attachement
        """
        attach_pool = self.pool.get('fashion.form.attachment')
        wizard = self.browse(cr, uid, ids, context=context)[0]
        form_id = wizard.form_id.id
        attach_id = wizard.attachment_id.id

        if not attach_id:
            attach_id = attach_pool.create(cr, uid, ids, {
                'name': wizard.name,
                'form_id': form_id,
                }, context=context)
        attach_filename = self.browse(
            cr, uid, attach_id, context=context).filename

        b64_file = base64.decodestring(wizard.file)
        f = open(attach_filename, 'wb')
        f.write(b64_file)
        f.close()
        return True

    _columns = {
         'form_id': fields.many2one('fashion.form', 'Form'),
         'attachment_id': fields.many2one(
             'fashion.form.attachment', 'Allegato'),
         'name': fields.char('Descrizione', size=60),
         'file': fields.binary('File'),
    }

    _defaults = {
        'name': lambda *s: 'Scheda cartacea',
    }

    def print_report(self, cr, uid, ids, context=None):
        """ Print report passing parameter dictionary
        """
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
