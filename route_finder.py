import networkx as nx
import pandas as pd


# --------------------------------------------------
# GET ALL STATIONS
# --------------------------------------------------
def get_all_stations(stations_df):
    if 'Station' in stations_df.columns:
        return sorted(stations_df['Station'].unique())
    elif 'Station_Name' in stations_df.columns:
        return sorted(stations_df['Station_Name'].unique())
    else:
        return sorted(stations_df.iloc[:, 0].unique())


# --------------------------------------------------
# CALCULATE FARE
# --------------------------------------------------
def calculate_fare(route, connections_df, stations_df):
    total_distance = 0.0

    if route is None or len(route) < 2:
        return 0, 0

    for i in range(len(route) - 1):
        row = connections_df[
            ((connections_df['Station1'] == route[i]) &
             (connections_df['Station2'] == route[i+1])) |
            ((connections_df['Station1'] == route[i+1]) &
             (connections_df['Station2'] == route[i]))
        ]

        if not row.empty:
            total_distance += float(row['Distance_km'].values[0])

    # Fare slabs
    if total_distance <= 2: fare = 11
    elif total_distance <= 4: fare = 21
    elif total_distance <= 6: fare = 32
    elif total_distance <= 8: fare = 42
    elif total_distance <= 10: fare = 53
    elif total_distance <= 15: fare = 63
    elif total_distance <= 20: fare = 74
    elif total_distance <= 25: fare = 84
    elif total_distance <= 30: fare = 90
    else: fare = 95

    return round(total_distance, 2), fare


# --------------------------------------------------
# CREATE GRAPH
# --------------------------------------------------
def create_metro_graph(stations_df, connections_df):
    G = nx.Graph()

    # Add nodes
    for _, row in stations_df.iterrows():
        G.add_node(
            row["Station"],
            line=row.get("Line", "Unknown"),
            id=row.get("Station_ID", None),
            lat=row.get("lat", None),
            lon=row.get("lon", None)
        )

    # Add edges (IMPORTANT FIX: use weight)
    for _, row in connections_df.iterrows():
        G.add_edge(
            row["Station1"],
            row["Station2"],
            weight=row["Distance_km"]
        )

    return G


# --------------------------------------------------
# FIND ROUTE
# --------------------------------------------------
def find_route(source, destination, stations_df, connections_df):
    G = create_metro_graph(stations_df, connections_df)

    if source not in G or destination not in G:
        return None, None

    try:
        path = nx.shortest_path(G, source, destination, weight="weight")

        lines_used = []
        current_line = None
        start_station = None

        for station in path:
            line = G.nodes[station].get("line")

            if current_line is None:
                current_line = line
                start_station = station
            elif line != current_line:
                lines_used.append((current_line, start_station, station))
                current_line = line
                start_station = station

        lines_used.append((current_line, start_station, path[-1]))

        return path, lines_used

    except nx.NetworkXNoPath:
        return None, None
    except Exception as e:
        print(f"Route error: {e}")
        return None, None


# --------------------------------------------------
# DETECT INTERCHANGES
# --------------------------------------------------
def detect_interchanges(route, stations_df):
    interchanges = []

    if not route or len(route) < 2:
        return interchanges

    current_line = None

    for i, station in enumerate(route):
        row = stations_df[stations_df['Station'] == station]

        if row.empty:
            continue

        line = row.iloc[0]['Line']

        if current_line is None:
            current_line = line
        elif line != current_line:
            interchanges.append({
                'station': station,
                'from_line': current_line,
                'to_line': line,
                'stop_number': i + 1
            })
            current_line = line

    return interchanges


# --------------------------------------------------
# LINE COLORS
# --------------------------------------------------
def get_line_color(line_name):
    return {
        'Purple': '#9b59b6',
        'Green': '#27ae60',
        'Yellow': '#f39c12'
    }.get(line_name, '#95a5a6')


# --------------------------------------------------
# ALTERNATIVE ROUTES
# --------------------------------------------------
def find_alternative_routes(source, destination, stations_df, connections_df, passenger_df=None):
    G = create_metro_graph(stations_df, connections_df)

    if source not in G or destination not in G:
        return None

    routes = {}

    try:
        # Shortest (fewest stops)
        shortest = nx.shortest_path(G, source, destination)
        d1, f1 = calculate_fare(shortest, connections_df, stations_df)

        routes['Shortest'] = {
            'path': shortest,
            'distance': d1,
            'fare': f1
        }

        # Fastest (distance)
        fastest = nx.shortest_path(G, source, destination, weight='weight')
        d2, f2 = calculate_fare(fastest, connections_df, stations_df)

        routes['Fastest'] = {
            'path': fastest,
            'distance': d2,
            'fare': f2
        }

        # Less crowded (simple fallback)
        routes['Less Crowded'] = routes['Shortest']

        return routes

    except:
        return None