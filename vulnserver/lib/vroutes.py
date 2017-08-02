import random
import os

from flask import Flask, request
import psycopg2
from sqlalchemy import create_engine, exc
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker

from vulnserver.lib.models import FakerSchema, SchemaGen

schema = None
schema_type = os.environ.get('VULNSERVER_SCHEMA_TYPE', '')
if schema_type.lower().strip() == 'schemagen':
    schema = SchemaGen()
else:
    schema = FakerSchema()
schema.gen()
schema.populate()
select_table, select_table_pk = schema.select_table()
engine = schema.get_engine()
app = Flask(__name__)

@app.route("/")
def index():
    return 'vulnserver: /v0/sqli/select?user_id=1'

@app.route("/v0/sqli/select")
def sqli_select():
    sqltext = '''select * from {0} where {1}={2}'''.format(select_table,select_table_pk,request.args.get('user_id',1))
    with engine.connect() as cursor:
        return str([i for i in cursor.execute(sqltext).fetchmany(10)])

@app.route("/v0/sqli/insert")
def sqli_insert():
    return 'insert'

@app.route("/v0/sqli/shell")
def sqli_shell():
    sql = request.args.get('sql')
    with engine.connect() as cursor:
        return str(cursor.execute(sql).fetchall())

@app.route("/v0/sqli/update")
def sqli_update():
    return 'updated'

@app.route("/v0/sqli/delete")
def sqli_delete():
    return 'deleted'

@app.route("/v0/sqli/refresh")
def sqli_refresh():
    _create_database()
    return 'refreshed'
