import numpy as np
import pandas as pd
import seaborn as sns
import os
from matplotlib import pyplot as plt

def tidy_and_wrangle_data():
    """
    Tidy and wrangle the data

    Returns
    --------
    demandPivot : pandas dataframe
        a tidied dataframe representing the demands
    """
    demand = pd.read_csv(f'data{os.sep}demandData.csv')
    locations = pd.read_csv(f'data{os.sep}WarehouseLocations.csv')

    # merge demand and locations dataset
    joinedData = pd.merge(demand, locations, how='inner', left_on="Name", right_on="Store")

    #drop store column , same as name column
    joinedData.drop(columns=['Store','Long','Lat'], inplace=True)

    # tidy the data
    demandPivot = pd.melt(joinedData, id_vars=['Name','Location','Type'], var_name='Date', value_name='Demand')

    # convert date format from dd/mm/yyyy to dd-mm-yyyy
    demandPivot['Date'] = pd.to_datetime(demandPivot['Date'], format='%d/%m/%Y')

    #conver date format to day of the week
    demandPivot['dayOfWeek'] = demandPivot['Date'].dt.strftime('%a')

    return demandPivot

def visualise_data(data):
    """
    Creates a visualisation for a given dataframe

    Parameters
    -----------
    data : dataframe
        dataframe containing all the data for the operation
    """
    # get average demand for each store across the 4 weeks
    group_demand = data.groupby(['Type', 'Location', 'dayOfWeek'])['Demand'].sum().reset_index()
    group_demand['Demand'] = np.ceil(group_demand['Demand'] / 4)

    # sum the averages up for the different store type , Noel Leeming and Warehouse
    demand_estimate = group_demand.groupby(['Type', 'dayOfWeek'])['Demand'].mean().round().reset_index()

    sns.barplot(x='Type',y='Demand', data = demand_estimate, hue='dayOfWeek')
    plt.show()
