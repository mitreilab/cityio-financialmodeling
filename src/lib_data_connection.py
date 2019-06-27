import psycopg2
import pandas.io.sql as psql
import requests

# module to execute database connection


def connection(hostname, dbname, username, pwd):
    db_connection = None
    try:
        db_connection = psycopg2.connect(host = hostname, database = dbname, user = username, password = pwd)
        return db_connection
    except:
        print("Unable to connect to the database.")


def extract(connection, sql_query):
    if connection == None:
        print("No connection given.")
        return None
    data = psql.read_sql(sql_query, connection)
    return data