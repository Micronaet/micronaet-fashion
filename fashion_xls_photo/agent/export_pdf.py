# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import sys
import os
import xmlrpclib
import base64
import ConfigParser

# -----------------------------------------------------------------------------
#                                Parameters
# -----------------------------------------------------------------------------
# Config file:
cfg_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "openerp.cfg", )
    
config = ConfigParser.ConfigParser()
config.read([cfg_file])

# Read parameters:
server = config.get('openerp', 'server')
port = config.get('openerp', 'port')
dbname = config.get('openerp', 'dbname')
user = config.get('openerp', 'user')
pwd = config.get('openerp', 'pwd')

csv_file = config.get('mexal', 'csv_file')
pdf_file = config.get('mexal', 'pdf_file')

# -----------------------------------------------------------------------------
# XMLRPC connection for autentication (UID) and proxy 
# -----------------------------------------------------------------------------
sock = xmlrpclib.ServerProxy(
    'http://%s:%s/xmlrpc/common' % (server, port), allow_none=True)
uid = sock.login(dbname, user, pwd)
sock = xmlrpclib.ServerProxy(
    'http://%s:%s/xmlrpc/object' % (server, port), allow_none=True)

# -----------------------------------------------------------------------------
# Read file CSV:
# -----------------------------------------------------------------------------
csv_f = open(csv_file, 'r')
i = 0
code_list = []
for row in csv_f:
    i += 1
    if i <= 4: # Start article line
        continue
    row = row.split(';')
    model = row[1]
    if not model:
        break
    model = model[:7].replace('-', '')
    code_list.append(model)
                
binary_data = sock.execute(
    dbname, uid, pwd, 'fashion.form', 
    'generate_report_xls_photo_pdf', code_list,
    )

# -----------------------------------------------------------------------------
# Write PDF file:    
# -----------------------------------------------------------------------------
if binary_data:
    pdf_f = open(pdf_file, 'wb')
    pdf_f.write(binary_data.data)
    pdf_f.close()
