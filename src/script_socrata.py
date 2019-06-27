# Script file to import public datasets to the REIL Database, via Socrata API
# (C) MIT Real Estate Innovation Lab, 2019
# NB: '#%%' headers signify Jupyter Notebook Cells for VSCode.

#%% Set the directory below to the working directory of the project on your computer to import project libraries:
import sys
sys.path.insert(0, 'E:/User Data/danfink/Dropbox (MIT)/REIL/5_TheValueofDesign/2_CityIOFinancialModelling/Code/src/')
import lib_socrata
import lib_database

#%% Retrieve and parse all datasets belonging to domain:
token = '44TCQSoL2igJ2376fmSMcGkkh'
domain = "data.cityofnewyork.us"
descriptors = lib_socrata.soda.get_dataset_descriptors(domain, token)
parsed_descriptors = lib_socrata.soda.parse_dataset_descriptors(descriptors)


#%% If needed, query and filter through dataset descriptors for data of interest here...
print(parsed_descriptors.classification)
selected = []
for i, row in parsed_descriptors.iterrows():    
    classification = row['classification'][0]
    print(classification['categories'])



#%% Upload dataset descriptors table to database:
engine = 'postgresql+psycopg2://$$USER$$:$$PASSWORD$$@$$IP$$/$$DB$$n'
lib_database.database.upload_table(parsed_descriptors, domain, engine, 'socrata')

#%% Connect to the database and retrieve the socrata sources table:
conn = lib_socrata.database.connect('$$IP$$', '$$DB$$', '$$USER$$', '$$PASSWORD$$')
socrata_table = lib_database.database.execute(conn, 'SELECT * FROM sources."data.cambridgema.gov"')
datasets = lib_socrata.soda.get_datasets(socrata_table)

#%% Upload full datasets into REIL Database (with specified SRID for geospatial data):
for dataset in datasets:
    lib_database.database.upload_data(dataset, 4326)
