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
import pdb
import excel_export

from datetime import datetime
try:
    import ConfigParser
except:
    import configparser as ConfigParser

ExcelWriter = excel_export.excelwriter.ExcelWriter


# -----------------------------------------------------------------------------
# Utility:
# -----------------------------------------------------------------------------
# Utility dict:
category_setup = (
    # 3 start (before)
    ('ADE', 'Adesivo'),  # Start, Category, order
    ('PAN', 'Panamino'),
    # ('ELA', 'Elastico'),
    # ('FIL', 'Filo'),
    # ('GAN', 'Gancio'),

    # 1 start
    ('T', 'Tessuto'),
    ('FOD', 'Fodera'),
    # ('L', 'Lampo'),
)

sort_category = {
    'Tessuto': 1,
    'Adesivo': 2,
    'Fodera': 3,
    'Panamino': 4,
    # 'Lampo': 3,
    # 'Filo': 5,
    # 'Elastico': 6,
    # 'Gancio': 7,
    }


# Function:
def clean(value):
    """ Clean text
    """
    if not value:
        return ''
    return value.strip()


def clean_float(value):
    """ Clean float
    """
    if not value:
        return 0.0
    value = value.strip()
    value = value.replace(',', '.')
    return float(value)


def get_category(default_code):
    """ Function that analyse and manage:
        1. If code need to be used
        2. Extract category from code
        3. Extract order position in report list
    """
    default_code = default_code.upper()
    for start, category in category_setup:
        if default_code.startswith(start):
            return category
    return False   # Excluded


# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('./config/excel.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])

# In file:
file_job = os.path.expanduser(config.get('parameters', 'file_job'))
file_product = os.path.expanduser(config.get('parameters', 'file_product'))
# Out file:
xlsx_file = os.path.expanduser(config.get('parameters', 'file_xlsx'))

# -----------------------------------------------------------------------------
# Report master data:
# -----------------------------------------------------------------------------
file_data = {
    # Header detail:
    'date': datetime.now().strftime('%d/%m/%Y'),
    'mrp_name': '',  # Product MRP name
    'fodera_material': '',
    'fabric_material': '',
    'jobs': [],  # Total Job touched

    # Master detail used
    'master': {},  # Master data for job list
    'master_component': {},  # Master data for component linked
    'compact_component': {},  # List of component

    'total': 0,  # Total pz.
    'range_tg': [100, 0],  # Tg range position

    # Extra detail used:
    'components': {},  # Job - Line: components list
    }

# -----------------------------------------------------------------------------
#                          Load components from file:
# -----------------------------------------------------------------------------
for line in open(file_product, 'r'):
    part = line.split(';')
    job = clean(part[0])
    row = clean(part[1])
    default_code = clean(part[2])
    name = clean(part[3])
    quantity = clean_float(part[4])
    material = clean(part[5])

    key = job, row
    if key not in file_data['components']:
        file_data['components'][key] = {}

    category = get_category(default_code)
    if not category:
        # component not used
        continue
    if category not in file_data['components'][key]:
        file_data['components'][key][category] = {}
    # name not default_code
    if name not in file_data['components'][key][category]:
        file_data['components'][key][category][name] = 0.0
    file_data['components'][key][category][name] += quantity

    # Update header data:
    if category == 'Fodera' and not file_data['fodera_material']:
        file_data['fodera_material'] = material  # Always the same!

    if category == 'Tessuto' and not file_data['fabric_material']:
        file_data['fabric_material'] = material  # Always the same!

# -----------------------------------------------------------------------------
#                          Load Job from file:
# -----------------------------------------------------------------------------
# Setup file data:
tg_cols = 16  # total tg col (no TOT)
fixed_col = 4  # Job, row, MRP code, Description
empty_tg = [0 for i in range(tg_cols)]  # No TOT col

