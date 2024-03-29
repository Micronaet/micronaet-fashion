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
debug = False
final_debug = False

# -----------------------------------------------------------------------------
# Utility:
# -----------------------------------------------------------------------------
# Utility dict:
center_cols = 9 * 3
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
    value = value.strip()
    if not value:
        return 0.0
    value = value.replace(',', '.')
    try:
        return float(value)
    except:
        print('Error converting float: [{}]'.format(value))
        return 0.0


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
    'jobs': [],  # Total Job touched

    # -------------------------------------------------------------------------
    # Master detail used
    # -------------------------------------------------------------------------
    'master': {},  # Master data for job list
    'master_jobs': {},
    # Master data for component linked:
    #         MRP KEY              JOB LINE KEY
    # (mrp name, article, color): [(job, line)]
    'components': {},
    # Job - Line: components list (completed)

    'total_tg': [],
    'range_tg': [100, 0],  # Tg range position
    'total': 0,  # Total pz.

    # Extra detail used:
    'components_set': {},  # List of component (file 1)
    # not used!

    'components_check': {},
    # Job - Line: components list (check code!)
    #   MRP KEY list to check if unique
    }

# -----------------------------------------------------------------------------
#                         Load components from file BL:
# -----------------------------------------------------------------------------
for line in open(file_product, 'r'):
    part = line.split(';')
    job = clean(part[0])
    row = clean(part[1])
    default_code = clean(part[2])
    name = clean(part[3])
    quantity = clean_float(part[4])
    material = clean(part[5])

    job_line_key = job, row
    # 1. Level components - job line ID
    if job_line_key not in file_data['components']:
        file_data['components'][job_line_key] = {}

    category = get_category(default_code)
    if not category:
        # component not used
        continue
    # 2. Level components - job line ID - Category
    if category not in file_data['components'][job_line_key]:
        file_data['components'][job_line_key][category] = {}

    # 2. Level components - job line ID - Category - Code > Component line
    if default_code not in file_data['components'][job_line_key][category]:
        # Save all line only once!
        file_data['components'][job_line_key][category][default_code] = part

# -----------------------------------------------------------------------------
#                          Load Job from file:
# -----------------------------------------------------------------------------
# Setup file data:
tg_cols = 16  # total tg col (no TOT)
fixed_col = 4  # Job, row, MRP code, Description
empty_tg = [0 for i in range(tg_cols)]  # No TOT col
empty_center = ['' for i in range(center_cols)]  # Center empty cols

pos = 0
get_name = {}
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

        mrp_name = (
            description[:description.index('ART.')]).replace(' ', '')
        mrp_code = mrp_product[:8].strip('-')
        if mrp_code not in get_name:
            get_name[mrp_code] = mrp_name

        article_name = 'ART.%s' % mrp_product[8:11]
        color = 'COL.%s' % mrp_product[12:15]
        # Not present extra description:
        mrp_key = mrp_code, article_name, color

        # mrp_key = tuple(description.split(' '))
        # Compact extra data for key:
        # if len(mrp_key) > 3:
        #    new_key = list(mrp_key[:2])
        #    key3 = ' '.join(mrp_key[2:])
        #    new_key.append(key3)
        #    mrp_key = tuple(new_key)
        # mrp_name, article_name, color = mrp_key  # Must be 3 here!

        if not file_data['mrp_name']:
            file_data['mrp_name'] = mrp_name  # always the same?
        if job not in file_data['jobs']:
            file_data['jobs'].append(job)

        # ---------------------------------------------------------------------
        # Tg total data:
        # ---------------------------------------------------------------------
        job_line_key = job, row  # Used for component
        if mrp_key not in file_data['master']:
            file_data['master'][mrp_key] = empty_tg[:]  # Duplicate empty
            file_data['master_jobs'][mrp_key] = []  # List component keys

        # Used for load all component needed:
        file_data['master_jobs'][mrp_key].append(job_line_key)
        # Populate:
        tg_pos = 0
        this_quantity = 0
        for quantity in part[fixed_col:-1]:
            try:
                this_quantity = int(quantity)
                file_data['master'][mrp_key][tg_pos] += this_quantity
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
file_data['active_col_tg'] = file_data['col_tag'][
         file_data['range_tg'][0]:file_data['range_tg'][1] + 1]

# Total (last line):
file_data['total_tg'] = [0 for loop in range(len(file_data['active_col_tg']))]

block = {
    'center': 9,
    'right': len(file_data['active_col_tg']),
    }

