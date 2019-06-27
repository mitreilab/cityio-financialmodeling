import math
import pandas as pd


def get_use_data_frames(df):
    # break up data frame by real estate use, return dictionary mapping use name to dataframe
    Retail = df[df['space_type'] == 'Retail']
    Office = df[df['space_type'] == 'Office']
    Flex_R_D = df[df['space_type'] == 'Flex/R&D']
    Industrial = df[df['space_type'] == 'Industrial']
    Other =  df[df['space_type'] == 'Other']
    uses = {'Retail': Retail, 'Office': Office, 'Flex/R&D': Flex_R_D, 'Industrial': Industrial, 'Other': Other}
    return uses

def get_year_groups(df):
    # break up data farme by commencement year, return dictionary mapping year to dataframe
    year_groups = {}
    for y in range(2007,2020):
        if y not in set(df['commencement_year']): continue
        year_groups[str(y)] = df[df['commencement_year'] == y ]
    return year_groups


def clean_lease_term(df):
    # data clean data frame for lease term
    dirty = df['lease_term']
    clean = []
    for lease in dirty:
        if pd.isnull(lease):
            clean.append(lease)
            continue
        elif type(lease) == float:
            clean.append(int(lease))
            continue
        first_string_list = lease.split()
        string_list = []
        for s in first_string_list:
            string_list.extend(s.split(','))
        if len(string_list) == 2:
            clean.append(float(string_list[0]))
        elif len(string_list) == 4:
            clean.append(float(string_list[0]) + float(string_list[2])/12)
        else:
            print('Lease term description unreadable length')
    df_clean = df.assign(lease_term = clean)
    return df_clean

def clean_freerent(df):
    # data clean data frame for free rent
    dirty = df['free_rent']
    clean = []
    for rent in dirty:
        if rent == float('nan') or rent == None:
            clean.append(rent)
            continue
        elif type(rent) == float:
            clean.append(rent)
            continue
        string_list = rent.split()
        clean.append(float(string_list[0]))
    df_clean = df.assign(free_rent = clean)
    return df_clean

def clean_commencement_year(df):
    # data clean data frame for commencement year
    dirty = df['commencement_date']
    clean = []
    for date in dirty:
        if date == None:
            clean.append(date)
        else:
            year = date.year
            clean.append(year)
    df_clean = df.assign(commencement_year = clean)
    return df_clean

def clean_buildingclass(df):
    # data clean data frame for building class
    dirty = df['building_class']
    clean = []
    for bldg_class in dirty:
        if bldg_class == None:
            clean.append(bldg_class)
        else:
            if bldg_class == 'A':
                clean.append(1)
            elif bldg_class == 'B':
                clean.append(2)
            elif bldg_class == 'C':
                clean.append(3)
    df_clean = df.assign(building_class = clean)
    return df_clean

def clean_submarket(df):
    # data clean data frame for submarket
    dirty = df['submarket']
    clean = []
    for market in dirty:
        if market == None:
            clean.append(market)
        else:
            if market == 'East Cambridge':
                clean.append(1)
            elif market == 'Mid-Cambridge':
                clean.append(2)
    df_clean = df.assign(submarket = clean)
    return df_clean

def clean_rentbumppercent(df):
    # data clean data frame for rent bump percent
    dirty = df['rentbumppercent']
    clean = []
    for pbump in dirty:
        if pbump == None:
            clean.append(pbump)
        else:
            pbump = pbump.split('%')
            clean.append(float(pbump[0]))
    df_clean = df.assign(rentbumppercent = clean)
    return df_clean

def clean_rentbumpdollar(df):
    # data clean data frame for rent bump dollar
    dirty = df['rentbumpdollar']
    clean = []
    for dbump in dirty:
        if dbump ==  None:
            clean.append(dbump)
        else:
            dbump = dbump.split('/')
            clean.append(float(dbump[0]))
    df_clean = df.assign(rentbumpdollar = clean)
    return df_clean



def make_fttovolpe(df, targetlat, targetlong):
    # add series to data frame that gives distance to target location
    original = df['geopoint']
    new = []
    for loc in original:
        if loc == None:
            new.append(loc)
        else:
            splice = loc[1:-1]
            str_list = splice.split(',')
            str_list = [float(i) for i in str_list]
            d = distance_to_volpe_ft(str_list[0], str_list[1], targetlat, targetlong)
            new.append(d)
    df_new = df.assign(fttovolpe = new)
    return df_new



def distance_to_volpe_ft(lat,long, volpe_lat= 42.365266, volpe_long=  -71.085765):
    # helper function to calculate distance to volpe site
    volpe_lat, volpe_long = volpe_lat, volpe_long
    lat, long = math.radians(lat), math.radians(long)

    d_lat = volpe_lat - lat
    d_long = volpe_long - long
    R = 6371000

    a = math.sin(d_lat/2)**2 + math.cos(lat) * math.cos(volpe_lat) * math.sin(d_long/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    m = R * c
    ft = 0.000621371 * 5280 * m
    return ft



def clean_data(df):
    # wrapper function to clean data frame, return cleaned data frame
    clean_df = clean_lease_term(df)
    clean_df = clean_commencement_year(clean_df)
    clean_df = clean_freerent(clean_df)
    # partial_clean_df = clean_rentbumppercent(partial_clean_df)
    # clean_df = clean_rentbumpdollar(partial_clean_df)
    return clean_df


