import pandas as pd
import numpy as np
import os
from pathlib import Path

# Get the directory where this script is located (works for both local and Streamlit Cloud)
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def _normalize_coordinates(df):
    """
    Normalize latitude/longitude columns to support multiple naming conventions.
    Ensures 'Latitude', 'Longitude', 'lat', 'lon' all exist and map correctly.
    """
    # Rename to standardized names if they exist in other formats
    rename_map = {}
    
    # Handle latitude variations
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ['latitude', 'lat'] and col != 'Latitude':
            rename_map[col] = 'Latitude'
            break
    
    # Handle longitude variations
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ['longitude', 'lon', 'lng'] and col != 'Longitude':
            rename_map[col] = 'Longitude'
            break
    
    # Apply renames
    if rename_map:
        df = df.rename(columns=rename_map)
    
    # Create aliases for backward compatibility
    if 'Latitude' in df.columns and 'lat' not in df.columns:
        df['lat'] = df['Latitude']
    if 'Longitude' in df.columns and 'lon' not in df.columns:
        df['lon'] = df['Longitude']
    
    return df

def load_station_data():
    """
    Returns a DataFrame with Bengaluru Metro station information using accurate GPS coordinates.
    Loads from CSV file if available, otherwise generates data.
    Columns: Station_ID, Station_Name, Line, Latitude, Longitude, Traffic
    Also includes: Station, lat, lon (for backward compatibility)
    """
    csv_path = DATA_DIR / "bengaluru_metro_stations.csv"
    
    try:
        # Try to load from CSV with accurate coordinates
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            
            # Normalize coordinate columns
            df = _normalize_coordinates(df)
            
            # Ensure required columns exist
            if len(df) > 0 and 'Latitude' in df.columns and 'Longitude' in df.columns:
                # Clean up Line names (remove "Line" suffix if present for consistency)
                if 'Line' in df.columns:
                    df['Line'] = df['Line'].str.replace(' Line', '', regex=False).str.strip()
                
                # Add Station column if not present
                if 'Station' not in df.columns and 'Station_Name' in df.columns:
                    df['Station'] = df['Station_Name']
                elif 'Station' not in df.columns:
                    # Fallback to first available column as station name
                    df['Station'] = df.iloc[:, 1]
                
                # Ensure Station_Name exists
                if 'Station_Name' not in df.columns and 'Station' in df.columns:
                    df['Station_Name'] = df['Station']
                
                # Add Traffic column if not present (synthetic)
                if 'Traffic' not in df.columns:
                    np.random.seed(42)
                    base_traffic = np.random.randint(500000, 2000000, size=len(df))
                    line_multipliers = {'Purple': 1.2, 'Green': 1.0, 'Yellow': 0.6}
                    df['Traffic'] = [
                        int(base * line_multipliers.get(line, 1.0))
                        for base, line in zip(base_traffic, df.get('Line', ['Purple']*len(df)))
                    ]
                
                # Ensure Station_ID exists
                if 'Station_ID' not in df.columns:
                    df['Station_ID'] = range(1, len(df) + 1)
                
                # Select and return required columns
                required_cols = ['Station_ID', 'Station_Name', 'Line', 'Latitude', 'Longitude', 'Traffic', 'lat', 'lon', 'Station']
                available_cols = [col for col in required_cols if col in df.columns]
                return df[available_cols].reset_index(drop=True)
        
    except Exception as e:
        print(f"Warning: Could not load station data from CSV ({csv_path}): {e}. Using generated data.")
    
    # Fallback: Generate data as before
    stations = [
        # ========== PURPLE LINE (East-West) ========== 37 stations
        'Challaghatta', 'Kengeri', 'Kengeri Bus Terminal', 'Pattanagere',
        'Jnanabharathi', 'Rajarajeshwari Nagar', 'Nayandahalli', 'Mysuru Road',
        'Deepanjali Nagar', 'Attiguppe', 'Vijayanagar', 'Hosahalli',
        'Magadi Road', 'City Railway Station', 'Majestic', 'Sir M. Visvesvaraya',
        'Vidhana Soudha', 'Cubbon Park', 'Mahatma Gandhi Road', 'Trinity',
        'Halasuru', 'Indiranagar', 'Swami Vivekananda Road', 'Baiyappanahalli',
        'Benniganahalli', 'Krishnarajapura', 'Mahadevapura', 'Garudacharpalya',
        'Hoodi', 'Seetharampalya', 'Kundalahalli', 'Nallurhalli',
        'Sadaramangala', 'Pattandur Agrahara', 'Kadugodi Tree Park', 'Hopefarm',
        'Whitefield (Kadugodi)',
        # ========== GREEN LINE (North-South) ========== 32 stations
        'Madavara', 'Chikkabidarakallu', 'Manjunathanagar', 'Nagasandra',
        'Dasarahalli', 'Jalahalli', 'Peenya Industry', 'Peenya',
        'Goraguntepalya', 'Yeshwanthpur', 'Sandal Soap Factory', 'Mahalakshmi',
        'Rajajinagar', 'Kuvempu Road', 'Srirampura', 'Sampige Road',
        'Majestic', 'Chickpete', 'Krishna Rajendra Market', 'National College',
        'Lalbagh', 'South End Circle', 'Jayanagar', 'Rashtreeya Vidyalaya Road',
        'Banashankari', 'Jaya Prakash Nagar', 'Yelachenahalli', 'Konanakunte Cross',
        'Doddakallasandra', 'Vajarahalli', 'Thalaghattapura', 'Silk Institute',
        # ========== YELLOW LINE (RV Road - Bommasandra) ========== 14 stations
        'Ragigudda', 'Jayadeva Hospital', 'BTM Layout', 'Central Silk Board',
        'Bommanahalli', 'Hongasandra', 'Kudlu Gate', 'Singasandra', 'Hosa Road',
        'Beratena Agrahara', 'Electronic City', 'Infosys Foundation Konappana Agrahara',
        'Huskur Road', 'Bommasandra'
    ]
    
    lines = ['Purple']*37 + ['Green']*32 + ['Yellow']*14
    
    # Generate realistic coordinates for Bengaluru
    np.random.seed(42)
    n = len(stations)
    base_lat, base_lon = 12.97, 77.59
    
    lats = []
    lons = []
    purple_count = 0
    green_count = 0
    yellow_count = 0
    
    for i, line in enumerate(lines):
        if line == 'Purple':
            # Purple Line: East-West (left to right)
            lats.append(base_lat + np.random.uniform(-0.01, 0.01))
            lons.append(base_lon - 0.15 + purple_count * 0.008)
            purple_count += 1
        elif line == 'Green':
            # Green Line: North-South (top to bottom)
            lats.append(base_lat + 0.15 - green_count * 0.01)
            lons.append(base_lon - 0.05 + np.random.uniform(-0.01, 0.01))
            green_count += 1
        else:  # Yellow
            # Yellow Line: Diagonal (bottom-right area)
            lats.append(base_lat - 0.1 + yellow_count * 0.012)
            lons.append(base_lon + 0.12 + yellow_count * 0.006)
            yellow_count += 1
    
    df = pd.DataFrame({
        'Station': stations,
        'Line': lines,
        'lat': lats,
        'lon': lons,
        'Latitude': lats,
        'Longitude': lons
    })
    
    df['Station_ID'] = df.index + 1
    df['Station_Name'] = df['Station']
    
    # Add synthetic Traffic column (annual passengers per station)
    base_traffic = np.random.randint(500000, 2000000, size=n)
    line_multipliers = {'Purple': 1.2, 'Green': 1.0, 'Yellow': 0.6}
    df['Traffic'] = [
        int(base * line_multipliers.get(line, 1.0))
        for base, line in zip(base_traffic, df['Line'])
    ]
    
    return df


