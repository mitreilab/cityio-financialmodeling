# Library file for functions to import public datasets to the REIL Database, via Socrata API
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
import sodapy
import sqlalchemy

class soda:
    @staticmethod
    def get_dataset_descriptors(domain, token):
        client = sodapy.Socrata(domain, token)
        return client.datasets()

    @staticmethod
    def parse_dataset_descriptor(descriptor):
        items = {}

        items['title'] = descriptor['resource']['name']
        items['id'] = descriptor['resource']['id']
        items['name'] = items['id'] + '_' + items['title'].lower().replace(' ', '_').replace('(','').replace(')','')

        items['description'] = descriptor['resource']['description']
        items['classification'] = [descriptor['classification']]
        items['domain'] = descriptor['metadata']['domain']
        items['permalink'] = descriptor['permalink']
        items['link'] = descriptor['link']
        
        #dataframe = pandas.DataFrame(items)
        return items

    @staticmethod
    def parse_dataset_descriptors(descriptors):
        parsed_descriptors = []
        for descriptor in descriptors:
            foo = soda.parse_dataset_descriptor(descriptor)
            parsed_descriptors.append(foo)
        return pandas.DataFrame(parsed_descriptors)

    @staticmethod
    def get_metadatas(socrata_table, identifier_column_name, domain_column_name):
        ids = socrata_table[identifier_column_name]
        domains = socrata_table[domain_column_name]

        metadatas = []
        for id, domain in zip(ids, domains):
            client = sodapy.Socrata(domain, '44TCQSoL2igJ2376fmSMcGkkh')
            try:
                metadata = client.get_metadata(id)
                metadata['domain'] = domain
                metadatas.append(metadata)
                print("Retrieved metadata for dataset: {}".format(str(id)))
            except:
                continue
        return metadatas
    
    @staticmethod
    def get_data(metadata):
        data = {}
        endpoint = ''
        print("Processing dataset: {}".format(metadata['id']))
        with requests.Session() as session:
            if metadata['viewType'] == 'tabular':
                endpoint = 'https://' + metadata['domain'] + '/resource/' + metadata['id'] + '.csv'
                response = session.get(endpoint)
                decoded_response = response.content.decode('utf-8')
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                    return None
                content = csv.reader(decoded_response.splitlines(), delimiter = ',')
                dataframe = pandas.DataFrame(list(content))
                dataframe.columns = dataframe.iloc[0]
                dataframe.columns = [x.lower().replace(' ', '_').replace('(', '').replace(')', '') for x in dataframe.columns]
                data['content'] = dataframe.drop([0])

            if metadata['viewType'] == 'geo':
                endpoint = 'https://' + metadata['domain'] + '/api/geospatial/' + metadata['id'] + '?method=export&format=geojson'
                response = requests.get(endpoint)
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                    return None
                content = response.json()

                #data = geopandas.GeoDataFrame()
                data['content'] = geopandas.GeoDataFrame.from_features(content['features'])   

        name = metadata['id'] + '_' + metadata['name'].lower().replace(' ', '_').replace('(','').replace(')','')
        if len(name) > 63:
            name = name[0:63]
        data['name'] = name
        data['id'] = metadata['id']
        data['domain'] = metadata['domain']
        data['viewType'] = metadata['viewType']
        return data

    @staticmethod
    def get_datasets(socrata_table):
        datasets = []
        metadatas = soda.get_metadatas(socrata_table, 'id', 'domain')
        for metadata in metadatas:
            datasets.append(soda.get_data(metadata))
        return datasets

class filesystem:
    @staticmethod
    def save_contents(dataset, dir):
        filename = ''
        if dataset['viewType'] == 'tabular':
            filename = dataset['name'] + '.csv'
            filepath = os.path.join(dir, filename)
            dataset['content'].to_csv(filepath, index = False, header = False, doublequote=True)
            #with open(os.path.join(dir, filename), 'w') as file:
            #    writer = csv.writer(file)
            #    writer.writerows(dataset['content'])

        if dataset['viewType'] == 'geo':
            filename = dataset['name'] + '.geojson'
            with open(os.path.join(dir, filename), 'wb') as file:
                pickle.dump(str(dataset['content']), file, pickle.DEFAULT_PROTOCOL)
        return None

    @staticmethod
    def save_datasets(datasets, dir):
        for dataset in datasets:
            save_contents(dataset, dir)


