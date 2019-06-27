# Library file for functions to connect to the REIL Database
# (C) MIT Real Estate Innovation Lab, 2019
#%% Imports:
import csv
import os
import pickle

import geoalchemy2
import geopandas
import pandas
import pandas.io.sql as psql
import psycopg2
import requests
import sqlalchemy

# module to execute database connection
class database:
    @staticmethod
    def connect(hostname, dbname, username, pwd):
        db_connection = None
        try:
            db_connection = psycopg2.connect(host = hostname, database = dbname, user = username, password = pwd)
            print("Connected to database {} at {}, with user {}".format(dbname, hostname, username))
            return db_connection
        except:
            print("Unable to connect to the database.")

    @staticmethod
    def upload_table(table, name, engine, schema_name):
        engine = sqlalchemy.create_engine(engine) #, connect_args = {'schema':'sources'})

        try:
            table.to_sql(name, engine, schema = schema_name, if_exists='replace', dtype = {'classification':sqlalchemy.types.JSON})
        except Exception as e:
            print("ERROR! Cannot upload {}. Error: {}".format(name, str(e)))
                
        print('Uploaded {}'.format(name))

    @staticmethod
    def execute(connection, sql_query):
        if connection == None:
            print("No connection given.")
            return None
        result = psql.read_sql(sql_query, connection)
        print("Executed SQL Command")
        return result
        
    @staticmethod
    def upload_data(dataset, epsg):
        engine = sqlalchemy.create_engine('postgresql://$$USER$$:$$PASSWORD$$@$$IP$$/$$DB$$')
        content = dataset['content']
        print("Attempting to upload {}".format(dataset['name']))

        if 'geometry' in content.columns:
            geometry_type = str(content.geom_type[0]).upper()
            content['geom'] = content['geometry'].apply(lambda x: geoalchemy2.WKTElement(x.wkt, srid=epsg))
            content.drop('geometry', 1, inplace=True)
            try:
                content.to_sql(dataset['name'], engine, if_exists='replace', index=False, dtype={'geom': geoalchemy2.Geometry(geometry_type, srid=epsg)})
            except Exception as e:
                print("ERROR! Cannot upload {}. Error: {}".format(dataset['name'], str(e)))
                    
            print('Uploaded {}'.format(dataset['name']))

        else:
            try:
                content.to_sql(dataset['name'], engine, if_exists='replace')
            except Exception as e:
                print("ERROR! Cannot upload {}. Error: {}".format(dataset['name'], str(e)))
                
            print('Uploaded {}'.format(dataset['name']))



