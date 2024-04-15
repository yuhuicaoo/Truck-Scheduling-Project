import openrouteservice as ors
import pandas as pd
import numpy as np
import folium
import os

# open route service key
ORSkey = "5b3ce3597851110001cf6248d6aa623b1bd9473ab13dbd68d775d0d5"
# avaiable colors for the routes
available_colors = [
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "darkred",
    "lightred",
    "darkblue",
    "darkgreen",
    "cadetblue",
    "darkpurple",
    "pink",
    "gray",
    "black",
    "lightgray",
]


# read datafiles
locations = pd.read_csv(f"data{os.sep}WarehouseLocations.csv")


def map_optimal_routes(locations, weekday=True, southOnly = True):
    """
    Creates a map to visulise our proposed trucking routes

    Parameters
    -----------
    locations : dataframe
        dataframe of all the store locations used in the project / operation
    weekday : bool , optional
        A flag indicating whether we visulise weekday routes or weekend, defualt is True
    southOnly : bool , optional
        A flag indicating wheter we visualise routes starting at only south distribution (True) or 
        south and north distributions (False), defualt is True
    """

    day = "weekday" if weekday else "saturday"
    distributions = "south" if southOnly else "both"

    coords = locations[["Long", "Lat"]]  # Mapping packages work with Long, Lat arrays
    coords = coords.to_numpy().tolist()  # Make the arrays into a list of lists.

    # Folium, however, requires Lat, Long arrays - so a reversal is needed.
    # coords[0] is the warehouse

    m = folium.Map(location=list(reversed(coords[2])), zoom_start=10)

    folium.Marker(
        list(reversed(coords[0])),
        popup=locations.Store[0],
        icon=folium.Icon(color="black"),
    ).add_to(m)

    for i in range(1, len(coords)):
        if locations.Type[i] == "The Warehouse":
            iconCol = "red"
        elif locations.Type[i] == "Noel Leeming":
            iconCol = "orange"
        elif locations.Type[i] == "Distribution":
            iconCol = "black"
        folium.Marker(
            list(reversed(coords[i])),
            popup=locations.Store[i],
            icon=folium.Icon(color=iconCol),
        ).add_to(m)

    client = ors.Client(key=ORSkey)

    # read optimal routes txt files
    with open(f"optimalRoutes{os.sep}{distributions + '_' + day}.txt", "r") as fp:
        # ignore objective function
        _ = fp.readline()
        routes = fp.readlines()
    
    for i, current_route in enumerate(routes):
        current_route = current_route.strip().split(",")

        # get the index in the dataframe for each store in route from
        route_indices = [
            locations[locations["Store"] == store].index[0] for store in current_route
        ]

        # get the coords for each route
        route_coords = [coords[i] for i in route_indices]

        route = client.directions(
            coordinates=route_coords,
            profile="driving-hgv",
            format="geojson",
            validate=False,
        )

        folium.PolyLine(
            color=available_colors[i],
            locations=[
                list(reversed(coord))
                for coord in route["features"][0]["geometry"]["coordinates"]
            ],
        ).add_to(m)

    m.save(f"mappedRoutes{os.sep}{day}_{distributions}.html")


map_optimal_routes(locations, weekday=False, southOnly= True)