for mrp_key in sorted(file_data['master']):
    if debug:
        print(mrp_key)
    subtotal = sum(tuple(file_data['master'][mrp_key]))
    file_data['total'] += subtotal
    tg_block = file_data['master'][mrp_key][
               file_data['range_tg'][0]:file_data['range_tg'][1] + 1]

    # -------------------------------------------------------------------------
    # Update total line
    # -------------------------------------------------------------------------
    tg_pos = 0
    for tg_value in tg_block:
        file_data['total_tg'][tg_pos] += tg_value
        tg_pos += 1

    # -------------------------------------------------------------------------
    # Component linked with job-line:
    # -------------------------------------------------------------------------
    file_data['components_check'][mrp_key] = []  # Save code x check double
    file_data['components_set'][mrp_key] = []  # Save component record
    for job_line_key in file_data['master_jobs'][mrp_key]:
        if job_line_key not in file_data['components']:
            print('\n\n\n')
            print('*' * 100)
            print('ERRORE: Non riesco a trovare gli impegni delle BL '
                  'per il lanciato {} riga {}.\n'
                  'Procedura bloccata, chiudere questa videata e '
                  'rilanciare una volta corretto il problema nel '
                  'gestionale.'.format(
                        job_line_key[0], job_line_key[1],
                  ))
            print('*' * 100)
            print('\n\n\n')
            pdb.set_trace()
        component_list = file_data['components'][job_line_key]
        for category in sorted(component_list,
                               key=lambda x: sort_category.get(x, 0)):

            category_components = \
                file_data['components'][job_line_key][category]
            for default_code in category_components:
                # Use check list to keep only first code record:
                if default_code not in file_data['components_check'][
                        mrp_key]:
                    component_record = category_components[default_code]
                    component_name = (
                        category,
                        '%s\n%s-%s\n%s' % (
                        component_record[3].strip(),  # Component name
                        component_record[6].strip(),  # Supplier code
                        component_record[7].strip(),  # Supplier name
                        component_record[8].strip(),  # Supplier name
                        ))
                    # Save for report:
                    file_data['components_set'][mrp_key].append(component_name)
                    # Update check list:
                    file_data['components_check'][mrp_key].append(
                        default_code)

# -----------------------------------------------------------------------------
#                            Excel file:
# -----------------------------------------------------------------------------
# Create WB:
Excel = ExcelWriter(xlsx_file, verbose=True)
# Create WS:
detail_page = u'Lanciati totali'
Excel.create_worksheet(detail_page)

# Parameters:
pixel = {
    # Colums:
    'less': 10, 'standard': 15, 'big': 20, 'wide': 40,

    'center': 4, 'tg': 5,

    # Row:
    'h_header': 20, 'h_data': 35,
}

fixed_side = {
    'left': 3,
    'center': center_cols,
    'right': len(file_data['active_col_tg']) + 1,  # +TOT
}

# 3 part:
left = [
    # Passanti
    pixel['standard'],
    # Raggruppamento:
    pixel['less'],
    pixel['wide'],
    ]
center = [pixel['center'] for i in range(fixed_side['center'])]
right = [pixel['tg'] for i in range(fixed_side['right'] - 1)]
right.append(pixel['less'])  # Total column

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
    ('MODELLO: %s' % file_data['mrp_name'], f_text_title),
]
excel_line.extend(['' for i in range(fixed_side['center'] - 1)])  # - 1 x MOD.
excel_line.extend([
    ('NOTE', f_text_title),
])
excel_line.extend(['' for i in range(fixed_side['right'] - 1)])  # - 1 x NOTE

Excel.write_xls_line(detail_page, row, excel_line, f_text)

# Group:
Excel.merge_cell(detail_page, [row, 1, row, 2])
Excel.merge_cell(detail_page, [row, 3, row, 3 + fixed_side['center'] - 1])
Excel.merge_cell(detail_page, [
    row, 3 + fixed_side['center'],
    row, 3 + fixed_side['center'] + fixed_side['right'] - 1])

# -----------------------------------------------------------------------------
# ROW 1
# -----------------------------------------------------------------------------
row += 1
excel_line = [
    '',
    ('LANCIO IN PRODUZIONE N.: %s' % ', '.join(file_data['jobs']),
     f_text_title),
    '',
    ]
excel_line.extend(['' for i in range(fixed_side['center'])])
excel_line.extend(['' for i in range(fixed_side['right'])])

Excel.write_xls_line(detail_page, row, excel_line, f_text)

# Group:
Excel.merge_cell(detail_page, [row, 1, row, 2])
Excel.merge_cell(detail_page, [row, 3, row, 3 + fixed_side['center'] - 1])
Excel.merge_cell(detail_page, [
    row, 3 + fixed_side['center'],
    row, 3 + fixed_side['center'] + fixed_side['right'] - 1])

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

# excel_line.extend([('Consumo:', f_text_title)])
excel_line.extend(['' for i in range(fixed_side['right'])])

Excel.write_xls_line(detail_page, row, excel_line, f_text)

# Group:
Excel.merge_cell(detail_page, [row, 1, row, 2])
# Excel.merge_cell(detail_page, [row, 3, row, 3 + fixed_side['center'] - 1])
Excel.merge_cell(detail_page, [
    row, 3 + fixed_side['center'],
    row, 3 + fixed_side['center'] + fixed_side['right'] - 1])

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

Excel.write_xls_line(detail_page, row, excel_line, f_text)