def load_connection_data():
    """
    Returns a DataFrame with station connections and distances.
    Includes Station1_ID and Station2_ID for route_finder compatibility.
    """
    stations = load_station_data()
    connections = []
    
    def get_station_id(station_name):
        """Safely get station ID, handling name variations."""
        try:
            # Try exact match first
            result = stations[stations['Station'] == station_name]['Station_ID']
            if len(result) > 0:
                return result.iloc[0]
            
            # Try Station_Name column
            result = stations[stations['Station_Name'] == station_name]['Station_ID']
            if len(result) > 0:
                return result.iloc[0]
            
            # Fallback: try case-insensitive match
            result = stations[stations['Station'].str.lower() == station_name.lower()]['Station_ID']
            if len(result) > 0:
                return result.iloc[0]
            
            # If still not found, return None
            return None
        except Exception as e:
            print(f"Error finding station {station_name}: {e}")
            return None
    
    def add_connection(s1, s2, dist):
        """Add connection only if both stations exist."""
        id1 = get_station_id(s1)
        id2 = get_station_id(s2)
        
        # Only add connection if both stations were found
        if id1 is not None and id2 is not None:
            connections.append({
                'Station1': s1,
                'Station2': s2,
                'Distance_km': dist,
                'Station1_ID': int(id1),
                'Station2_ID': int(id2)
            })
            connections.append({
                'Station1': s2,
                'Station2': s1,
                'Distance_km': dist,
                'Station1_ID': int(id2),
                'Station2_ID': int(id1)
            })
        else:
            print(f"Warning: Could not create connection between {s1} and {s2} - station not found")
    
    # Purple Line sequential connections
    purple_stations = stations[stations['Line'] == 'Purple']['Station'].tolist()
    for i in range(len(purple_stations)-1):
        add_connection(purple_stations[i], purple_stations[i+1], 1.2 + np.random.uniform(-0.2, 0.3))
    
    # Green Line sequential connections
    green_stations = stations[stations['Line'] == 'Green']['Station'].tolist()
    for i in range(len(green_stations)-1):
        add_connection(green_stations[i], green_stations[i+1], 1.0 + np.random.uniform(-0.1, 0.4))
    
    # Yellow Line sequential connections
    yellow_stations = stations[stations['Line'] == 'Yellow']['Station'].tolist()
    for i in range(len(yellow_stations)-1):
        add_connection(yellow_stations[i], yellow_stations[i+1], 1.1 + np.random.uniform(-0.2, 0.3))
    
    # Add inter-line interchange connections
    # Purple-Green Interchange at Majestic
    purple_majestic = stations[(stations['Station'] == 'Majestic') & (stations['Line'] == 'Purple')]
    green_majestic = stations[(stations['Station'] == 'Majestic') & (stations['Line'] == 'Green')]
    if len(purple_majestic) > 0 and len(green_majestic) > 0:
        add_connection('Majestic', 'Majestic', 0.05)  # Transfer time
    
    # Green-Yellow Interchange at RV Road / RV Road Junction
    green_rv = stations[(stations['Station'] == 'RV Road') & (stations['Line'] == 'Green')]
    yellow_rv = stations[(stations['Station'] == 'RV Road Junction') & (stations['Line'] == 'Yellow')]
    if len(green_rv) > 0 and len(yellow_rv) > 0:
        add_connection('RV Road', 'RV Road Junction', 0.05)  # Transfer time
    
    # Purple-Green Interchange at KSR City Railway Station / Chickpete area
    # Check for other potential interchanges
    try:
        ksr = stations[stations['Station'] == 'KSR City Railway Station']
        chickpete = stations[stations['Station'] == 'Chickpete']
        if len(ksr) > 0 and len(chickpete) > 0:
            add_connection('KSR City Railway Station', 'Chickpete', 0.1)
    except:
        pass
    
    # Return empty dataframe if no connections found
    if not connections:
        print("Warning: No connections created. Returning minimal connection data.")
        return pd.DataFrame(columns=['Station1', 'Station2', 'Distance_km', 'Station1_ID', 'Station2_ID'])
    
    return pd.DataFrame(connections)


