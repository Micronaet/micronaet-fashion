# Copyright 2019  Micronaet SRL (<http://micronaet.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Label job report',
    'version': '0.1',
    'category': 'Report',
    'description': '''        
        Lab job management
        Wizard for import from Excel
        ''',
    'author': 'Micronaet S.r.l. - Nicola Riolini',
    'website': 'http://www.micronaet.it',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'report_aeroo',
        ],
    'init_xml': [],
    'demo': [],
    'data': [
        'label_job_view.xml',
        'report/label_report.xml',
        'wizard/wizard_import_job.xml',
        ],
    'active': False,
    'installable': True,
    'auto_install': False,
    }
