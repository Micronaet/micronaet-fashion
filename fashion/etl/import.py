#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Modules used for ETL - Create User

# Modules required:
import os
import xmlrpclib, sys, csv, ConfigParser
import pdb
from tools.status_history import status
from datetime import datetime


# Set up parameters (for connection to Open ERP Database) *********************
config = ConfigParser.ConfigParser()
file_config = os.path.expanduser('~/etl/fashion/openerp.cfg')
config.read([file_config])
dbname = config.get('dbaccess','dbname')
user = config.get('dbaccess','user')
pwd = config.get('dbaccess','pwd')
server = config.get('dbaccess','server')
port = config.get('dbaccess','port')   # verify if it's necessary: getint
separator = eval(config.get('dbaccess','separator')) # test

# For final user: Do not modify nothing below this line (Python Code) *********
def Prepare(valore):
    # For problems: input win output ubuntu; trim extra spaces
    #valore=valore.decode('ISO-8859-1')
    valore=valore.decode('cp1252')
    valore=valore.encode('utf-8')
    return valore.strip()

def format_date(valore,date=True):
    ''' Formatta nella data di PG
    '''
    try:
        if date:
            gma = valore.split(' ')[0].split('/')
            return '%s-%02d-%02d' % (gma[2], int(gma[1]), int(gma[0]))
    except:
        return False

def format_currency(valore):
    ''' Formatta nel float per i valori currency
    '''
    try:
        return float(valore.split(' ')[-1].replace(',','.'))
    except:
        return 0.0
        
log_file = os.path.expanduser("~/etl/fashion/log/%s.txt" % (datetime.now()))
log = open(log_file, 'w')

def log_event(*event):
    ''' Log event and comunicate with print
    '''
    log.write("%s. %s\r\n" % (datetime.now(), event))
    print event
    return

# XMLRPC connection for autentication (UID) and proxy
sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/common' % (server, port), allow_none=True)
uid = sock.login(dbname ,user ,pwd)
sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (server, port), allow_none=True)

#====================#
# Importazione Costo #
#====================#
only_create = True 
jump_because_imported = True