def load_passenger_data():
    """
    Returns a DataFrame with monthly passenger data for Purple, Green, and Yellow lines.
    Years: 2019-2026. Yellow line data starts from 2022.
    """
    np.random.seed(42)
    years = range(2019, 2027)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    data = []
    base_purple = 600000
    base_green = 400000
    base_yellow = 150000
    growth_rate = 1.08
    
    for year_idx, year in enumerate(years):
        for month in months:
            seasonal = 1.0
            if month in ['May', 'Jun']:
                seasonal = 0.85
            elif month in ['Dec']:
                seasonal = 1.2
            elif month in ['Jul', 'Aug']:
                seasonal = 0.9
            
            noise_p = np.random.uniform(0.95, 1.05)
            noise_g = np.random.uniform(0.95, 1.05)
            noise_y = np.random.uniform(0.90, 1.10)
            
            # Yellow line opened partially in 2021, fully in 2022
            yellow_factor = 0.0
            if year >= 2022:
                yellow_factor = 1.0
            elif year == 2021:
                yellow_factor = 0.3
            
            purple_pass = int(base_purple * (growth_rate ** year_idx) * seasonal * noise_p)
            green_pass = int(base_green * (growth_rate ** year_idx) * seasonal * noise_g)
            yellow_pass = int(base_yellow * (growth_rate ** max(0, year_idx-2)) * seasonal * noise_y * yellow_factor)
            total = purple_pass + green_pass + yellow_pass
            
            data.append({
                'Year': year,
                'Month': month,
                'Purple_Line_Passengers': purple_pass,
                'Green_Line_Passengers': green_pass,
                'Yellow_Line_Passengers': yellow_pass,
                'Passengers': total
            })
    
    return pd.DataFrame(data)


