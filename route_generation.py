import pandas as pd
import numpy as np
import itertools as it
from helper import *
from pulp import *


def generate_routes(subset, distribution, weekday=True):
    """
    Generate a set of routes for a given subset

    Parameters
    ----------
    subset : list , array-like
        holds the stores in a given subset
    route : list
        list of distribution centres we can start at (e.g Southern or Northern)
    weekday : boolean
        defualt is True, condition for if we want routes for weekday or weekend

    Returns
    --------
    feasible_routes : 2d array
        a list of all feasible routes possible with demand under truck capcity (20)
    """

    # Map demands to stores
    subset = map_demands_to_store(subset, weekday)

    # intialise array to store all feasible routes
    feasible_routes = []

    def add_feasible_routes(current_route, current_pallets):
        for store in subset:
            # add store to route, if its not already in and if new demand is less than truck capacity (20)
            if store not in current_route and 0 < subset[store] <= 20 - current_pallets:

                # new feasible route is made
                new_route = current_route + [store]

                feasible_routes.append(tuple(new_route + [current_route[0]]))

                # recursively call function again to see what new stores we can add to current route
                add_feasible_routes(new_route, current_pallets + subset[store])

    # get the routes for the different starting distribution centres
    for start in distribution:
        add_feasible_routes([start], 0)

    return feasible_routes


def generate_all_routes(subsets,start, weekday = True, southOnly = True):
    """
    Generates and stores all feasible routes for a given subset of stores

    Parameters
    ----------
    subsets : dict
        a dictionary that contains all the subset of stores
    start   : list / array
        a list that holds the different distribution centres each route starts at
    weekday : boolean , optional
        determines if weekday demands are used (defualt is True). If false, use weekend demands.
    """
    all_feasible_routes = []
    
    # get all stores in the subsets
    for _, stores in subsets.items():
        # get all feasible routes
        feasible_routes = generate_routes(stores, start, weekday)

        # write feasible routes to .txt file
        all_feasible_routes.extend(feasible_routes)
    write_routes(all_feasible_routes,is_optimal=False, weekday=weekday, southOnly=southOnly)
    return all_feasible_routes