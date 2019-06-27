import numpy as np
import matplotlib.pyplot as plt
import tensorflow
import pickle
import lib_adj_bos_compstak as adjust
import math
import pandas as pd
import keras.optimizers
import keras.initializers

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras import regularizers

def feature_transformation(row):
    # make feature transformation for row of database
    feature_list = []
    # relative to class A
    class_map = {'A': [0,0], 'B': [1,0], 'C': [0,1] }
    submarket_list = ['East Cambridge', 'North Station Government Center', 'Back Bay', 'Mid-Town', 'North End', 'Allston Brighton', 'Roxbury Dorchester', 'Mid-Cambridge', 'Brookline', 'Seaport', 'Near North']
    submarket_iter = [(submarket_list[s],[0]*s + [1] + [0]*(len(submarket_list)-s - 1)) for s in range(len(submarket_list))]
    submarket_map = {key:value for (key, value) in submarket_iter}
    # realtive to 1 year lease term
    leaseterm = row['lease_term'] - 1
    buildingclass = class_map[row['building_class']]
    # relative to financial district
    if row['submarket'] != 'Financial District': submarket = submarket_map[row['submarket']]
    else: submarket = [0]*len(submarket_list)
    # relative to 1 floor
    bldg_fl = row['building_floors'] - 1
    # relative to 50,000
    bldg_sz = row['building_size'] - 50000
    # realative to 1950
    yearbuilt = row['year_built'] - 1950
    # realative to 0
    TI = row['work_value_usd']
    # relative to 0 months
    free_rent = row['free_rent']
    feature_list.extend(submarket)
    feature_list.extend(buildingclass)
    feature_list.append(leaseterm)
    feature_list.append(bldg_fl)
    feature_list.append(bldg_sz)
    feature_list.append(yearbuilt)
    feature_list.append(TI)
    feature_list.append(free_rent)
    return feature_list



def check_row_complete(row, feature_list):
    # make sure required data is contained in used data rows
    for feature in feature_list:
        if row[feature] == None:
            return False
        try:
            if math.isnan(row[feature]):
                return False
        except:
            pass
        try:
            if pd.isna(row[feature]):
                return False
        except:
            pass
    return True

def normalize_features(df, feature_list):
    # normalized input features to mean distances above or below mean
    for feature in feature_list:
        series = df[feature]
        mean = series.mean()
        normalized = (series-mean)/(mean)
        df = df.assign(**{feature: normalized})
    return df

def make_training_data(df, normalize = True):
    # make training data, either normalized or raw
    # return tuple of predictive features and prediction outputs
    cleaned_df = adjust.clean_data(df)
    needed_features = ['effective_rent_usd_per_year', 'building_size','building_class', 'building_floors', 'lease_term', 'submarket', 'year_built', 'work_value_usd', 'free_rent']
    if normalize:
        normal_features = ['lease_term']
        train_clean_df = normalize_features(cleaned_df, normal_features)
    else:
        train_clean_df = cleaned_df
    X_train = []
    Y_train = []
    for row_tup in train_clean_df.iterrows():
        row = row_tup[1]
        if check_row_complete(row, needed_features):
            x = feature_transformation(row)
            y = [row['effective_rent_usd_per_year']]
            X_train.append(x)
            Y_train.append(y)
        else:
            continue
    X_train = np.array(X_train)
    Y_train = np.array(Y_train)
    return (X_train, Y_train)

def save_model(x):
    pickle.dump(x, open("Rent_model", "wb"))


def load_model():
    x = pickle.load(open("Rent_model", "rb"))
    return x

def train_model(data, epochs):
    # make single layer linear neural network with 1 fully connected node
    # training mean squared error using adam optimizer
    # use 85% of data for training, 15% for validation
    model = Sequential()
    # model.add(Dropout(.2))
    # model.add(Dense(1, activation='linear', input_dim=5, kernel_regularizer=regularizers.l2(0.2)))
    weight_init = keras.initializers.random_normal(mean=0.0 , stddev = 4)
    bias_init = keras.initializers.random_normal(mean=40.0, stddev=1)
    model.add(Dense(1, activation='linear', input_dim=18, kernel_initializer= weight_init, bias_initializer= bias_init))
    opt = keras.optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)

    model.compile(optimizer= opt,
                  loss='mean_squared_error',
                  metrics=['accuracy'])

    X, Y = make_training_data(data, normalize=False)
    # print(X, Y)

    # Train the model, iterating on the data in batches of 32 samples
    history = model.fit(X, Y, epochs=epochs, batch_size= 1, validation_split = 0.15, verbose = 2, shuffle=True)
    # l = model.get_layer(index = 1)
    l = model.get_layer(index=0)
    print(l.get_weights())



    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()
    return model, history