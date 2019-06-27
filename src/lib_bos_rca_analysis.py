import lib_data_connection as connect
import lib_adj_bos_compstak as adjust_bos
import lib_viz_compstak as viz
import lib_nn_setup as nn

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

class bos_rca(object):
    def __init__(self):
        # establish data connection
        conn = connect.connection('$$IP$$', '$$DB$$', '$$USER$$', '$$PASSWORD$$')
        bos_rca = connect.extract(conn, "SELECT * FROM rca.rca_transactions_bos")
        # make dictionary the maps real estate use to average cap rate
        dict = self.get_use_data_frames(bos_rca)
        self.use_caprate_dict = {}
        for use in dict.keys():
            type_df = dict[use]
            type_cap = type_df['caprate']
            clean_cap = type_cap[pd.notnull(type_cap)]
            self.use_caprate_dict[use] = clean_cap.mean()


    def get_use_data_frames(self,df):
        # function that maps real estate use to filtered data frame
        Retail = df[df['main_type'] == 'Retail']
        Office = df[df['main_type'] == 'Office']
        Industrial = df[df['main_type'] == 'Industrial']
        Hotel = df[df['main_type'] == 'Hotel']
        SH_C = df[df['main_type'] == 'Seniors Housing & Care']
        Dev = df[df['main_type'] == 'Dev Site']
        Apt = df[df['main_type'] == 'Apartment']
        Other =  df[df['main_type'] == 'Other']
        uses = {'Retail': Retail, 'Office': Office, 'Industrial': Industrial, 'Hotel': Hotel, 'Seniors Housing & Care': SH_C, 'Dev Site': Dev,  'Apartment': Apt, 'Other': Other}
        return uses