def get_all_stations(stations_df=None):
    """Return sorted list of all station names."""
    if stations_df is None:
        stations_df = load_station_data()
    if 'Station' in stations_df.columns:
        station_col = 'Station'
    elif 'Station_Name' in stations_df.columns:
        station_col = 'Station_Name'
    else:
        station_col = stations_df.columns[0]
    return sorted(stations_df[station_col].unique().tolist())


def load_hourly_breakdown():
    """
    Returns a DataFrame with hourly passenger breakdown by station, line, and year.
    Used for crowding heatmaps and timeline charts.
    """
    np.random.seed(42)
    stations_df = load_station_data()
    passenger_df = load_passenger_data()
    
    hours = list(range(6, 23))  # 6 AM to 10 PM
    data = []
    
    hourly_weights = {}
    for hour in hours:
        if 7 <= hour <= 9:
            hourly_weights[hour] = 2.5  # morning peak
        elif 17 <= hour <= 19:
            hourly_weights[hour] = 3.0  # evening peak
        elif 10 <= hour <= 16:
            hourly_weights[hour] = 1.2  # daytime
        else:
            hourly_weights[hour] = 0.6  # early/late

    total_hourly_weight = sum(hourly_weights.values())
    total_station_traffic = max(stations_df['Traffic'].sum(), 1)
    yearly_totals = passenger_df.groupby('Year')['Passengers'].sum().to_dict()

    for year, yearly_total in yearly_totals.items():
        daily_network_total = yearly_total / 365

        for _, station_row in stations_df.iterrows():
            station = station_row['Station']
            line = station_row['Line']
            station_share = station_row['Traffic'] / total_station_traffic
            station_daily_total = daily_network_total * station_share
            
            for hour in hours:
                base_hourly = station_daily_total * (hourly_weights[hour] / total_hourly_weight)
                passengers = int(base_hourly * np.random.uniform(0.85, 1.15))
                
                data.append({
                    'Year': year,
                    'Station': station,
                    'Line': line,
                    'Hour': hour,
                    'Passengers': max(passengers, 10)
                })
    
    return pd.DataFrame(data)


def get_hourly_traffic_for_station(station, year, hourly_df):
    """
    Get hourly traffic pattern for a specific station and year.
    """
    if hourly_df is None:
        return None
    
    station_data = hourly_df[hourly_df['Station'] == station]
    if 'Year' in hourly_df.columns:
        station_data = station_data[station_data['Year'] == year]
    if len(station_data) == 0:
        return None
    
    hourly_agg = station_data.groupby('Hour')['Passengers'].sum().reset_index()
    return hourly_agg


def get_lat_lon(row):
    """
    Safely extract latitude and longitude from a DataFrame row.
    Handles multiple naming conventions: Latitude/Longitude, lat/lon, etc.
    
    Args:
        row: pandas Series (single row from DataFrame)
    
    Returns:
        tuple: (latitude, longitude) or (None, None) if not found
    """
    # Try standard names first
    lat = None
    lon = None
    
    # Latitude variations
    for col in ['Latitude', 'lat', 'LAT', 'latitude']:
        if col in row.index:
            lat = row[col]
            if pd.notna(lat):
                break
    
    # Longitude variations  
    for col in ['Longitude', 'lon', 'LON', 'longitude', 'lng', 'LNG']:
        if col in row.index:
            lon = row[col]
            if pd.notna(lon):
                break
    
    return lat, lon

