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
import os
import sys
import xlsxwriter
import ConfigParser
import excel_export

ExcelWriter = excel_export.excelwriter.ExcelWriter

# -----------------------------------------------------------------------------
# Utility: 
# -----------------------------------------------------------------------------
def clean(value):
    ''' Clean float
    '''
    if not value:
       return ''
    return value.strip()
       

def clean_float(value):
    ''' Clean float
    '''
    if not value:
       return 0.0
       
    value = value.strip()
    value = value.replace(',', '.')
    return float(value)

def mode_sort(fabric):
    mode = 0
    if fabric[0:1].upper() == 'T':
        mode = 1
    elif fabric[0:1].upper() == 'F':
        mode = 2
    elif fabric[0:1].upper() == 'A':
        mode = 3                
    return mode    
    
    
# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('setup.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
path = config.get('parameters', 'folder')
xlsx_file = config.get('parameters', 'output')

details = []
name_db = {}
mrp_db = []

# -----------------------------------------------------------------------------
# 1. os.walk (read all files and generare res records)
# -----------------------------------------------------------------------------
for root, folders, files in os.walk(path):
    for f in files:
        mrp = f[:-4]
        if mrp not in mrp_db:
            mrp_db.append(mrp)
        filename = os.path.join(root, f)
        for line in open(filename, 'r'):
            line = line.strip()
            line = line.split(';')
           
            # Get fields:
            lavoration = clean(line[0])
            product = clean(line[1])
            fabric = clean(line[2])
            unit = clean_float(line[3])
            total = clean_float(line[4])
            description = clean(line[5])
            
            if fabric not in name_db:
                name_db[fabric] = description
            
            mode = mode_sort(fabric)           
            
            # Save record:
            details.append((
                mode, fabric, product, lavoration, unit, total, description))
            
            
    break # XXX read only first folder!

# -----------------------------------------------------------------------------
#                            Excel file:
# -----------------------------------------------------------------------------
# Create WB:
Excel = ExcelWriter(xlsx_file, verbose=True)

# Create WS:
#data_page = 'Stampa'
detail_page = 'Sviluppo'
#Excel.create_worksheet(data_page)
Excel.create_worksheet(detail_page)

# Column setup:
#Excel.column_width(data_page, (
#    5, 
#    5, 
#    10,
#    30, 
#    40
#    ))
Excel.column_width(detail_page, (
    5, 
    20, 
    30,
    10, 
    5,
    5,
    5,
    40,
    40,
    ))

# Create format:
f_title = Excel.get_format('title')
f_header = Excel.get_format('header')
f_text = Excel.get_format('text')
f_number = Excel.get_format('number')

# -----------------------------------------------------------------------------
# 2. Create sheet with detail (generate total database)
# -----------------------------------------------------------------------------
total_db = {}
sum_db = {}

# Header:
row = 0
Excel.write_xls_line(detail_page, row, (
    u'Tipo',
    u'Tessuto',
    u'Prodotto',
    u'Lavorazione',
    u'Unit.',
    u'Q.',
    u'Totale',
    u'Descrizione',
    ), f_header)


for detail in sorted(details):
    row += 1
    
    subtotal = detail[4] * detail[5]
    fabric = detail[1]
    
    if fabric in total_db:
        total_db[fabric] += subtotal
        sum_db[fabric][1] = row # End block
    else:   
        total_db[fabric] = subtotal
        sum_db[fabric] = [row, row] # Start block

    Excel.write_xls_line(detail_page, row, (
        fabric[0:1],
        fabric,
        detail[2],
        detail[3],
        (detail[4], f_number),
        (detail[5], f_number),
        '',#('', f_number), # subtotal
        detail[6],
        ), f_text)
        
    # -------------------------------------------------------------------------
    # Write formula for subtotal:
    # -------------------------------------------------------------------------
    cell_1 = Excel.rowcol_to_cell(row, 4)
    cell_2 = Excel.rowcol_to_cell(row, 5)
    Excel.write_formula(detail_page, row, 6, '=%s*%s' % (
        cell_1, cell_2), f_number, subtotal)

# -----------------------------------------------------------------------------
# 3. Create sheet total 
# -----------------------------------------------------------------------------

# MRP
row += 3
Excel.write_xls_line(detail_page, row, (
    'Elenco lanciati: %s' % (', '.join(mrp_db)),
    ), f_title)

row += 1
Excel.write_xls_line(detail_page, row, (u'Data:', ), f_title)

row += 1
Excel.write_xls_line(detail_page, row, (u'Raggruppamento:', ), f_title)

row += 1
Excel.write_xls_line(detail_page, row, (u'Articolo Tessuto:', ), f_title)

row += 1
Excel.write_xls_line(detail_page, row, (u'Totale Capi:', ), f_title)

# Header:
row += 2
Excel.write_xls_line(detail_page, row, (
    u'Tipo',
    u'Materiale',
    u'Descrizione',
    u'Totale',
    u'UM',
    ), f_header)

for fabric in sorted(total_db, key=lambda x: (mode_sort(x), x)):
    row += 1
    Excel.write_xls_line(detail_page, row, (
        fabric[0],
        fabric,
        name_db[fabric],
        ('', f_number),
        'mt',
        ), f_text)

    # -------------------------------------------------------------------------
    # Write formula for subtotal:
    # -------------------------------------------------------------------------
    from_cell, to_cell = sum_db[fabric]
    cell_1 = Excel.rowcol_to_cell(from_cell, 6)
    cell_2 = Excel.rowcol_to_cell(to_cell, 6)
    formula = "=SUM(%s:%s)" % (
        cell_1, 
        cell_2,
        )
        
    Excel.write_formula(detail_page, row, 3, formula, f_number, total_db[fabric])

Excel.close_workbook()

# Open Excel file
#try:
#    os.system('start \'%s\'' % xlsx_file)
#except:
#    print 'Error launching Excel file'    
