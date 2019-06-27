import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import lib_adj_bos_compstak as adjust


def plot_cleaned_vars(df, x_var, y_var, x_cleaner = lambda x: x, y_cleaner = lambda x: x, xticksarg = None, yticksarg =  None):
    # plot cleaned compstak data as scatter plot
    uses = adjust.get_use_data_frames(df)
    index = 1
    fig = plt.figure(dpi=300)
    for u in uses:
        ax = fig.add_subplot(3, 2, index)
        cleaned_df = y_cleaner(x_cleaner(u[0]))
        cleaned_df.plot(x = x_var, y = y_var, title = u[1], kind = 'scatter', ax = ax)
        index += 1
        if xticksarg != None:
            plt.xticks(xticksarg[0],xticksarg[1])
        if yticksarg != None:
            plt.yticks(yticksarg[0], yticksarg[1])
    plt.show()


def make_heat_plot(df, var_list):
    # make a heat plot for compstak data
    clean_df = pd.DataFrame()
    for var in var_list:
        name = var[0]
        cleaner = var[1]
        s = df[name].to_frame()
        clean_s = cleaner(s)
        clean_df = pd.concat([clean_df, clean_s], axis = 1)
    corr = clean_df.corr()
    cmap = seaborn.diverging_palette(220, 10, as_cmap=True)
    seaborn.heatmap(corr, cmap=cmap, annot=True)
    plt.show()

def make_year_hist(df):
    # make histogram plot for compstak data
    years_series = df['commencement_year']
    plt.hist(years_series.tolist(),19)
    plt.show()