# Group:
Excel.merge_cell(detail_page, [row, 1, row, 2])
# Excel.merge_cell(detail_page, [row, 3, row, 3 + fixed_side['center'] - 1])
Excel.merge_cell(detail_page, [
    row, 3 + fixed_side['center'],
    row, 3 + fixed_side['center'] + fixed_side['right'] - 1])

# -----------------------------------------------------------------------------
# ROW 4
# -----------------------------------------------------------------------------
row += 1
excel_line = [
    file_data['date'],
    ('Lung. progressiva', f_text_title),
    '',
]
excel_line.extend(['' for i in range(fixed_side['center'])])
excel_line.extend(['' for i in range(fixed_side['right'])])

Excel.write_xls_line(detail_page, row, excel_line, f_text)

# Group:
Excel.merge_cell(detail_page, [row, 1, row, 2])
Excel.merge_cell(detail_page, [
    row, 3 + fixed_side['center'],
    row, 3 + fixed_side['center'] + fixed_side['right'] - 1])

# Row height header:
Excel.row_height(
    detail_page, tuple(range(0, row + 1)), height=pixel['h_header'])

# -----------------------------------------------------------------------------
#                                  DATA BLOCK:
# -----------------------------------------------------------------------------
# ROW 4 - Header title:
# -----------------------------------------------------------------------------
row += 1
excel_line = [
    ('PROD.', f_text_title_center),
    ('ARTICOLO', f_text_title_center),
    ('COLORE', f_text_title_center),
]
excel_line.extend(['' for i in range(fixed_side['center'])])
excel_line.extend([
    (cell, f_text_title_center) for cell in file_data['active_col_tg']])
excel_line.extend([('Totale\nCapi', f_text_title_center)])

Excel.write_xls_line(detail_page, row, excel_line, f_text)

# Row height header:
Excel.row_height(detail_page, [row ], height=pixel['h_data'])

# Merge 3 lines and block 3x3:
for this_row in range(2, 5):
    for col in range(0, fixed_side['center'], 3):
        this_col = fixed_side['left'] + col
        Excel.merge_cell(
            detail_page, [
                this_row, this_col, this_row, this_col + 2])

# -----------------------------------------------------------------------------
# ROW 5 - Line data:
# -----------------------------------------------------------------------------
row += 1
empty_component = ['', '', '']
empty_component.extend(empty_center)
merge_from = len(empty_component)
empty_component.extend(['' for cell in tg_block])
empty_component.extend([''])
merge_to = len(empty_component)

start_row = row
for mrp_key in sorted(file_data['master']):
    block_row = row

    mrp_code, block_name, color_name = mrp_key
    mrp_name = get_name[mrp_code]
    # fabric_name = '%s %s' % (block_name, color_name)
    tg_block = file_data['master'][mrp_key][
               file_data['range_tg'][0]:file_data['range_tg'][1] + 1]
    subtotal = sum(tuple(file_data['master'][mrp_key]))

    # Article first line:
    excel_line = [
        (mrp_code[:7], f_text_title), (block_name, f_text_title),
        (color_name, f_text_title)]
    excel_line.extend(empty_center)
    excel_line.extend([(cell, f_text_center) for cell in tg_block])
    excel_line.extend([(subtotal, f_text_title_center)])
    Excel.write_xls_line(detail_page, row, excel_line, f_text)
    row += 1

    # -------------------------------------------------------------------------
    # Component extra line:
    # -------------------------------------------------------------------------
    excel_line = empty_component[:]
    for component_detail in file_data['components_set'][mrp_key]:
        # Also fabric is always loaded!
        excel_line[1] = component_detail[0]  # category
        excel_line[2] = component_detail[1]  # component
        Excel.write_xls_line(detail_page, row, excel_line, f_text)
        row += 1

    # Merge TG cells:
    for this_col in range(merge_from, merge_to):
        Excel.merge_cell(
            detail_page, [
                block_row, this_col, row-1, this_col])

excel_line = file_data['total_tg'][:]
excel_line.append(file_data['total'])
Excel.write_xls_line(
    detail_page, row, [(v, f_text_title_center) for v in excel_line], f_text,
    col=fixed_side['left'] + fixed_side['center'])

# Row height data:
Excel.row_height(
    detail_page, tuple(range(start_row, row)), height=pixel['h_data'])

if final_debug:
    print('MASTER')
    print(file_data['master'])

    print('\n\nMASTER JOB')
    print(file_data['master_jobs'])

    print('\n\nDETTAGLIO LISTA COMPONENTI')
    print(file_data['components'])

    print('\n\nDETTAGLIO SET COMPONENTI')
    print(file_data['components_set'].keys())
    print('\n\n')
    print(file_data['components_set'])

    # print('\n\nDETTAGLIO CHECK COMPONENTI')
    # print(file_data['components_set'])

    pdb.set_trace()

"""
# cell_1 = Excel.rowcol_to_cell(row, 4)
# cell_2 = Excel.rowcol_to_cell(row, 5)
# Excel.write_formula(detail_page, row, 6, '=%s*%s' % (
#    cell_1, cell_2), f_number, subtotal)

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
"""
Excel.close_workbook()
