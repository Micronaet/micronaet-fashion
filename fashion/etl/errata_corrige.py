#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Modules used for ETL - Create User

# Modules required:
import os
import xmlrpclib, sys, csv, ConfigParser
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

# XMLRPC connection for autentication (UID) and proxy
sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/common' % (server, port), allow_none=True)
uid = sock.login(dbname ,user ,pwd)
sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (server, port), allow_none=True)

if len(sys.argv) != 2: 
    print "Use: errata_corrige parameters\n parameters: supplier, code, price, user, mt, header, colors, model, model_partner, reload_model"
    sys.exit()
if sys.argv[1] == 'supplier':
    result = sock.execute(dbname, uid, pwd, "fashion.form" , "correct_supplier_code")
    print "Supplier updated"

elif sys.argv[1] == 'code':
    result = sock.execute(dbname, uid, pwd, "fashion.form" , "set_customer_code_in_form")
    print "Code updated"

elif sys.argv[1] == 'price':
    result = sock.execute(dbname, uid, pwd, "fashion.form" , "set_correct_accessory_price")
    print "Price updated"

elif sys.argv[1] == 'user':
    result = sock.execute(dbname, uid, pwd, "fashion.form" , "set_user_comment")
    print "Price updated"

elif sys.argv[1] == 'mt':
    result = sock.execute(dbname, uid, pwd, "fashion.form" , "set_mt")
    print "Mt updated"

elif sys.argv[1] == 'header':
    result = sock.execute(dbname, uid, pwd, "fashion.form" , "set_header")
    print "Header updated"

elif sys.argv[1] == 'colors':
    result = sock.execute(dbname, uid, pwd, "fashion.form" , "set_colors")
    print "Colors updated"

elif sys.argv[1] == 'model':
    result = sock.execute(dbname, uid, pwd, "fashion.form", "explode_model")
    print "Model explosion updated"

elif sys.argv[1] == 'model_partner':
    result = sock.execute(dbname, uid, pwd, "fashion.form", "explode_model_partner")
    print "Model partner explosion updated"

elif sys.argv[1] == 'reload_model':
    result = sock.execute(dbname, uid, pwd, "fashion.form", "force_all_recalculation")
    print "Model reloaded and forced"
    

