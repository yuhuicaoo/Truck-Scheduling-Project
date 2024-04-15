import pandas as pd
import numpy as np
import os

## Helper functions for part1 of project

# Constants
MAX_TIME_SECONDS = 14400
UNLOAD_RATE_SECONDS = 600

# durations dataframe
durations = pd.read_csv(os.path.join('data','WarehouseDurations.csv'), index_col="Unnamed: 0")

# starting distribution centers
south_only = ["Distribution South"]
south_and_north = ["Distribution South", "Distribution North"]

# dictionary that holds the subsets of stores
stores = {
    "subset1": [
        "Noel Leeming Albany",
        "The Warehouse Albany",
        "Noel Leeming Wairau Park",
        "The Warehouse Milford",
        "The Warehouse Glenfield Mall",
    ],
    "subset2": [
        "Noel Leeming Henderson",
        "Noel Leeming New Lynn",
        "The Warehouse Westgate",
        "The Warehouse WestCity",
        "The Warehouse New Lynn",
        "The Warehouse Lincoln Road",
    ],
    "subset3": [
        "The Warehouse St Lukes",
        "Noel Leeming St Lukes Mega",
        "The Warehouse Mt Roskill",
        "The Warehouse Royal Oak",
        "Noel Leeming Royal Oak",
        "The Warehouse Newmarket",
        "Noel Leeming Newmarket",
        "The Warehouse Atrium",
        "The Warehouse Lunn Avenue",
        "Noel Leeming Lunn Avenue",
        "Noel Leeming Penrose Clearance",
        "The Warehouse Sylvia Park",
        "Noel Leeming Sylvia Park",
        "The Warehouse Pakuranga",
    ],
    "subset4": [
        "The Warehouse Airport",
        "Noel Leeming Papatoetoe",
        "Noel Leeming Manukau Supa Centre",
        "The Warehouse Manukau",
        "The Warehouse Clendon",
        "The Warehouse Takanini",
        "Noel Leeming Papakura",
        "Noel Leeming Ormiston",
        "Noel Leeming Botany",
        "The Warehouse Botany Downs",
    ],
}

all_stores = (stores["subset1"] + stores["subset2"] + stores["subset3"] + stores["subset4"])

def map_demands_to_store(subset, weekday=True):
    '''
    Maps the estimated demands to each store

    Parameters
    ----------
    subset : list, array
        list that holds all the stores in a subset
    
    weekday : boolean
        defualt is True, condition for if we want to map the weekday or weekend demands to stores.
    '''
    noel_leeming_demand = 5 if weekday else 0
    other_store_demand = 7 if weekday else 3
    return {store: noel_leeming_demand if "Noel Leeming" in store else other_store_demand for store in subset}
    
def write_routes(routes, southOnly = True, optimal_cost=None, is_optimal=False, weekday=True):
    """
    Write routes / optimal routes to a txt file

    Parameters
    ----------
    routes : 2d list / array
        2d list that holds all the routes needed to be written

    optimal_cost : float / integer
        defualt is None, the optimal cost of the linear program
    
    is_optimal : Boolean
        True if writing optimal routes, False if writing generated routes
    
    weekday : Boolean
        True if routes are for weekday, False if for weekend
    """
    directory = "optimalRoutes" if is_optimal else "routes"
    file_prefix = 'south' if southOnly else 'both'
    file_name = f"{file_prefix}_weekday.txt" if weekday else f"{file_prefix}_saturday.txt"
    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w') as fp:
        if optimal_cost:
            fp.write(f"Optimal objective function,{optimal_cost}\n")
        lines = [",".join(route) for route in routes]
        fp.write("\n".join(lines))

def get_route_cost(stores,route,weekday = True, traffic = False):
    """
    Calculates the cost of a given route based on its travel time

    Parameters
    -----------
    stores : list
        a list of all the stores to map their demands
    route  : list
        a list of store names representing the route to be "costed"
    weekday : bool, optional
        determines if weekday demands are used (defualt is True). If false, weekend demands are used
    traffic : bool, optional
        determines if traffic is accounted for (defualt is True) in our travel durations . If false traffic is not accounted

    Returns:
    ---------
    route_cost : float
        the cost of the given route 
    """
    traffic_multiplier = [1,2] if weekday else [1,1.5]

    #get number of pallets and calculate unloading time
    num_pallets = sum(stores.get(store,0) for store in route)
    unloading_time = num_pallets * UNLOAD_RATE_SECONDS

    # calculate travel time
    if traffic:
        travel_time = sum(durations.loc[store_from][store_to] * np.random.choice(traffic_multiplier) for store_from, store_to in zip(route,route[1:]))
    else:
        travel_time = sum(durations.loc[store_from][store_to] for store_from, store_to in zip(route,route[1:]))

    time_seconds = travel_time + unloading_time

    # calculate the amount of seconds over max timeframe (4hours)
    overtime_seconds = max(0, time_seconds- MAX_TIME_SECONDS)

    # return cost for the route
    return ((time_seconds - overtime_seconds) * (175/3600)) + (overtime_seconds * (300/3600))