log_event("Start import fashion.form.cost")
file_input = os.path.expanduser('~/etl/fashion/Costi.txt')
openerp_object = 'fashion.form.cost'
fashion_form_cost = {}
lines = csv.reader(open(file_input,'rb'),delimiter=separator)
counter={'tot':0, 'new':0, 'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            name = Prepare(line[1])
            note = Prepare(line[2])
            sequence = Prepare(line[3])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'name': name,
                'note': note,
                'sequence': sequence,
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   fashion_form_cost[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   fashion_form_cost[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    fashion_form_cost = store.load()
else:
    store.store(fashion_form_cost)    

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#==============================#
# Importazione Caratteristiche #
#==============================#
only_create = True
jump_because_imported = True # True if jump reimportation False for force importation

log_event("Start import fashion.characteristic")
file_input = os.path.expanduser('~/etl/fashion/Caratteristiche.txt')
openerp_object = 'fashion.form.characteristic'
fashion_form_characteristic = {}
lines = csv.reader(open(file_input,'rb'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            name = Prepare(line[1])
            note = Prepare(line[2])
            sequence = Prepare(line[3])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'name': name,
                'note': note,
                'sequence': sequence,
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   fashion_form_characteristic[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   fashion_form_characteristic[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    fashion_form_characteristic = store.load()
else:
    store.store(fashion_form_characteristic)   

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#=======================#
# Importazione Stagioni #
#=======================#
only_create = True
jump_because_imported = True

log_event("Start import fashion.season")
file_input = os.path.expanduser('~/etl/fashion/Stagioni.txt')
openerp_object = 'fashion.season'
fashion_season = {}
lines = csv.reader(open(file_input,'rb'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            name = Prepare(line[1])
            note = Prepare(line[2])
            code = "%s%s%s" % (name[0], name[2], name[6:8])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'name': name,
                'note': note,
                'code': code,
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   fashion_season[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   fashion_season[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    fashion_season = store.load()
else:
    store.store(fashion_season)  

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#=======================#
# Importazione Cuciture #
#=======================#
only_create = True
jump_because_imported = True

log_event("Start import fashion.form.stitch")
file_input = os.path.expanduser('~/etl/fashion/Cuciture.txt')
openerp_object = 'fashion.form.stitch'
fashion_form_stitch = {}
lines = csv.reader(open(file_input,'rb'), delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            name = Prepare(line[1])
            note = Prepare(line[2])
            sequence = Prepare(line[3])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'name': name,
                'note': note,
                'sequence': sequence,
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   fashion_form_stitch[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   fashion_form_stitch[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    fashion_form_stitch = store.load()
else:
    store.store(fashion_form_stitch)  

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#======================#
# Importazione Tessuti #
#======================#
only_create = True
jump_because_imported = True # True if jump reimportation False for force importation

log_event("Start import fashion.fabric")
file_input = os.path.expanduser('~/etl/fashion/Tessuti.txt')
openerp_object = 'fashion.form.fabric'
fashion_form_fabric = {}
lines = csv.reader(open(file_input,'rb'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            code = Prepare(line[1])
            perc_composition = Prepare(line[5])
            if not code:
                log_event("[ERROR] Riga nulla: %s" %(counter['tot']))
                continue
            note = Prepare(line[6])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'code': code,
                'perc_composition': perc_composition,
                'note': note,
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", code)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, code)
                   fashion_form_fabric[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, code)
                   fashion_form_fabric[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug
    
store = status(openerp_object)
if jump_because_imported:
    fashion_form_fabric = store.load()
else:
    store.store(fashion_form_fabric)          
        
log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#=====================#
# Importazione Misure #
#=====================#
only_create = True
jump_because_imported = True # True if jump reimportation False for force importation

log_event("Start import fashion.form.measure")
file_input = os.path.expanduser('~/etl/fashion/Misure.txt')
openerp_object = 'fashion.form.measure'
fashion_form_measure = {}
lines = csv.reader(open(file_input,'rb'), delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            name = Prepare(line[2])
            letter = Prepare(line[1])
            note = Prepare(line[3])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'name': name,
                'letter': letter,
                'note': note,
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   fashion_form_measure[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   fashion_form_measure[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug
    
store = status(openerp_object)
if jump_because_imported:
    fashion_form_measure = store.load()
else:
    store.store(fashion_form_measure)          

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#========================#
# Importazione Accessori #
#========================#
only_create = True
jump_because_imported = True # True if jump reimportation False for force importation

log_event("Start import fashion.form.accessory")
file_input = os.path.expanduser('~/etl/fashion/Accessori.txt')
openerp_object = 'fashion.form.accessory'
fashion_form_accessory = {}
lines = csv.reader(open(file_input,'rb'), delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            name = Prepare(line[1])
            note = Prepare(line[2])
            sequence = Prepare(line[3])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'name': name,
                'note': note,
                #'sequence': sequence, # default 1000
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   fashion_form_accessory[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   fashion_form_accessory[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    fashion_form_accessory = store.load()
else:
    store.store(fashion_form_accessory)  
    
log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#=======================#
# Importazione Articolo #
#=======================#
only_create = True
jump_because_imported = True # True if jump reimportation False for force importation

log_event("Start import fashion.article")
file_input = os.path.expanduser('~/etl/fashion/Articoli.txt')
openerp_object = 'fashion.article'
fashion_article = {}
lines = csv.reader(open(file_input,'rb'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            name = Prepare(line[1])
            note = Prepare(line[2])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'name': name,
                'note': note,
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   fashion_article[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   fashion_article[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)

except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    fashion_article = store.load()
else:
    store.store(fashion_article)

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#======================#
# Importazione Clienti #
#======================#
only_create = False
jump_because_imported = True # True if jump reimportation False for force importation

log_event("Start import res.partner")
file_input = os.path.expanduser('~/etl/fashion/Clienti.txt')
openerp_object = 'res.partner'
res_partner = {}
lines = csv.reader(open(file_input,'rb'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            description = Prepare(line[1])
            comment = Prepare(line[2])
            start = Prepare(line[3])
            name = Prepare(line[4])
            
            name = name or description

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id),('customer','=',True)])
            data = {
                #'description': description,
                'comment': comment,
                'start': start,
                'name': name,
                'is_company': True,
                'access_id': access_id,
                'customer': True,
                'supplier': False,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   res_partner[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   res_partner[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    res_partner = store.load()
else:
    store.store(res_partner)
    
log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#========================#
# Importazione Fornitori #
#========================#
only_create = False
jump_because_imported = True # True if jump reimportation False for force importation

log_event("Start import res.partner")
file_input = os.path.expanduser('~/etl/fashion/Fornitori.txt')
openerp_object = 'res.partner'
res_partner = {}
lines = csv.reader(open(file_input,'rb'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
extra_id = 1000
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = str(extra_id + int(line[0]))
            name = Prepare(line[1])
            comment = Prepare(line[2])

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id),('supplier','=',True)])
            data = {
                #'description': description,
                'comment': comment,
                'name': name,
                'is_company': True,
                'access_id': access_id,
                'customer': False,
                'supplier': True,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   res_partner[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   res_partner[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    res_partner = store.load()
else:
    store.store(res_partner)
    
log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#================================#
# Importazione Listino Accessori #
#================================# 
only_create = False
jump_because_imported = True
log_event("Start import fashion.form.accessory.pricelist")
file_input = os.path.expanduser('~/etl/fashion/Listini.txt')
openerp_object = 'fashion.form.accessory.pricelist'
fashion_form_accessory_pricelist = {}
lines = csv.reader(open(file_input,'rb'), delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            accessory = Prepare(line[1])
            supplier = Prepare(line[2])            
            name = Prepare(line[3])
            um = Prepare(line[4])
            cost = format_currency(line[5])
            extra_info = Prepare(line[6])
            note = Prepare(line[7])

            # Start of importation:
            counter['tot'] += 1

            accessory_id = fashion_form_accessory.get(accessory, 0)
            if not accessory_id:
                log_event("[ERROR] Riga senza accessorio padre (jumped): %s" % (counter['tot']))
                continue

            if supplier and supplier != '0':
                supplier = str(1000 + int(supplier))
                supplier_id = res_partner.get(supplier, 0)
            else:
                supplier_id = False    

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'name': name,
                'accessory_id': accessory_id,
                'supplier_id': supplier_id,
                'um': um,
                'extra_info': extra_info,
                'cost': cost,
                'note': note,
            
                'access_id': access_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   fashion_form_accessory_pricelist[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   fashion_form_accessory_pricelist[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)
except:
    log_event('>>> [ERROR] Error importing data!')
    raise

store = status(openerp_object)
if jump_because_imported:
    fashion_form_accessory_pricelist = store.load()
else:
    store.store(fashion_form_accessory_pricelist)  
    
log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#=====================#
# Importazione Schede #
#=====================#
only_create = True
jump_because_imported = True # True if jump reimportation False for force importation
log_event("Start import fashion.form")
file_input = os.path.expanduser('~/etl/fashion/Schede.txt')
openerp_object = 'fashion.form'
fashion_form = {}
lines = csv.reader(open(file_input, 'rb'), delimiter=separator)
counter = {'tot':0,'new':0,'upd':0}
col_ref_range = range(1, 13)
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            #name = Prepare(line[1])
            model = Prepare(line[1])
            if not model:
                log_event("[ERROR] Riga nulla (senza modello): %s" % (counter['tot']))
                continue

            size_base = Prepare(line[2])
            size_measure = Prepare(line[3])
            review = Prepare(line[4])
            date = format_date(Prepare(line[5]))
            season = Prepare(line[7])
            original = Prepare(line[18])
            h_lining = Prepare(line[19])
            mt_lining = Prepare(line[20])
            cost_lining = Prepare(line[21])
            article = Prepare(line[25])
            #conformed = Prepare(line[26])
            start = Prepare(line[27])
            ironing = Prepare(line[28])
            area = Prepare(line[29])
            #reference = Prepare(line[31])
            cut = Prepare(line[32])
            size = Prepare(line[33])
            colors = Prepare(line[34])
            #product_id = Prepare(line[19])
            article_id = fashion_article.get(article, 0)
            #name = '%s.%s' % (model,review)
            old_model = True
            show_old_model = True

            season_id = fashion_season.get(season, 0)
            
            col_ref = 3 # default
            try:
               if start == '0' or not start:
                   start = '40' # default start point
                   
               if start:
                   col_ref = 1 + (int(size_base) - int(start)) / 2
                   if type(col_ref) != int or col_ref not in col_ref_range:
                       col_ref = 3 # set as default if real value
            except:
                pass  # default if errors
                       
            if not season_id:
                log_event("[WARNING] Stagione non trovata: %s" % (season))
                # creo una stagione fittizia:
                data_season = {
                    'name': "Stagione X%s" % (season,),
                    'note': "Creata manualmente perchè eliminata",
                    'code': "X%s" % (season,),
                    'access_id': season,
                }
                try:
                    season_id = sock.execute(dbname, uid, pwd, 'fashion.season', 'create', data_season)
                    fashion_season[season] = season_id
                except:
                    log_event("[ERROR] Create season during form: ", data_season)

            # parse model 
            model = model.upper()
            if model[0:1].isalpha():
                if model[1:2].isalpha():
                    model_customer = model[0:1]
                    model_article = model[1:2]
                else:
                    model_customer = ''
                    model_article = model[0:1]
            else:
                log_event("Error: Model must start with letter, jump line", model)
                continue # jump line
            model_customer = model_customer
            model_article = model_article
            model_number = ''
            i = 2 if model_customer else 1
            for c in model[2 if model_customer else 1:]:
                if c.isdigit():
                    i += 1
                    model_number += c
                else:
                    break
            model_number = int(model_number) if model_number.isdigit() else 0
            model_revision = model[i:]
            conformed = model_revision == 'C'

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            if len(item) > 1:
                log_event("[ERROR] Scheda già presente: Modello %s Revisione %s" % (model, review))

            data = {
                'model': model,
                # parse model
                'model_customer': model_customer,
                'model_article': model_article,
                'model_number': model_number,
                'model_revision': model_revision,
                
                'size_base': size_base,
                'size_measure': size_measure,
                'review': review,
                'date': date,
                #'create_date': "%s 08:00:00" % (date,),
                'original': original,
                'h_lining': h_lining,
                'mt_lining': mt_lining,
                'article_id': article_id,
                'conformed': conformed,
                'start': start,
                'ironing': ironing,
                'area': area,
                'cut': cut,
                'size': size,
                'colors': colors,
                'season_id': season_id,
                'old_model': old_model,
                'show_old_model': show_old_model,
                'col_ref': col_ref,
                #'name': name,
                #'product_id': product,
                #'cost_lining': cost_lining,
                #'reference': reference, # TODO utente ora è user_id
                'access_id': access_id,
            }

            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", model)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, model, review)
                   fashion_form[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

            else: # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, model, review)
                   fashion_form[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    fashion_form = store.load()
else:
    store.store(fashion_form)

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

# TODO Esequire la query per aggiornare la create_date partendo da date

#====================================#
# Importazione Relazione Abbinamenti #
#====================================#
only_create = True
jump_because_imported = True 

log_event("Start import fashion.measure.rel")
file_input = os.path.expanduser('~/etl/fashion/Abbinamenti.txt')
openerp_object = 'fashion.measure.rel'
fashion_measure_rel = {}
lines = csv.reader(open(file_input,'rb'), delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
try:
    for line in lines:
        if jump_because_imported:
            break
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            access_id = line[0]
            article = line[1]
            measure = line [2]

            article_id = fashion_article.get(article,0)
            measure_id = fashion_form_measure.get(measure,0)

            if not article_id or not measure_id:
                log_event("Jumped line: article or measure not present!")                
                continue
                
            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            data = {
                'access_id': access_id,
                'article_id': article_id,
                'measure_id': measure_id,
            }
            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", article)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, article)
                   fashion_measure_rel[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data)

            else:   # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, article)
                   fashion_measure_rel[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data)

except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

store = status(openerp_object)
if jump_because_imported:
    fashion_measure_rel = store.load()
else:
    store.store(fashion_measure_rel)

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#========================================#
# Importazione Relazione caratteristiche #
#========================================#
only_create = True
jump_because_imported = True

log_event("Start import fashion.form.characteristic.rel")
file_input = os.path.expanduser('~/etl/fashion/SchXcar.txt')
openerp_object = 'fashion.form.characteristic.rel'
#fashion_form_characteristic_rel = {} # Non viene usato il link a questa tabella
lines = csv.reader(open(file_input,'rU'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
max_col = False
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)
            
        if counter['tot'] < 0:
            counter['tot'] += 1
            continue
            
        if len(line) != max_col:
            log_event('[ERROR]', counter['tot'], "Column error! ")
            continue
            
        access_id = line[0]
        form = Prepare(line[1])
        characteristic = Prepare(line[2])
        name = Prepare(line[3])
        
        form_id = fashion_form.get(form, 0)
        characteristic_id = fashion_form_characteristic.get(characteristic, 0)

        # Start of importation:
        counter['tot'] += 1

        # test if record exists (basing on Ref. as code of Partner)
        item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
        if len(item) > 1 :
            log_event("[ERROR] More than one key found!")
        data = {
            'form_id': form_id,
            'characteristic_id': characteristic_id,
            'name': name,
            'old_name': name[:29],
            'access_id': access_id,
        }

        if item:  # already exist
           counter['upd'] += 1
           try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
               #fashion_form_characteristic_rel[access_id] = item[0]
           except:
               log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

        else: # new
           counter['new'] += 1
           try:
               openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
               log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
               #fashion_form_characteristic_rel[access_id] = openerp_id
           except:
               log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

#store = status(openerp_object)
#if jump_because_imported:
#    fashion_form_characteristic_rel = store.load()
#else:
#    store.store(fashion_form_characteristic_rel)
    
log_event("[INFO]","Total line: ", counter['tot'], " (imported: ", counter['new'], ") (updated: ", counter['upd'], ")")

#==============================#
# Importazione Relazione costo #
#==============================#
only_create = True
jump_because_imported = True

log_event("Start import fashion.form.cost.rel")
file_input = os.path.expanduser('~/etl/fashion/SchXcos.txt')
openerp_object = 'fashion.form.cost.rel'
#fashion_form_cost_rel = {}
lines = csv.reader(open(file_input, 'rU'), delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
max_col = False
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)
            
        if counter['tot']<0:
            counter['tot'] += 1
            continue

        if len(line) != max_col:
            log_event('[ERROR]', counter['tot'], "Column error! ")
            continue

        access_id = line[0]
        form_id = Prepare(line[1])
        cost_id = Prepare(line[2])
        value = format_currency(Prepare(line[3]))
        note = Prepare(line[4])

        form_id = fashion_form.get(form_id, 0)
        cost_id = fashion_form_cost.get(cost_id, 0)

        # Start of importation:
        counter['tot'] += 1

        # test if record exists (basing on Ref. as code of Partner)

        item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
        if len(item) > 1 :
            log_event("[ERROR] More than one key found!")
        data = {
            'form_id': form_id,
            'cost_id': cost_id,
            'value': value,
            'note': note,
            'access_id': access_id,
        }

        if item:  # already exist
           counter['upd'] += 1
           try:
               if only_create: 
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
               else:    
                   item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, value)
               #fashion_form_cost_rel[access_id] = item[0]
           except:
               log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

        else: # new
           counter['new'] += 1
           try:
               openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
               log_event("[INFO]", counter['tot'], "Create", openerp_object, value)
               #fashion_form_cost_rel[access_id] = openerp_id
           except:
               log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

#store = status(openerp_object)
#if jump_because_imported:
#    fashion_form_cost_rel = store.load()
#else:
#    store.store(fashion_form_cost_rel)

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#=================================#
# Importazione Relazione Cucitura #
#=================================#
only_create = True
jump_because_imported = True

log_event("Start import fashion.form.stitch.rel")
file_input = os.path.expanduser('~/etl/fashion/SchXcuc.txt')
openerp_object = 'fashion.form.stitch.rel'
#fashion_form_stitch_rel = {}
lines = csv.reader(open(file_input,'rU'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
max_col = False
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)
            
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        if len(line):
            if len(line)!=max_col:
                log_event('[ERROR]', counter['tot'], "Column error! ")
                continue
            access_id = line[0]
            stitch_id = Prepare(line[1])
            form_id = Prepare(line[2])
            name = Prepare(line[3])
            topstitch = Prepare(line[4])
            form_id = fashion_form.get(form_id, 0)
            if not form_id:
                log_event("[ERROR] Stich with form_id = 0,jumped line, ref:", stitch_id)
                continue
            stitch_id = fashion_form_stitch.get(stitch_id, 0)

            # Start of importation:
            counter['tot'] += 1

            # test if record exists (basing on Ref. as code of Partner)

            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            if len(item) > 1 :
                log_event("[ERROR] more than one finded!")
            data = {
                'stitch_id': stitch_id,
                'form_id': form_id,
                'name': name,
                'topstitch': topstitch,
                'access_id': access_id,
            }

            if item:  # already exist
               counter['upd'] += 1
               try:
                   if only_create: 
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
                   else:    
                       item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                       log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
                   #fashion_form_stitch_rel[access_id] = item[0]
               except:
                   log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

            else: # new
               counter['new'] += 1
               try:
                   openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
                   log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
                   #fashion_form_stitch_rel[access_id] = openerp_id
               except:
                   log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

#store = status(openerp_object)
#if jump_because_imported:
#    fashion_form_stitch_rel = store.load()
#else:
#    store.store(fashion_form_stitch_rel)

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#==================================#
# Importazione Relazione Accessori #
#==================================#
only_create = False
jump_because_imported = True

log_event("Start import fashion.form.accessory.rel")
file_input = os.path.expanduser('~/etl/fashion/SchXacc.txt')
openerp_object = 'fashion.form.accessory.rel'
#fashion_form_accessory_rel = {}
lines = csv.reader(open(file_input,'rU'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
max_col = False
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)

        #TODO Error creating data, current record:
        if counter['tot']<0:
            counter['tot'] += 1
            continue

        if len(line)!=max_col:
            log_event("[ERROR]", counter['tot'], "Column error! ")
            continue

        access_id = line[0]
        form = Prepare(line[1])
        accessory = Prepare(line[2])
        name = Prepare(line[3])
        um = Prepare(line[4])
        quantity = format_currency(Prepare(line[5]))        
        supplier = Prepare(line[6])
        currency = format_currency(Prepare(line[7]))
        note = Prepare(line[8]) # TODO mettere nel database
        gerber_name = Prepare(line[9])
        gerber_desc = Prepare(line[10])
        gerber_h = Prepare(line[11])
        gerber_l = Prepare(line[12])

        form_id = fashion_form.get(form, 0)
        
        tot_cost = currency * quantity if currency and quantity else 0.0
        if not form_id:
            log_event("[WARNING] Line jumped, no form ID, Access ID:", access_id , "Access Form ID:", form)
            continue
            
        accessory_id = fashion_form_accessory.get(accessory, 0)
        if supplier:
            supplier = str(extra_id + int(supplier))
            supplier_id = res_partner.get(supplier, False)
        else:
            supplier_id = False    
        # Start of importation:
        counter['tot'] += 1

        # test if record exists (basing on Ref. as code of Partner)
        item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
        if len(item) > 1 :
            log_event("[ERROR] More than one key found!")
        data = {
            'form_id': form_id,
            'accessory_id': accessory_id,
            'name': name,
            'um': um,
            'quantity': quantity,
            'currency': currency,
            'tot_cost': tot_cost,
            'note': note,
            'supplier_id': supplier_id,
            'gerber_name':gerber_name,
            'gerber_desc':gerber_desc,
            'gerber_h':gerber_h,
            'gerber_l':gerber_l,
            'access_id': access_id,
        }

        if item:  # already exist
           counter['upd'] += 1
           try:
               if only_create: 
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
               else:    
                   item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
               #fashion_form_accessory_rel[access_id] = item[0]
           except:
               log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

        else: # new
           counter['new'] += 1
           try:
               openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
               log_event("[INFO]", counter['tot'], "Insert: ", name)
               #fashion_form_accessory_rel[access_id] = openerp_id
           except:
               log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

#store = status(openerp_object)
#if jump_because_imported:
#    fashion_form_accessory_rel = store.load()
#else:
#    store.store(fashion_form_accessory_rel)
    
log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#================================#
# Importazione Relazione Comment #
#================================#
only_create = True
jump_because_imported = True # True if jump reimportation False for force importation <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< reimportare dopo!!!

log_event("Start import fashion.comment.rel")
file_input = os.path.expanduser('~/etl/fashion/Modifiche.txt')
openerp_object = 'fashion.form.comment.rel'
#fashion_form_comment_rel = {}
lines = csv.reader(open(file_input,'rU'),delimiter=separator)
counter={'tot':0, 'new':0, 'upd':0}
max_col = False
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)
            
        if counter['tot'] < 0:
            counter['tot'] += 1
            continue

        if len(line) != max_col:
            log_event('[ERROR]', counter['tot'], "Column error! ")
            continue

        access_id = line[0]
        form = Prepare(line[1])
        reference = Prepare(line[2])
        date = format_date(line[3])
        name = Prepare(line[4])

        form_id = fashion_form.get(form, 0)
        #reference = get_or_create_user_id(dbname, uid, pwd, username)

        # Start of importation:
        counter['tot'] += 1

        # test if record exists (basing on Ref. as code of Partner)
        item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
        if len(item) > 1 :
            log_event("[ERROR] More than one key found!")
        data = {
            'form_id': form_id,
            #'user_id': user_id,
            'reference': reference,
            'date': date,
            'name': name,
            'access_id': access_id,
        }

        if item:  # already exist
           counter['upd'] += 1
           try:
               if only_create: 
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
               else:    
                   item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
               #fashion_form_comment_rel[access_id] = item[0]
           except:
               log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

        else: # new
           counter['new'] += 1
           try:
               openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
               log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
               #fashion_form_comment_rel[access_id] = openerp_id
           except:
               log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())

except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

#store = status(openerp_object)
#if jump_because_imported:
#    fashion_form_comment_rel = store.load()
#else:
#    store.store(fashion_form_comment_rel)

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

#================================#
# Importazione Relazione clienti #
#================================#
only_create = True
jump_because_imported = True # True if jump reimportation False for force importation

log_event("Start import fashion.form.partner.rel")
file_input = os.path.expanduser('~/etl/fashion/SchXcli.txt')
openerp_object = 'fashion.form.partner.rel'
#fashion_form_partner_rel = {}
lines = csv.reader(open(file_input,'rU'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
tot_col = 0
max_col = False
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)

        #TODO errore creating data, current record:
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        
        if len(line)!=max_col:
            log_event('[ERROR]', counter['tot'], "Column error! ")
            continue
                
        access_id = line[0]
        form = Prepare(line[1])
        partner = Prepare(line[2])
        fabric = Prepare(line[3])
        name = Prepare(line[4])
        perc_fabric = Prepare(line[5])
        corr_fabric = Prepare(line[6])
        note_fabric = Prepare(line[7])
        weight = format_currency(Prepare(line[8]))
        h_fabric = format_currency(Prepare(line[9]))
        mt_fabric = format_currency(Prepare(line[10]))
        cost = format_currency(Prepare(line[11]))
        detail = Prepare(line[12])
        wholesale = Prepare(line[13])
        department_store = format_currency(Prepare(line[14]))
        symbol_fabric = Prepare(line[15])
        code = Prepare(line[16])
        gerber_name = Prepare(line[17])
        gerber_desc = Prepare(line[18])
        gerber_h = Prepare(line[19])
        gerber_l = Prepare(line[20])

        form_id = fashion_form.get(form, 0)
        if not form_id:
            log_event("[WARNING] Jump record for empty form_id!")
            continue

        partner_id = res_partner.get(partner, False)
        if not partner_id:
            log_event("[ERROR] Partner non trovato")
            continue
            
        fabric_id = fashion_form_fabric.get(fabric, False)

        # Start of importation:
        counter['tot'] += 1

        # test if record exists (basing on Ref. as code of Partner)
        item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            
        if len(item) > 1 :
            log_event("[ERROR] More than one key found!")
        data = {
            'form_id': form_id,
            'partner_id': partner_id,
            'fabric_id': fabric_id,
            'desc_fabric': name,
            'perc_fabric': perc_fabric,
            'corr_fabric': corr_fabric,
            'note_fabric': note_fabric,
            'weight': weight,
            'h_fabric': h_fabric,
            'mt_fabric': mt_fabric,
            'cost': cost,
            'detail': detail,
            'wholesale': wholesale,
            'department_store': department_store,
            'symbol_fabric': symbol_fabric,
            'code': code,
            'gerber_name': gerber_name,
            'gerber_desc': gerber_desc,
            'gerber_h': gerber_h,
            'gerber_l': gerber_l,
            'access_id': access_id,
        }

        if item:  # already exist
           counter['upd'] += 1
           try:
               if only_create: 
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
               else:    
                   item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
               #fashion_form_partner_rel[access_id] = item[0]
           except:
               log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

        else: # new
           counter['new'] += 1
           try:
               openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
               log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
               #fashion_form_partner_rel[access_id] = openerp_id
           except:
               log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

#store = status(openerp_object)
#if jump_because_imported:
#    fashion_form_partner_rel = store.load()
#else:
#    store.store(fashion_form_partner_rel)
    
log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")





#===========================================#
# Importazione Relazione clienti parte costi#
#===========================================#
only_create = False
jump_because_imported = False
import pdb; pdb.set_trace()
log_event("Start import fashion.form.partner.rel second stes")
file_input = os.path.expanduser('~/etl/fashion/SchXtes.txt')
openerp_object = 'fashion.form.partner.rel'
#fashion_form_partner_rel = {}
lines = csv.reader(open(file_input,'rU'),delimiter=separator)
counter = {'tot':0, 'new':0, 'upd':0}
tot_col = 0
max_col = False
active_cost_list = []
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)

        #TODO errore creating data, current record:
        if counter['tot']<0:
            counter['tot'] += 1
            continue
        
        if len(line) != max_col:
            log_event('[ERROR]', counter['tot'], "Column error! ")
            continue
                
        access_2_id = line[0]
        form = Prepare(line[1])
        fabric = Prepare(line[2])
        #name = Prepare(line[4])
        #h = Prepare(line[4])
        #mt = Prepare(line[5])
        cost = format_currency(Prepare(line[6]))
        ric1 = format_currency(Prepare(line[7]))
        ric2 = format_currency(Prepare(line[8]))
        sale = format_currency(Prepare(line[9])) # Price for GM
        partner = Prepare(line[10])
        note = Prepare(line[11])
    
        try:
            access_2_id = int(access_2_id)
            form = int(form)
            partner = int(partner)
            fabric = int(fabric)
            if not(form and partner and fabric):
                log_event("[ERR] Manca uno dei 3 elementi necessari!")    
                continue           
        except:
            log_event("[ERR] Jump record for empty form_id!")
            continue

        form_id = sock.execute(dbname, uid, pwd, 'fashion.form', 'search', [
            ('access_id', '=', form)])
        if not form_id:
            log_event("[WARNING] Jump record for empty form_id!")
            continue
        form_id = form_id[0]
        if form_id not in active_cost_list:
            active_cost_list.append(form_id)
               
        partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [
            ('access_id', '=', partner)])
        if not partner_id:
            log_event("[ERROR] Partner non trovato")
            continue
        partner_id = partner_id[0]    
            
        fabric_id = sock.execute(dbname, uid, pwd, 'fashion.form.fabric', 'search', [
            ('access_id', '=', fabric)])        
        if not fabric_id:
            log_event("[ERROR] Tessuto non trovato")
            continue
        fabric_id = fabric_id[0]    

        # Start of importation:
        counter['tot'] += 1

        # test if record exists (basing on Ref. as code of Partner)
        item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [
            ('access_2_id', '=', access_2_id)])

        if not item:
            # try to link to partner-fabric id
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [
                ('form_id', '=', form_id),
                ('partner_id', '=', partner_id),
                ('fabric_id', '=', fabric_id),
            ])

        if len(item) > 1 :
            log_event("[ERROR] More than one key found!")
            continue
            
        data = {
            'form_id': form_id,
            'fabric_id': fabric_id,
            'partner_id': partner_id,
            #'h_fabric': h_fabric,
            #'mt_fabric': mt_fabric,
            'cost': cost,
            'retail': ric1,
            'wholesale': ric2,
            'sale': sale,
            'note_cost': note,
            'access_2_id': access_2_id,
        }

        if item: # already exist
           counter['upd'] += 1
           try:
               if only_create: 
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, "(jumped only_create clause)")
               else:    
                   item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                   log_event("[INFO]", counter['tot'], "Write", openerp_object)
           except:
               log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

        else:
           counter['new'] += 1
           try:
               openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
               log_event("[INFO]", counter['tot'], "Create", openerp_object)
           except:
               log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

# Write model_for_cost
sock.execute(dbname, uid, pwd, "fashion.form", 'write', active_cost_list, {'model_for_cost': True})

#=============================================#
# Importazione Relazione clienti listino costi#
#=============================================#
only_create = False
jump_because_imported = False
log_event("Start import fashion.form.cost.rel.pricelist")
file_input = os.path.expanduser('~/etl/fashion/FornitoriXCosto.txt')
openerp_object = 'fashion.form.cost.rel.pricelist'
import pdb; pdb.set_trace()
lines = csv.reader(open(file_input,'rU'),delimiter=separator)
counter = {'tot':0, 'new':0, 'upd':0}
tot_col = 0
max_col = False
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)

        if counter['tot']<0:
            counter['tot'] += 1
            continue
        
        if len(line) != max_col:
            log_event('[ERROR]', counter['tot'], "Column error! ")
            continue
                
        access_id = line[0]
        cost = Prepare(line[1])    # rel
        partner = Prepare(line[2]) # supplier
        value = format_currency(Prepare(line[3]))
        note = Prepare(line[4])
        current = Prepare(line[5]) == '1'
    
        try:
            access_id = int(access_id)
            cost = int(cost)
            partner = 1000 + int(partner)
            if not(cost and partner):
                log_event("[ERR] Manca uno dei 2 elementi necessari!")    
                continue           
        except:
            log_event("[ERR] Jump record for empty form_id!")
            continue

        cost_id = sock.execute(dbname, uid, pwd, 'fashion.form.cost.rel', 'search', [
            ('access_id', '=', cost)])
        if not cost_id:
            log_event("[WARNING] Jump record for empty cost_id!")
            continue
        cost_id = cost_id[0]
               
        partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [
            ('access_id', '=', partner)])
        if not partner_id:
            log_event("[ERROR] Partner non trovato")
            continue
        partner_id = partner_id[0]    
            
        # Start of importation:
        counter['tot'] += 1

        # test if record exists (basing on Ref. as code of Partner)
        item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [
            ('access_id', '=', access_id)])

        if not item:
            # try to link to partner-fabric id
            item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [
                ('cost_rel_id', '=', cost_id),
                ('supplier_id', '=', partner_id),
            ])

        if len(item) > 1 :
            log_event("[ERROR] More than one key found!")
            continue
            
        data = {
            'cost_rel_id': cost_id,
            'supplier_id': partner_id,
            'value': value,
            'note': note,
            'current': current,
            'access_id': access_id,
        }

        if item: # already exist
           counter['upd'] += 1
           try:
               if only_create: 
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, "(jumped only_create clause)")
               else:    
                   item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                   log_event("[INFO]", counter['tot'], "Write", openerp_object)
           except:
               log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

        else:
           counter['new'] += 1
           try:
               openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
               log_event("[INFO]", counter['tot'], "Create", openerp_object)
           except:
               log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!')
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")





#===============================#
# Importazione Relazione Misure #
#===============================#
only_create = True
jump_because_imported = True

log_event("Start import fashion.form.measure.rel")
file_input = os.path.expanduser('~/etl/fashion/SchXmis.txt')
openerp_object = 'fashion.form.measure.rel'
#fashion_form_measure_rel = {}
lines = csv.reader(open(file_input,'rU'),delimiter=separator)
counter={'tot':0,'new':0,'upd':0}
tot_col=0
max_col = False
try:
    for line in lines:
        if jump_because_imported:
            break

        if not max_col:
            max_col = len(line)

        if counter['tot']<0:
            counter['tot'] += 1
            continue

        if len(line) != max_col:
            log_event('[ERROR]', counter['tot'], "Column error! ")
            continue

        access_id = line[0]
        form = Prepare(line[1])
        measure_id = Prepare(line[2])
        size_1 = Prepare(line[3])
        size_2 = Prepare(line[4])
        size_3 = Prepare(line[5])
        size_4 = Prepare(line[6])
        size_5 = Prepare(line[7])
        size_6 = Prepare(line[8])
        size_7 = Prepare(line[9])
        size_8 = Prepare(line[10])
        size_9 = Prepare(line[11])
        size_10 = Prepare(line[12])
        size_11 = Prepare(line[13])
        size_12 = Prepare(line[14])
        size_13 = Prepare(line[15])
        visible = Prepare(line[16])
        real = Prepare(line[19])

        form_id = fashion_form.get(form, 0)
        if not form_id:
            continue

        measure_id = fashion_form_measure.get(measure_id, 0)

        # Start of importation:
        counter['tot'] += 1

        # test if record exists (basing on Ref. as code of Partner)
        item = sock.execute(dbname, uid, pwd, openerp_object , 'search', [('access_id', '=', access_id)])
            
        if len(item) > 1 :
            log_event("[ERROR] More than one key found!")
        data = {
            'form_id': form_id,
            'measure_id': measure_id,
            'size_1': size_1,
            'size_2': size_2,
            'size_3': size_3,
            'size_4': size_4,
            'size_5': size_5,
            'size_6': size_6,
            'size_7': size_7,
            'size_8': size_8,
            'size_9': size_9,
            'size_10': size_10,
            'size_11': size_11,
            'size_12': size_12,
            'size_13': size_13,
            'visible': visible,
            'real': real,
            'access_id': access_id,
        }

        if item:  # already exist
           counter['upd'] += 1
           try:
               if only_create: 
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, " (jumped only_create clause: ", name)
               else:    
                   item_mod = sock.execute(dbname, uid, pwd, openerp_object, 'write', item, data)
                   log_event("[INFO]", counter['tot'], "Write", openerp_object, name)
               #fashion_form_measure_rel[access_id] = item[0]
           except:
               log_event("[ERROR] Modifing data, current record:", data, sys.exc_info())

        else: # new
           counter['new'] += 1
           try:
               openerp_id=sock.execute(dbname, uid, pwd, openerp_object, 'create', data)
               log_event("[INFO]", counter['tot'], "Create", openerp_object, name)
               #fashion_form_measure_rel[access_id] = openerp_id
           except:
               log_event("[ERROR] Error creating data, current record: ", data, sys.exc_info())
except:
    log_event('>>> [ERROR] Error importing data!', sys.exc_info())
    raise #Exception("Errore di importazione!") # Scrivo l'errore per debug

#store = status(openerp_object)
#if jump_because_imported:
#    fashion_form_measure_rel = store.load()
#else:
#    store.store(fashion_form_measure_rel)

log_event("[INFO]","Total line: ",counter['tot']," (imported: ",counter['new'],") (updated: ", counter['upd'], ")")

log_event("End of importation")