pos = 0
for line in open(file_job, 'r'):
    part = line.split(';')

    if not pos:  # First line
        # ---------------------------------------------------------------------
        # Col tg name:
        # ---------------------------------------------------------------------
        tg_pos = 0
        file_data['col_tag'] = empty_tg[:]
        for tg in part[fixed_col:-1]:  # Jump 4 unused columns and TOT:
            file_data['col_tag'][tg_pos] = clean(tg)
            tg_pos += 1
    else:
        # ---------------------------------------------------------------------
        # Tg line (populate)
        # ---------------------------------------------------------------------
        #  Fixed data:
        job = clean(part[0])
        row = clean(part[1])
        mrp_product = clean(part[2])
        description = clean(part[3])
        key = tuple(description.split(' '))
        mrp_name, article_name, color = key

        if not file_data['mrp_name']:
            file_data['mrp_name'] = mrp_name  # always the same?
        if job not in file_data['jobs']:
            file_data['jobs'].append(job)

        # ---------------------------------------------------------------------
        # Tg total data:
        # ---------------------------------------------------------------------
        component_key = job, row  # Used for component
        if key not in file_data['master']:
            file_data['master'][key] = empty_tg[:]  # Duplicate empty
            file_data['master_component'][key] = []  # List of component keys

        # Used for load all component needed:
        file_data['master_component'][key].append(component_key)
        # Populate:
        tg_pos = 0
        for quantity in part[fixed_col:-1]:
            try:
                this_quantity = int(quantity)
                file_data['master'][key][tg_pos] += this_quantity
                # Last columns is total!
            except:
                this_quantity = 0  # empty

            # -----------------------------------------------------------------
            # Range check:
            # -----------------------------------------------------------------
            if this_quantity > 0:
                # Min:
                if tg_pos < file_data['range_tg'][0]:
                    file_data['range_tg'][0] = tg_pos
                # Max:
                if tg_pos > file_data['range_tg'][1]:
                    file_data['range_tg'][1] = tg_pos
            tg_pos += 1
        file_data['total'] += this_quantity  # Update with last number find

    pos += 1

# Compact component view:
print('MODELLO', file_data['mrp_name'],
      'DATA', file_data['date'],
      'LANCIO IN PRODUZIONE', file_data['jobs'])
print('TESSUTO', file_data['fabric_material'],
      'FODERA', file_data['fodera_material'])
# print('TAGLIE COMPLETE', file_data['col_tag'])
# print('RANGE TAGLIE', file_data['range_tg'])
file_data['active_col_tg'] = file_data['col_tag'][
         file_data['range_tg'][0]:file_data['range_tg'][1] + 1]
print('TAGLIE ATTIVE', file_data['active_col_tg'])
block = {
    'center': 9,
    'right': len(file_data['active_col_tg']),
    }

for master_key in file_data['master']:
    subtotal = sum(tuple(file_data['master'][master_key]))
    file_data['total'] += subtotal
    tg_block = file_data['master'][master_key][
               file_data['range_tg'][0]:file_data['range_tg'][1] + 1]
    print('>>>>>>> BLOCCO: ARTICOLO-COLORE', master_key[1:],
          'TAGLIE', tg_block, 'Tot', subtotal)

    # Job linked:
    file_data['components'][master_key] = []
    for job_reference in file_data['master_component'][master_key]:
        references = file_data['components'][job_reference]
        for category in sorted(references,
                               key=lambda x: sort_category.get(x, 0)):

            categories = file_data['components'][job_reference][category]
            for product_name in categories:
                if product_name not in file_data['components'][master_key]:
                    file_data['components'][master_key].append(product_name)
                    # quantity = categories[product_name]
                    print(category, product_name)  # Only first!

print('Totale', file_data['total'])

# print(file_data)
# -----------------------------------------------------------------------------
#                            Excel file:
# -----------------------------------------------------------------------------
# Create WB:
Excel = ExcelWriter(xlsx_file, verbose=True)

# Create WS:
detail_page = 'Lanciati totali'
Excel.create_worksheet(detail_page)

# Parameters:
pixel = {
    # Colums:
    'less': 10,
    'standard': 15,
    'big': 20,

    'center': 4,
    'tg': 5,

    # Row:
    'header': 20,
    'data': 30,
}

fixed_side = {
    'left': 3,
    'center': 7 * 3,
    'right': len(file_data['active_col_tg']) + 1,  # +TOT
}

# 3 part:
left = [
    # Passanti
    pixel['standard'],
    # Raggruppamento:
    pixel['less'],
    pixel['standard'],
    ]
center = [pixel['center'] for i in range(fixed_side['center'])]
right = [pixel['tg'] for i in range(fixed_side['right'])]

Excel.column_width(detail_page, left + center + right)

# Create format:
f_title = Excel.get_format('title')
f_header = Excel.get_format('header')

f_text = Excel.get_format('text')
f_text_center = Excel.get_format('text_center')
f_text_no_low = Excel.get_format('text_no_low')
f_text_title = Excel.get_format('text_title')
f_text_title_center = Excel.get_format('text_title_center')

f_number = Excel.get_format('number')

