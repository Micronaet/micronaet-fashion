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
# Read configuration parameter:
# -----------------------------------------------------------------------------
def write_subtotal(Excel, page, row, old, f_total, f_empty):
    ''' Write total for model
    '''
    # Merce cell:
    Excel.merge_cell(page, [row, 0, row, 1])
    Excel.merge_cell(page, [row, 2, row, 3])
    Excel.merge_cell(page, [row, 5, row, 12])

    Excel.write_xls_line(page, row, (
        ('', f_empty), 
        ('', f_empty), 
        'Totale modello: %s' % old[1], '', old[2],
        ('', f_empty), 
        ('', f_empty), 
        ('', f_empty), 
        ('', f_empty), 
        ('', f_empty), 
        ('', f_empty), 
        ('', f_empty), 
        ('', f_empty), 
        ), f_total)
    return 

def write_total(Excel, page, row, old, f_current):
    ''' Write total for supplier
    '''
    total_model = len(old[4])        
    
    # Set height:
    Excel.row_height(page, [row], height=35)

    # Merce cell:
    Excel.merge_cell(page, [row, 0, row, 1])
    Excel.merge_cell(page, [row, 2, row, 3])
    Excel.merge_cell(page, [row, 5, row, 12])

    Excel.write_xls_line(page, row, (
        'TOTALE: %s' % old[0], 
        '', 
        '%s Modell%s' % (total_model, 'o' if total_model == 1 else 'i'), 
        '', old[3],
        ' '.join(old[4]),
        '', '', '', '', '', '', '',
        ), f_current)
    return     
        
def clean(value):
    res = ''
    if not value:
        return res
    for c in value:
        if ord(c) <= 127:
            res += c
        else:
            res += '?'
    return res

def split_block(block, line):
    ''' Split block depend on report part
    '''
    if block == 1:
        if line.startswith('Modello'):
            return (
                line[:8].strip(), # Order
                line[8:19].strip(), # Parent code
                '',
                int(line[48:60].lstrip('.').replace('.', '')), # Total
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                )
        else:
            return [
                line[:8].strip(), # Order
                line[8:33].strip(), # Product code
                line[33:48].strip(), # Product description
                int(line[48:61].strip()), # Qty
                line[61:71].strip(), # Customer code
                line[71:110].strip(), # Customer name
                # separator: |
                line[111:118].strip(), # Note
                line[118:122].strip(), # Phase
                line[122:129].strip(), # DL
                line[129:138].strip(), # Data
                line[138:148].strip(), # Supplier code
                line[148:188].strip(), # Supplier description
                ]
    elif block == 3:
        return (
            line[:7].strip(), # Code
            line[7:18].strip(), # Description
            line[19:108].strip(), # Models
            line[108:110].strip(), # Tot model
            line[111:119].strip(), # Tot PCE
            )

    elif block == 4:
        return (
            line[:15].strip(), # Model
            line[15:20].strip(), # Qty
            )
    elif block == 5:
        return (
            line[:10].strip(), # Code
            line[10:31].strip(), # Supplier
            line[31:216].strip(), # Model
            line[216:230].strip(), # Total
            )

def clean4sheet(supplier):
    ''' Remove char non valid for sheet name
    ''' 
    page = supplier           
    invalid = '[]:*?/\\'
    for char in invalid:
        page = page.replace(char, '')
    return page    
                
