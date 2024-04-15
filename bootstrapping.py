import matplotlib.pyplot as plt
import os
from visualisations import tidy_and_wrangle_data
from LPprogram import generate_optimal_routes
from route_generation import generate_routes
from helper import *
import numpy as np
from scipy import stats


data = tidy_and_wrangle_data()



def read_optimal_routes(southOnly=True, weekday=True):
    """ "
    Get the objective function and optimal routes of a given file

    Parameters
    -----------
    southOnly : bool
        boolean that determines if our starting distribution centre is south only if True, else south and north
    weekday : bool
        boolean that determines if routes are for weekday or not.

    Returns
    ----------
    objective function: float
        the cost of operation for this given set of optimal routes
    routes : list , array
        a list of all the optimal routes
    
    Notes
    --------
    file that data is read from is in the optimalRoutes file.
    """

    # create file path
    start = "south" if southOnly else "both"
    day = "weekday" if weekday else "saturday"
    filepath = os.path.join("optimalRoutes", f"{start}_{day}.txt")

    with open(filepath, "r") as fp:
        # get objective function line
        objective_function = fp.readline()
        # store all optimal routes in a array
        routes = [line.strip().split(",") for line in fp.readlines()]

    # get only the number from objective value
    objective_function = float(objective_function.strip().split(",")[1])

    return objective_function, routes

def map_demands(data, weekday =True):
    """
    generate random demands for each store

    Parameters
    -----------
    data : dataframe
        dataframe that holds all the information about the stores
    weekday : bool, optional
        defualt is True, decides whether we are considering weekday or weekend demands

    Returns
    ---------
    store_demand_dict : dict
        dictionary that contains the randomised demands to their respective stores.
    """

    # Create a filter to only select weekdays if weekend is True, else saturday
    filter_days = data[~data['dayOfWeek'].isin(['Sat','Sun'])] if weekday else data[data['dayOfWeek'] == 'Sat']


    # Create a dictionary with stores as the keys and the random demands as the values.
    store_demand_dict = {store_name: store_group['Demand'].sample(n=1).values[0] for store_name, store_group in filter_days.groupby('Name')}
    
    return store_demand_dict
        
def get_route_cost_boot(route, randomised_demands, weekday=True, traffic=False):
    """
    Get the cost of the route when randomised demands are applied

    Parameters
    ------------
    route : list, array
        A list of store representing the route.
    randomised_demands : dict
        A dictionary where keys are stores and values are the corresponding randomised pallet demands.
    weekday : bool, optional
        A flag indicating whether the route is on a weekday (True) or not (False). Defaults to True.
    traffic : bool, optional
        A flag indicating whether traffic conditions should be considered (True) or not (False). Defaults to False.

    Returns
    -------
    cost : float
        The calculated cost of the route after accounting for randomised demands , traffic and potential store removals.
    removed_stores : list
        A list of stores that were removed from the route to meet truck capacity constraints.
    route : list
        The modified route after potential store removals.
    """
    # holds stores removed from route
    removed_stores = []

    # if pallet of the route is above truck capacity
    while sum(randomised_demands.get(store, 0) for store in route) > 20:
        # remove the last store in the route
        removed_stores.append(route.pop(-2))

    # get the new cost of route
    cost = get_route_cost(randomised_demands, route, weekday=weekday, traffic=traffic)

    return cost, removed_stores, route


