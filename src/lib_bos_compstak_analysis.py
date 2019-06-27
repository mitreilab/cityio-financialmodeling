#%% Set the directory below to the working directory of the project on your computer to import project libraries:
import sys
sys.path.insert(0, 'E:/User Data/danfink/Dropbox (MIT)/REIL/5_TheValueofDesign/2_CityIOFinancialModelling/Code/src/')

import lib_data_connection as connect
import lib_adj_bos_compstak as adjust
import lib_viz_compstak as viz
import lib_nn_setup as nn

import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt


class bos_compstak(object):
    # define class to analyize boston compstak data set
    def __init__(self):
        # establish data connection
        conn = connect.connection('$$IP$$', '$$DB$$', '$$USER$$', '$$PASSWORD$$')
        # cambridge_data = connect.extract(conn, "SELECT * FROM compstak.compstak_cambridge")
        boston_data = connect.extract(conn, "SELECT * FROM compstak.compstak_boston")

        self.use_df_dict = adjust.get_use_data_frames(boston_data)
        self.use_reg_dict = {}
        for use in self.use_df_dict:
            dirty_df = self.use_df_dict[use]
            clean_df = adjust.clean_data(dirty_df)
            year_dict = adjust.get_year_groups(clean_df)
            regs_dict = self.get_regs_dict(year_dict)
            self.use_reg_dict[use] = regs_dict

    def get_regs_dict(self, year_dict):
        # function to make yearly regressions
        # input dictionary mapping years to yearly data frames
        # returns dictionary mapping years to yearly regression models
        results_dict = {}
        for year in year_dict:
            if year_dict[year].shape[0] < 5:
                continue
            else:
                X, Y = nn.make_training_data(year_dict[year], normalize=False)
                if X.shape[0] < 5:
                    continue
                X = sm.tools.tools.add_constant(X)
                model = sm.OLS(Y, X)
                results = model.fit()
                results_dict[year] = results
        return results_dict

    def get_index(self, regs_dict, feature_array):
        # function to make rent index
        # inputs of regression dictionary and prediction feature array
        # set rent prediction to 2019 prediction, or latest year with precition
        # set rent growth to rent index CAGR
        # return rent prediction and rent growth
        index_list = []
        year_list = []
        base_rent = None
        for year in regs_dict:
            year_list.append(year)
            base_rent_prelim = regs_dict[year].predict(feature_array)[0]
            index_list.append(base_rent_prelim)
            if year == 2019:
                base_rent = regs_dict[year].predict(feature_array)[0]
        if base_rent == None: base_rent = base_rent_prelim
        const_scale = 100 / index_list[0]
        index_list = [const_scale * x for x in index_list]
        cagr = (index_list[-1] / index_list[0]) ** (1 / (len(index_list) - 1)) - 1

        return base_rent, cagr
    def calculate_index(self, feature_array, use):
        # wrapper function to get base rent and rent growth
        base_rent, cagr = self.get_index(self.use_reg_dict[use], feature_array)
        return base_rent, cagr


