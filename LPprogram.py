from pulp import *
from helper import *
from route_generation import *


def generate_optimal_routes(routes, stores, weekday=True, southOnly= True,traffic = False, save = False):
    """
    Given a set of routes , return the optimised routes

    Parameters
    -----------
    routes : 2d list, array
        list / array that holds all feasible routes to be optimised
    stores : list , array
        list that holds every store in the problem
    durations : dictionary
        a dictionary that contains the durations for each store to another
    weekday : boolean
        defualt is True, checks if given data is for weekday or not

    Returns
    ---------
    optimal_routes : list
        holds the optimal routes
    """

    # filter to only Warehouse Stores if its a weekend (SATURDAY)
    if not weekday:
        stores = {store: demand for store, demand in stores.items() if store.startswith("The Warehouse")}
    # use index to represent the route names
    index = [i for i in range(len(routes))]

    # create the LP problem
    prob = LpProblem("TruckRouting", LpMinimize)

    # routes put into dictionary
    x = LpVariable.dicts("route", index, cat=LpBinary)

    # create objective function
    prob += lpSum([get_route_cost(stores, routes[i], traffic) * x[i] for i in index])

    # add truck availibiilty constraint
    prob += lpSum([x[i] for i in index]) <= 32

    # each store must be visisted once
    for store in stores:
        prob += lpSum([x[i] for i in index if store in routes[i]]) == 1

    # write problem data to a .lp file
    prob.writeLP("TruckRouting.lp")

    # solve the problem
    prob.solve(PULP_CBC_CMD(msg=False))

    # get the optimal routes and write it to a txt file
    optimal_routes = [routes[i] for i in index if x[i].value() == 1.0]
    if save:
        write_routes(
            optimal_routes,
            optimal_cost=value(prob.objective),
            is_optimal=True,
            weekday=weekday,
            southOnly= southOnly
        )
    return value(prob.objective), optimal_routes


# change south_only or south_and_north, change weekday from True or False
demands = map_demands_to_store(all_stores, weekday=False)
routes = generate_all_routes(stores, south_and_north, weekday=False, southOnly=False)
optimal_routes = generate_optimal_routes(routes, demands, weekday=False, southOnly=False, save=True, traffic=False)