def bootstrapped_cost(mapped_demands, southOnly=True, weekday=True, traffic=False):
    """
    Calculate the bootstrapped operation cost and generates any routes needed to satisfy demand requirements

    Parameters
    ------------
    mapped_demands : dict
        A dictionary where keys are store identifiers and values are corresponding mapped pallet demands.
    southOnly : bool, optional
        A flag indicating whether to consider only southern distribution (True) or both south and north distributions (False). Defaults to True.
    weekday : bool, optional
        A flag indicating whether the operation is for  weekday (True) or not (False). Defaults to True.
    traffic : bool, optional
        A flag indicating whether traffic conditions should be considered (True) or not (False). Defaults to False.

    Returns
    -------
    operation_cost : float
        The calculated bootstrapped operation cost based on modified optimal routes and randomised demands and traffic.
    optimal_routes : list
        A list of  routes, considering demand adjustments and possible store removals.
    """

    distribution = south_only if southOnly else south_and_north
    operation_cost = 0
    all_removed_stores, optimal_routes = set(), []

    # get all the optimal routes from the .txt file
    _, routes = read_optimal_routes(southOnly, weekday)


    for route in routes:
        new_route_cost, removed_stores, modified_route = get_route_cost_boot(route, mapped_demands,weekday, traffic)
        # update operation cost, removed_stores and optimal_routes
        operation_cost += new_route_cost
        all_removed_stores.update(removed_stores)
        optimal_routes.append(modified_route)

    # check if there is any removed stores
    if all_removed_stores:
        removed_stores_dict = {
            store: demand
            for store, demand in mapped_demands.items()
            if store in all_removed_stores
        }

        # generate new optimal routes for the removed stores
        new_routes = generate_routes(removed_stores_dict, distribution, weekday)
        optimal_new_cost, optimal_new_routes = generate_optimal_routes(
            new_routes,
            removed_stores_dict,
            weekday=weekday,
            save=False,
            traffic=traffic,
        )

        # update operation cost, and routes
        operation_cost += optimal_new_cost
        optimal_routes.extend(optimal_new_routes)

    return operation_cost, optimal_routes


def plot_operation_cost(sample_size, southOnly=True, weekday=True, traffic=False):
    """
    Generate a  plot of bootstrapped simulation costs

    Parameters
    ----------
    sample_size : int
        The number of simulations to generate
    southOnly : bool, optional
        A flag indicating whether to consider only southern distribution (True) or both south and north distributions (False). Defaults to True.
    weekday : bool, optional
        A flag indicating whether the operation is for weekday (True) or not (False). Defaults to True.
    traffic : bool, optional
        A flag indicating whether traffic conditions should be considered (True) or not (False). Defaults to False.

    Returns
    -------
    operation_cost : list
        A list containing the bootstrapped operation costs

    Notes
    --------
    Generates and saes a plot for the bootstrapped simulation  cost
    """

    starting= "south" if southOnly else "both"
    day = "weekday" if weekday else "saturday"
    filepath = os.path.join("simulationResults", f"{starting}_{day}.png")

    # intialise list that contains all the operation cost
    operation_cost = []

    # get the operation cost for given sample size
    for _ in range(sample_size):
        # random_demands = get_random_demands(data, weekday)
        mapped_demands = map_demands(data, weekday)
        cost, _ = bootstrapped_cost(mapped_demands, southOnly, weekday, traffic)
        operation_cost.append(cost)


    objective_func, _ = read_optimal_routes(southOnly, weekday)

    plt.hist(operation_cost, bins=int((max(operation_cost) - min(operation_cost)) / 100), edgecolor='black', alpha=0.7) 
    plt.xlabel("Operation Cost, NZD")
    plt.ylabel("Count")
    plt.title(f"Simulated cost distribution for {day} with {starting} distribution(s) open")
    plt.axvline(x=round(objective_func, 1), color="r", linestyle="--", label="proposed cost")
    plt.legend()
    plt.savefig(filepath)
    plt.show()

    return operation_cost


bootstrap_wday_south = plot_operation_cost(1000, southOnly=True, weekday=True, traffic=True)
bootstrap_wday_both = plot_operation_cost(1000, southOnly=False, weekday=True, traffic=True)

bootstrap_sat_south = plot_operation_cost(1000, southOnly=True, weekday=False, traffic=True)
bootstrap_sat_both = plot_operation_cost(1000, southOnly=False, weekday=False, traffic=True)

# #maybe write t-test function that compares the mean simulated operation cost between south and south + north?
# maybe write a function that calculates the confidence interval?

def boostrap_summaries(cost1, cost2):
    t_statistic, p_value = stats.ttest_ind(cost1, cost2)
    ci_1 = stats.norm.interval(0.95, loc=np.mean(cost1), scale=stats.sem(cost1))
    ci_2 = stats.norm.interval(0.95, loc=np.mean(cost2), scale=stats.sem(cost2))

    return ci_1, ci_2, t_statistic, p_value

print(boostrap_summaries(bootstrap_wday_south,bootstrap_wday_both))
print(boostrap_summaries(bootstrap_sat_south,bootstrap_sat_both))