# -----------------------------------------------------------------------------
#                                  Header:
# -----------------------------------------------------------------------------
# ROW 0
# -----------------------------------------------------------------------------
row = 0
excel_line = [
    ('PASSANTI', f_text_title),
    ('RAGGRUPPAMENTO', f_text_title), '',
    ('MODELLO: ', f_text_title),
]
excel_line.extend(['' for i in range(fixed_side['center'] - 1)])  # - 1 x MODELLO
excel_line.extend([
    ('NOTE', f_text_title),
])
excel_line.extend(['' for i in range(fixed_side['right'] - 1)])  # - 1 x NOTE

Excel.write_xls_line(
    detail_page, row, excel_line, f_text)

# -----------------------------------------------------------------------------
# ROW 1
# -----------------------------------------------------------------------------
row += 1
excel_line = ['', '', '']

excel_line.extend([
    ('LANCIO IN PRODUZIONE N.: ', f_text_title)])

excel_line.extend(['' for i in range(fixed_side['center'] - 1)])

excel_line.extend([('Comp. fodera:', f_text_title)])
excel_line.extend(['' for i in range(fixed_side['right'] - 1)])  # - 1 x NOTE

Excel.write_xls_line(
    detail_page, row, excel_line, f_text)

# -----------------------------------------------------------------------------
# ROW 2
# -----------------------------------------------------------------------------
row += 1
excel_line = [
    '',
    ('Alt. Matrici', f_text_title),
    '',
]

excel_line.extend(['' for i in range(fixed_side['center'])])

excel_line.extend([('Consumo:', f_text_title)])
excel_line.extend(['' for i in range(fixed_side['right'] - 1)])  # - 1 x NOTE

Excel.write_xls_line(
    detail_page, row, excel_line, f_text)

# -----------------------------------------------------------------------------
# ROW 3
# -----------------------------------------------------------------------------
row += 1
excel_line = [
    ('Data', f_text_title),
    ('Lung. Tappeto', f_text_title),
    '']
excel_line.extend(['' for i in range(fixed_side['center'])])
excel_line.extend(['' for i in range(fixed_side['right'])])

Excel.write_xls_line(
    detail_page, row, excel_line, f_text)

# -----------------------------------------------------------------------------
# ROW 4
# -----------------------------------------------------------------------------
row += 1
excel_line = [
    '/',
    ('Lung. progressiva', f_text_title),
    '',
]
excel_line.extend(['' for i in range(fixed_side['center'])])
excel_line.extend(['' for i in range(fixed_side['right'])])

Excel.write_xls_line(
    detail_page, row, excel_line, f_text)

# -----------------------------------------------------------------------------
# ROW 4 - Header title:
# -----------------------------------------------------------------------------
row += 1
excel_line = [
    '',
    ('ARTICOLO', f_text_title),
    ('COLORE', f_text_title),
]
excel_line.extend(['' for i in range(fixed_side['center'])])
excel_line.extend(file_data['active_col_tg'])
excel_line.extend([
    ('Totale\nCapi', f_text_title),])

Excel.write_xls_line(
    detail_page, row, excel_line, f_text)

