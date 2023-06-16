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
import pdb
import sys
import xlsxwriter
import excel_export
try:
    import ConfigParser
except:
    import configparser as ConfigParser


ExcelWriter = excel_export.excelwriter.ExcelWriter

# Parameters:
w1 = 2  # Size of columns width
w = 3  # Size of columns width


# -----------------------------------------------------------------------------
# Utility:
# -----------------------------------------------------------------------------
def remove_extra_space(value):
    """ Clean double spaces
    """
    value = (value or '').strip()
    return ' '.join(c for c in value.split() if c)


def clean(value):
    """ Clean float
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
cfg_file = os.path.expanduser('./config/setup.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])
file_csv = config.get('parameters', 'file_csv')
xlsx_file = config.get('parameters', 'file_xlsx')
filename = os.path.expanduser(file_csv)

# -----------------------------------------------------------------------------
#                               Parse Mexal file:
# -----------------------------------------------------------------------------
start_text = {
    'mes': 'M&S S.R.L.',
    'lot': 'LANCIO IN PRODUZIONE n. ',
    'composition': 'Comp. fodera             : ',
    'mt': 'Consumo da scheda tecnica: ',
    'coltag': 'COL/TAG',
    'eof': 'per tag',
    'eol': '. . . . . . . . . . . . . . . . . . . ',
}

pos = 0
lines = []
for line in open(file_csv, 'r'):
    line = line.strip()
    lines.append(line)

# Add some extra description fields from file:
file_data = {
    'date': lines[0][len(start_text['mes']):].strip()[:10],
    'lot': remove_extra_space(
        lines[2][len(start_text['lot']):]
    ),
    'article_name': lines[6],
    'composition': lines[7][len(start_text['composition']):],
    'material': remove_extra_space(lines[8][len(start_text['mt']):]),

    # Start population data:
    'master': {},
    'col_tag': {},
    'col_range': ['replace', 0],

    'color': [],
    'comment': {},   # Comment for every line (color line)
    'article_reference': '',  # Changed in procedure
}

# -----------------------------------------------------------------------------
# Load total list of size tag:
# -----------------------------------------------------------------------------
col_tag = lines[9][24:104]
col = -1
for i in range(0, len(col_tag), 5):
    col += 1
    size = col_tag[i:i + 5].strip()
    file_data['col_tag'][col] = size

for pos in range(11, len(lines), 2):
    # Description data:
    pdb.set_trace()
    article = lines[pos]
    if article.startswith(start_text['eof']):
        break
    line1 = lines[pos + 1]
    # comment = remove_extra_space(lines[pos + 2])
    comment = ''
    # line2 = lines[pos + 3]

    # Color:
    article_split = article[:26].split(' ')
    if len(article_split) < 2:
        color = 'NON PRESENTE'
    else:
        color = article_split[1]  # raise error?
    file_data['color'].append(color)
    file_data['comment'][color] = comment

    # Article:
    if file_data['article_reference']:
        # check if is the same:
        if file_data['article_reference'] != article_split[0]:
            print('Errore articolo differente da %s\n%s' % (
                file_data['article_reference'], article
            ))
    else:
        file_data['article_reference'] = article_split[0]

    # Size sub block:
    size_text = article[24:104]
    col = -1  # Start from 0
    size_total = []
    file_data['master'][color] = []
    for i in range(0, len(size_text), 5):
        col += 1
        size = size_text[i:i + 5].strip()
        size_total.append(int(size) if size else '')
        if not size:
            continue

        # Max col:
        if col > file_data['col_range'][1]:
            file_data['col_range'][1] = col
        # Min col:
        if file_data['col_range'][0] == 'replace' or \
                col < file_data['col_range'][0]:
            file_data['col_range'][0] = col
    file_data['master'][color] = size_total

# Last line will be jumped (per tag)
print('Columns range: %s' % file_data['col_range'])
file_data['col_tag_clean'] = file_data['col_tag'].values()[
    file_data['col_range'][0]:file_data['col_range'][1] + 1]

total_size = len(file_data['col_tag_clean'])  # todo only active filter!
total_color = len(file_data['color'])
data_ref = {}  # Reference for data population (done after)

# -----------------------------------------------------------------------------
#                            Excel file:
# -----------------------------------------------------------------------------
# Create WB:
Excel = ExcelWriter(xlsx_file, verbose=True)

# Create WS:
detail_page = 'Lanciati totali'
Excel.create_worksheet(detail_page)

left = [
    # Start
    w1, w1, w1, w1, w1, w1, w1,

    # Fabric:
    w,  w,

    # Color:
    w,  w,  w,  w,  w,
    ]

center = []
right = []
for loop in range(total_size):  # Dynamic (x tg):
    center.extend([w,  w,  w])
    right.append(w)

right.append(12)  # Total columns

total_columns = left + center + right
Excel.column_width(detail_page, total_columns)

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
# Left:
block_1 = [('PASSANTI', f_text_title), '', '', '', '', '', '']
block_2 = [('RAGGRUPPAMENTO', f_text_title), '', '', '', '', '', '']

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
        Excel.merge_cell(detail_page, [
            row + x, len_b1, row + x, len_b1 + 2 - 1])
        Excel.merge_cell(detail_page, [
            row + x, len_b1 + 2, row + x, len_b1 + 2 + 5 - 1])
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
Excel.close_workbook()
