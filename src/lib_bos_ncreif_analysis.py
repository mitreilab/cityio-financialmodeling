import lib_data_connection as connect
import lib_adj_bos_compstak as adjust_bos
import lib_viz_compstak as viz
import lib_nn_setup as nn

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt



class bos_ncreif(object):

    def __init__(self):
        # establish data connection
        conn = connect.connection('$$IP$$', '$$DB$$', '$$USER$$', '$$PASSWORD$$')
        self.bos_ncreif = connect.extract(conn, "SELECT * FROM ncreif.ncreif_incexp")

        self.use_opex_dict = self.get_use_opex_dict()



    def get_use_data_frames(self, df):
        # make dictionary that maps real estate use to filtered data frame
        Retail = df[df['PropertyType'] == 'R']
        Office = df[df['PropertyType'] == 'O']
        Industrial = df[df['PropertyType'] == 'I']
        Apt = df[df['PropertyType'] == 'A']
        uses = {'Retail': Retail, 'Office': Office, 'Industrial': Industrial, 'Apartment': Apt}
        return uses


    def get_use_opex_dict(self):
        # make dictionary that maps real estate use to mean opex margin
        dict = self.get_use_data_frames(self.bos_ncreif)
        use_opex_dict = {}
        for use in dict.keys():
            type_df = dict[use]
            type_df['EXP_MRGN'] = type_df['EXP_TOTAL']/type_df['INC_TOTAL']

            type_exp_mrgn = type_df['EXP_MRGN']
            clean_exp_mgn = type_exp_mrgn[pd.notnull(type_exp_mrgn)]

            use_opex_dict[use] = clean_exp_mgn.mean()

        return use_opex_dict