"""

# Center + Right:
first = True
block_3 = []
block_4 = []
for loop in range(total_size):
    block_3.extend(['', '', ''])  # 3 x size
    block_4.extend([''])  # 1 x size

block_4.extend([''])  # Total box

Excel.write_xls_line(
    detail_page, row,
    block_1 + block_2 + block_3 + block_4, f_text)

# -----------------------------------------------------------------------------
# ROW 1
# -----------------------------------------------------------------------------
row += 1

# Remove title:
block_1[0] = ''
block_2[0] = ''
block_3[0] = ''
block_4[0] = ''

Excel.write_xls_line(
    detail_page, row,
    block_1 + block_2 + block_3 + block_4, f_text)

# -----------------------------------------------------------------------------
# ROW 2
# -----------------------------------------------------------------------------
row += 1
# Assign new title:
block_2[0] = ('Alt. Matrici', f_text_title)

Excel.write_xls_line(
    detail_page, row,
    block_1 + block_2 + block_3 + block_4, f_text)

# -----------------------------------------------------------------------------
# ROW 3
# -----------------------------------------------------------------------------
row += 1
# Assign new title:
block_1[0] = ('Data', f_text_title)
block_2[0] = ('Lung. Tappeto', f_text_title)

Excel.write_xls_line(
    detail_page, row,
    block_1 + block_2 + block_3 + block_4, f_text)

# -----------------------------------------------------------------------------
# ROW 4
# -----------------------------------------------------------------------------
row += 1
# Assign new title:
block_1[0] = file_data['date']
block_2[0] = ('Lung. progessiva', f_text_title)

Excel.write_xls_line(
    detail_page, row,
    block_1 + block_2 + block_3 + block_4, f_text)

block_1[0] = ''


for loop in range(total_size):  # Dynamic (x tg):
    center.extend([w2,  w2,  w2])
    right.append(w2)

right.append(12)  # Total columns


# -----------------------------------------------------------------------------
#                               Merge cells:
# -----------------------------------------------------------------------------
len_b1 = len(block_1)
len_b2 = len(block_2)
len_b3 = len(block_3)
len_b4 = len(block_4)

# 1. PASSANTI
Excel.merge_cell(detail_page, [0, 0, 0, len_b1 - 1])
Excel.merge_cell(detail_page, [1, 0, 2, len_b1 - 1])

# 1. RAGGRUPPAMENTO
Excel.merge_cell(detail_page, [
    0, len_b1,
    0, len_b1 + len_b2 - 1])
Excel.merge_cell(detail_page, [
    1, len_b1,
    1, len_b1 + len_b2 - 1])

# 1.  MODELLO
Excel.merge_cell(detail_page, [
    0, len_b1 + len_b2,
    0, len_b1 + len_b2 + len_b3 - 1])
Excel.merge_cell(detail_page, [
    1, len_b1 + len_b2,
    1, len_b1 + len_b2 + len_b3 - 1])

block = 3  # todo keep parameter
this_range = range(
    len_b1 + len_b2,
    len_b1 + len_b2 + block * total_size,
    block,
)
for x in (2, 3, 4):  # for 3 rows
    for y in this_range:
        Excel.merge_cell(detail_page, [x, y, x, y + block - 1])

# 1.  NOTE
for x in range(5):
    Excel.merge_cell(detail_page, [
        x, len_b1 + len_b2 + len_b3,
        x, len_b1 + len_b2 + len_b3 + len_b4 - 1])

# 3. Alt. Matrici
Excel.merge_cell(detail_page, [
    2, len_b1, 2, len_b1 + 5 - 1])
Excel.merge_cell(detail_page, [
    2, len_b1 + 5, 2, len_b1 + 7 - 1])

# 4. Data
Excel.merge_cell(detail_page, [
    3, 0, 3, len_b1 - 1])
Excel.merge_cell(detail_page, [
    4, 0, 4, len_b1 - 1])

# Lung. Tappeto
Excel.merge_cell(detail_page, [
    3, len_b1, 3, len_b1 + 5 - 1])
Excel.merge_cell(detail_page, [
    3, len_b1 + 5, 3, len_b1 + 7 - 1])

# Lung. progressiva
Excel.merge_cell(detail_page, [
    4, len_b1,
    4, len_b1 + 5 - 1])
Excel.merge_cell(detail_page, [
    4, len_b1 + 5,
    4, len_b1 + 7 - 1])

# -----------------------------------------------------------------------------
#                                  DATA BLOCK:
# -----------------------------------------------------------------------------
# DATA Header
# -----------------------------------------------------------------------------
row += 1
block_2[0] = ''  # Clear

block = 3
this_line = block_1 + block_2 + block_3 + block_4

Excel.write_xls_line(
    detail_page, row, this_line, f_text)

# Merge Articolo:
Excel.merge_cell(detail_page, [
    row, len_b1, row, len_b1 + 2 - 1])
# Merge Colore:
Excel.merge_cell(detail_page, [
    row, len_b1 + 2, row, len_b1 + 2 + 5 - 1])

# -----------------------------------------------------------------------------
# Data lines
# -----------------------------------------------------------------------------
title_row = 0  # Change in procedure
first_rows = []

for color in range(-1, total_color):  # Add extra block of lines for header
    if color == -1:
        this_line[7] = ('ARTICOLO', f_text_title_center)
        this_line[9] = ('COLORE', f_text_title_center)

    for x in range(block):
        Excel.write_xls_line(
            detail_page, row + x, this_line, f_text)

        # Clean header data after written first time:
        if not x:
            first_rows.append(row)
        if color == -1 and not x:
            title_row = row
            this_line[7] = ''
            this_line[9] = ''

        # Merge:
        # import pdb; pdb.set_trace()
        dimension = [row + x, len_b1, row + x, len_b1 + 2 - 1]
        print(dimension)
        Excel.merge_cell(detail_page, dimension)
        dimension = [row + x, len_b1 + 2, row + x, len_b1 + 2 + 5 - 1]
        print(dimension)
        Excel.merge_cell(detail_page, dimension)
    row += block

# Merge after title cell (before raise problems)
# Title:
Excel.merge_cell(detail_page, [
    first_rows[0], len_b1 + 2, first_rows[0] + 2, len_b1 + 7 - 1])

# Unify 2 row in a column (only first 7)
total_row = 0
for row in first_rows:
    if not total_row:
        total_row = row  # First line
    # Write data:

    # Row height different:
    Excel.row_height(detail_page, [row, row+1, row+2], height=data_row_height)

    # First 7 columns merge:
    for col in range(7):
        Excel.merge_cell(detail_page, [
            row, col, row + 2, col])

    # Article merge
    Excel.merge_cell(detail_page, [
        row, 7, row + 2, 8])

# Total block right merge:
total_start = len_b1 + len_b2 + len_b3
for tot_col in range(total_start, total_start + len_b4):
    Excel.merge_cell(detail_page, [
        total_row, tot_col, total_row + 2, tot_col])

data_ref.update({
    'from_row': first_rows[0],
    'total_start_col': total_start,
    })

# -----------------------------------------------------------------------------
#                                   DATA:
# -----------------------------------------------------------------------------
# Header data:
# -----------------------------------------------------------------------------
# Lots:
Excel.write_xls_line(
    detail_page, 0, [
        ('MODELLO: %s' % file_data['article_name'], f_text_title)], f_text,
    col=len_b1+len_b2)
Excel.write_xls_line(
    detail_page, 1, [
        ('Lancio in produzione n.: %s' % file_data['lot'], f_text_title)],
    f_text,
    col=len_b1+len_b2)

# Note:
Excel.write_xls_line(
    detail_page, 0, [('NOTE', f_text_title)], f_text,
    col=len_b1+len_b2+len_b3)

Excel.write_xls_line(
    detail_page, 1, [u'Comp. fodera: %s' % file_data['composition']], f_text,
    col=len_b1+len_b2+len_b3)
Excel.write_xls_line(
    detail_page, 2, [u'Consumo: %s' % file_data['material']], f_text,
    col=len_b1+len_b2+len_b3)


# Write line references:
this_row = data_ref['from_row'] + 3  # Jump header yet compiled

# Generate empty line for total
master_total = [0 for l in file_data['col_tag_clean']]
master_total.append(0)  # Line total

for item in file_data['color']:
    # Article
    Excel.write_xls_line(
        detail_page, this_row, [file_data['article_reference']], f_text, col=7)
    # Color
    Excel.write_xls_line(
        detail_page, this_row, [item], f_text, col=9)  # f_text_no_low
    # Comment
    Excel.write_xls_line(
        detail_page, this_row + 1, [file_data['comment'][item]], f_text, col=9)

    # Total for this size (right)
    total_block = file_data['master'][item][
        file_data['col_range'][0]:
        file_data['col_range'][1] + 1]
    total_of_line = sum([int(t) for t in total_block if t])

    # Update master total:
    for position in range(len(total_block)):
        if total_block[position]:
            if total_block[position]:
                master_total[position] += total_block[position]
    master_total[-1] += total_of_line

    Excel.write_xls_line(
        detail_page, this_row, total_block,
        f_text_center, col=data_ref['total_start_col'])

    # Total of line with formula:
    Excel.write_xls_line(
        detail_page, this_row, [total_of_line],
        f_text_title_center, col=data_ref['total_start_col'] + len_b4 - 1)

    # Unity 3 for per every column:
    total_column_range = range(
        data_ref['total_start_col'], data_ref['total_start_col'] + len_b4)
    for this_col in total_column_range:
        Excel.merge_cell(
            detail_page, [this_row, this_col, this_row + 2, this_col])
    this_row += 3  # multiple rows!

# Write total sizes (and total column):
size_data_complete = file_data['col_tag_clean'][:]
size_data_complete.append('Totale\ncapi')
Excel.write_xls_line(
    detail_page, data_ref['from_row'], size_data_complete,
    default_format=f_text_title_center, col=data_ref['total_start_col'])

# Master total:
Excel.write_xls_line(
    detail_page, this_row, master_total,
    f_text_title_center, col=len_b1 + len_b2 + len_b3)

# , default_format=False, data='')

# cell_1 = Excel.rowcol_to_cell(row, 4)
# cell_2 = Excel.rowcol_to_cell(row, 5)
# Excel.write_formula(detail_page, row, 6, '=%s*%s' % (
#    cell_1, cell_2), f_number, subtotal)

'''
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
'''
print(file_data)
"""
Excel.close_workbook()