cfg_file = os.path.expanduser('./setup.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
csv_file = config.get('parameters', 'input')
xlsx_file = config.get('parameters', 'output')

# Line start with:
start_text = {
    'page_jump': 'DESCO S.R.L.         ',
    'dashline': '-' * 100 ,# almost 100
    'b3': 'Totale suddiviso per capi',
    'b4': 'Modelli per cliente',
    'b5': 'Lavorante       ',
    'end': 'ultima pagina',
    'mode': 'Dettaglio capi in ordine con riga L', # Check lauch mode (suppl)
    }

# Report name:
name = {
    1: 'Dettaglio capi in ordine con riga L Art. in lavorazione',
    2: 'Dettaglio capi in ordine con riga L Art. in lavorazione (fornitore)',
    3: 'Totale suddiviso per capi',
    4: 'Modelli per cliente',
    5: 'Modelli in lavorazione dal terzista',
    }    

# -----------------------------------------------------------------------------
# 1. os.walk (read all files and generare res records)
# -----------------------------------------------------------------------------
block = 0
blocks = {
    'title': [],
    1: [False, [], False], # 1. Detail data report: (header, data, total)
    2: [], # 2. Detail data (same as 1 but without total)
    3: [False, []],
    4: [False, []],
    5: [False, []],
    }
    
supplier_pages = False # No one page for supplier
jump = i = 0
for line in open(csv_file, 'r'):
    i += 1
    line = clean(line.rstrip())

    # -------------------------------------------------------------------------
    # Check launch mode: if L >> One page for supplier
    # -------------------------------------------------------------------------
    if line.startswith(start_text['mode']):
        supplier_pages = {}
        
    # -------------------------------------------------------------------------
    # Jump empty line and dash line:
    # -------------------------------------------------------------------------
    if not line or line.startswith(start_text['dashline']):
        print '%s. [%s] Jump empty or --- line' % (i, block)
        continue # jump empty line

    if line.startswith(start_text['end']): # End of loop
        print '%s. [%s] End line' % (i, block)
        break     

    # -------------------------------------------------------------------------
    # Jump page repeat header line:
    # -------------------------------------------------------------------------
    if jump > 0: 
        jump -= 1
        print '%s. [%s] Page header' % (i, block)
        continue

    # -------------------------------------------------------------------------
    # [Block 0] Read title block once:
    # -------------------------------------------------------------------------
    if block == 0: # Title line:
        if line.startswith('Ordine  '): # Start block 1
            block = 1
            blocks[block][0] = line
            print '%s. [%s] Start block (column line)' % (i, block)
            continue
        blocks['title'].append(line)
        print '%s. [%s] Read page header' % (i, block)

    # -------------------------------------------------------------------------
    # [Block 1] Read details line:
    # -------------------------------------------------------------------------
    elif block == 1:
        if line.startswith(start_text['page_jump']):
            jump = 3 # Jump next 3 line
            print '%s. [%s] Page header' % (i, block)
            continue
        #elif line.startswith('Ordine  '): # Start block 1
        #    print '%s. [%s] Jump column line' % (i, block)
        #    continue            
        elif line.startswith('Totale   '):
            blocks[block][2] = line # Last total block 1
            block = 3 # End this block, next is 3!
            print '%s. [%s] Read "Totale" End this block' % (i, block)
            continue
        else:    
            line_part = split_block(block, line)
            blocks[block][1].append(line_part)
            print '%s. [%s] Data line' % (i, block), # Leave , (add block 2)
        
        # ---------------------------------------------------------------------
        # [Block 2]: Detail line without total:
        # ---------------------------------------------------------------------
        if not line.startswith('Modello'):
            blocks[2].append(line_part)
            print ' [2] Data line'
        else:    
            print ' [2] Not Data line'

    # -------------------------------------------------------------------------
    # [Block 3] Tot for elements
    # -------------------------------------------------------------------------
    elif block == 3:
        if line.startswith(start_text['page_jump']):
            jump = 3 # Jump next 3 line
            print '%s. [%s] Page header' % (i, block)
            continue
        elif line.startswith(start_text['b3']): # Title line
            blocks[block][0] = line # Title
            print '%s. [%s] Start block (header line)' % (i, block)
            continue
        elif line.startswith(start_text['b4']): # End block
            block = 4
            blocks[block][0] = line            
            print '%s. [%s] Start block (header line)' % (i, block)
            continue
        else:
            line_part = split_block(block, line)
            if any(line_part):
                blocks[block][1].append(line_part)
                print '%s. [%s] Data line' % (i, block)
            else:    
                print '%s. [%s] Empty Data line' % (i, block)
            
    # -------------------------------------------------------------------------
    # [Block 4] Models for customer:
    # -------------------------------------------------------------------------
    elif block == 4:
        if line.startswith(start_text['page_jump']):
            jump = 3 # Jump next 3 line
            print '%s. [%s] Page header' % (i, block)
            continue
        elif line.startswith(start_text['b5']): # End block
            block = 5
            blocks[block][0] = line            
            print '%s. [%s] Start block (header line)' % (i, block)
            continue
        else:    
            blocks[block][1].append(line)
            print '%s. [%s] Data line' % (i, block)
            
    # -------------------------------------------------------------------------
    # [Block 5] Supplier models
    # -------------------------------------------------------------------------
    elif block == 5:
        if line.startswith(start_text['page_jump']):
            jump = 3 # Jump next 3 line
            print '%s. [%s] Page header' % (i, block)
            continue
        else:    
            blocks[block][1].append(line)
            print '%s. [%s] Data line' % (i, block)

print 'Report mode one page x supplier: %s' % (
    'NO' if supplier_pages == False else 'YES',
    )
                    
# -----------------------------------------------------------------------------
#                                  EXCEL FILES: 
# -----------------------------------------------------------------------------
Excel = ExcelWriter(xlsx_file, verbose=True)
print 'Start Excel file: %s' % xlsx_file

# --------------
# Create format:
# --------------
f_title = Excel.get_format('title')
f_header = Excel.get_format('header')
f_text = Excel.get_format('text')
f_bold = Excel.get_format('bold_blue')
f_bold_dark = Excel.get_format('bold_dark_blue')
f_bold_white = Excel.get_format('bold_wrap')
f_bold_empty = Excel.get_format('bold')
f_number = Excel.get_format('number')

# -----------------------------------------------------------------------------
#                                BLOCK 1: Details:
# -----------------------------------------------------------------------------
block = 1
page = 'Dettagli'
Excel.create_worksheet(page)
block1_header = [
    'Ordine', 
    'Cod. Art.', 
    'Desc. Art.', 
    'Capi', 
    'Cod. Cliente', 
    'Desc. cliente', 
    'Note',
    'Fase',
    'N. DL', 
    'Data uscita',
    'Codice terz.',
    'Descrizione terz.',    
    ]
block1a_header = block1_header[:10] + ['Consegna'] + block1_header[10:]

block1_width = [
    7, 
    20, 
    25, 
    8, 
    10, 
    26, 
    6, 
    6, 
    7, 
    11, 
    11, 
    45,
    ]
block1a_width = block1_width[:10] + [15] + block1_width[10:]
Excel.column_width(page, block1_width)


# Title:
row = 0
Excel.write_xls_line(page, row, (
    name[block], 
    ), f_title)

# Header:
row += 2
Excel.write_xls_line(page, row, block1_header, f_header)

# Details:   
for line in blocks[block][1]:
    row += 1
    if line[0] == 'Modello':
        f_select = f_bold
    else:
        f_select = f_text
    Excel.write_xls_line(page, row, line, f_select)

# End total:
row += 1
total = blocks[block][2].replace('|', '').split()[-1]
Excel.write_xls_line(page, row, ('Totale', '', '', total), f_bold)

# -----------------------------------------------------------------------------
#                                BLOCK 2: Details:
# -----------------------------------------------------------------------------
block = 2
page = 'Dettaglio fornitori'
Excel.create_worksheet(page)
Excel.column_width(page, [block1a_width[-1]] + block1a_width[:-1])

# Title:
row = 0
Excel.write_xls_line(page, row, (
    name[block], 
    ), f_title)

# Header:
row += 2
old = [
    False, # Supplier
    False, # Product code
    0, # Subtotal (parent code 7)
    0, # Total supplier
    [], # Model list
    ]

header_block_2 = [block1a_header[-1]] + block1a_header[:-1]
Excel.write_xls_line(page, row, header_block_2, f_header)

# Details:  
for line in sorted(blocks[block], key=lambda x: (x[11], x[1], x[0])):
    row += 1
    line = [line[-1]] + line[:-1] # New format
    
    # Fields:
    supplier = line[0] # supplier name
    model = line[2][:7] # product code
    qty = line[4] # product

    # -------------------------------------------------------------------------
    # Supplier page collect data (HEADER PART):
    # -------------------------------------------------------------------------
    if supplier_pages != False:
        if supplier not in supplier_pages:
            supplier_pages[supplier] = []
            
            # Setup first part of page:
            supplier_pages[supplier].append(
                ('W', [block1_width[-1]] + block1_width[:-1]))
            # Name of report:    
            supplier_pages[supplier].append( 
                ('N', (name[block], ), f_title))
            # Header:    
            supplier_pages[supplier].append(
                ('H', header_block_2, f_header))
                
                
    # Startup:
    if old[0] == False:
        old[0] = supplier
        old[1] = model
    
    # -------------------------------------------------------------------------
    # A. Break level product code:
    # -------------------------------------------------------------------------
    if model != old[1] or supplier != old[0]: # Change product or supplier 
        write_subtotal(Excel, page, row, old, f_bold, f_bold_empty)
        row += 1
        
        # ---------------------------------------------------------------------
        # Supplier page block (SUBTOTAL):
        # ---------------------------------------------------------------------
        if supplier_pages: # Copy list to print as total:
            supplier_pages[old[0]].append(
                ('S', old[:], f_bold, f_bold_empty))
        
        # Old this
        old[1] = model # New model
        old[2] = 0 # Reset total for model

    # Total product for model:
    old[2] += qty 
       
    # -------------------------------------------------------------------------
    # B. Break level partner:
    # -------------------------------------------------------------------------
    if supplier != old[0]:
        write_total(Excel, page, row, old, f_bold_white)
        
        # ---------------------------------------------------------------------
        # Supplier page block (TOTAL):
        # ---------------------------------------------------------------------
        if supplier_pages: # Copy list to print as total:
            supplier_pages[old[0]].append(
                ('T', old[:], f_bold_white))
        
        # ---------------------------------------------------------------------
        # Rewrite header line:
        # ---------------------------------------------------------------------
        row += 1
        Excel.merge_cell(page, [row, 0, row, 11])        
        row += 1 
        Excel.write_xls_line(page, row, header_block_2, f_header)
        row += 1
        
        # Old this
        old[0] = supplier # New supplier
        old[2] = qty # Reset total model with this qty
        old[3] = 0 # Reset supplier total (will be updated after)
        old[4] = [] # Reset model list

    old[3] += qty

    if model not in old[4]:
        old[4].append(model)

    # -------------------------------------------------------------------------
    # C. Data row:    
    # -------------------------------------------------------------------------
    # Add extra empty column:
    line = list(line)
    this_line = line[:11] + [''] + line[11:]
    Excel.write_xls_line(page, row, this_line, f_text)

    # -------------------------------------------------------------------------
    # Supplier page (DETAIL):
    # -------------------------------------------------------------------------
    if supplier_pages:
        supplier_pages[supplier].append(
            ('D', this_line, f_text))

if supplier_pages:
    supplier_pages[old[0]].append(('S', old[:], f_bold, f_bold_empty))
    supplier_pages[old[0]].append(('T', old[:], f_bold_white))
        
# Write last total block:
if blocks[block]: # if block list was present:
    row += 1
    write_subtotal(Excel, page, row, old, f_bold, f_bold_empty)

    row += 1
    write_total(Excel, page, row, old, f_bold_white)

# -----------------------------------------------------------------------------
#                                BLOCK 3: Model list
# -----------------------------------------------------------------------------
block = 3
page = 'Elenco capi'
Excel.create_worksheet(page)
Excel.column_width(page, (5, 12, 80, 8, 10))

# Title:
row = 0
Excel.write_xls_line(page, row, (
    name[block], 
    ), f_title)

# Header:
row += 2
Excel.write_xls_line(page, row, (
    'Sigla', 
    'Tipo', 
    'Codici',     
    'Tot. mod.',
    'Tot. pezzi',
    ), f_header)

# Details:   
total = ['Totale', 0.0, 0.0]
for line in blocks[block][1]:
    row += 1
    Excel.write_xls_line(page, row, line, f_text)
    total[1] += int(line[3].replace('.', '') or '0')
    total[2] += int(line[4].replace('.', '') or '0')

# Write last total block:
row += 1
Excel.write_xls_line(page, row, total, col=2, default_format=f_bold_white)

# -----------------------------------------------------------------------------
#                                BLOCK 4: Customer details:
# -----------------------------------------------------------------------------
block = 4
page = 'Dettaglio cliente'
Excel.create_worksheet(page)
Excel.column_width(page, (15, 10, ))

# Title:
row = 0
Excel.write_xls_line(page, row, (
    name[block], 
    ), f_title)

# Details:   
state = False
for line in blocks[block][1]:
    # -------------------------------------------------------------------------
    # New block (next write partner and header):
    # -------------------------------------------------------------------------
    if line.startswith('-----------------'):
        state = 'partner'

    # -------------------------------------------------------------------------
    # Jump header:
    # -------------------------------------------------------------------------
    elif state == 'jump':#line.startswith('Totale in lavorazione'):
        state = 'data'

    # -------------------------------------------------------------------------
    # Write total:
    # -------------------------------------------------------------------------
    elif state == 'header':#line.startswith('Totale     '):
        row += 1        
        line_part = split_block(block, line)
        Excel.write_xls_line(page, row, line_part, f_text)
        state = 'data'
    
    # -------------------------------------------------------------------------
    # Write partner and header:
    # -------------------------------------------------------------------------
    elif state == 'partner':
        # Partner name:
        row += 2        
        Excel.write_xls_line(page, row, (
            line,
            ), f_title)
            
         # Header:
        row += 1
        Excel.write_xls_line(page, row, (
            'Modello', 
            'Tot. lavoraz.',
            ), f_header)
        state = 'jump'    
            
    # -------------------------------------------------------------------------
    # Data row:
    # -------------------------------------------------------------------------
    else: # state = 'data'
        row += 1        
        line_part = split_block(block, line)
        if line_part[0] == 'Totale':
            f_select = f_bold
        else:
            f_select = f_text
        Excel.write_xls_line(page, row, line_part, f_select)
                

# -----------------------------------------------------------------------------
#                                BLOCK 5: Model list
# -----------------------------------------------------------------------------
if supplier_pages:
    for supplier in sorted(supplier_pages):
        page = clean4sheet(supplier)
        
        Excel.create_worksheet(page)
        row = 0
        for record in supplier_pages[supplier]:
            # Force col witdh:
            if record[0] == 'W':
                Excel.column_width(page, record[1])
                continue
                
            # Title:
            if record[0] == 'N':
                Excel.write_xls_line(page, row, record[1], record[2])
                row += 1 # Extra row
            # Header:
            elif record[0] == 'H':
                Excel.write_xls_line(page, row, record[1], record[2])
            # Details:   
            elif record[0] == 'D':
                Excel.write_xls_line(page, row, record[1], record[2])
            elif record[0] == 'S':
                write_subtotal(
                    Excel, page, row, record[1], record[2], record[3])
            elif record[0] == 'T':
                write_total(Excel, page, row, record[1], record[2])
            row += 1

# -----------------------------------------------------------------------------
#                                BLOCK 6: Customer details:
# -----------------------------------------------------------------------------
'''
block = 6
page = 'Modelli da fornitore'
Excel.create_worksheet(page)
Excel.column_width(page, (10, 18, 160, 10))

# Title:
row = 0
Excel.write_xls_line(page, row, (
    name[block], 
    ), f_title)

# Header:
row += 2
Excel.write_xls_line(page, row, (
    'Codice', 
    'Terzista', 
    'Modelli in lavorazione',     
    'Tot. modelli',
    ), f_header)

# Details:   
for line in blocks[block][1]:
    row += 1
    
    line_part = split_block(block, line)
    Excel.write_xls_line(page, row, line_part, f_text)
'''
Excel.close_workbook()
