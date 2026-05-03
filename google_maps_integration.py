"""
Google Maps Integration for Bengaluru Metro Tracker
Provides street view, directions, and interactive map features
"""

import streamlit as st
import folium
from folium import Marker, Icon, PolyLine, CircleMarker, LayerControl, TileLayer
import pandas as pd
import numpy as np
from metro_data import get_lat_lon


def create_comprehensive_metro_network_map(stations_df):
    """
    Create a comprehensive Bengaluru Metro network map with all lines and stations.
    Shows all three metro lines with color-coding and interactive markers.
    
    Args:
        stations_df: DataFrame with Station, Line, Latitude, Longitude
    
    Returns:
        folium.Map object with full metro network visualization
    """
    try:
        # Define accurate color mapping for Bengaluru Metro lines
        line_colors = {
            'Purple Line': '#9b59b6',
            'Purple': '#9b59b6',
            'Green Line': '#27ae60',
            'Green': '#27ae60',
            'Yellow Line': '#f39c12',
            'Yellow': '#f39c12',
        }
        
        line_icons = {
            'Purple': {'icon': 'circle', 'prefix': 'fa', 'color': 'purple'},
            'Green': {'icon': 'circle', 'prefix': 'fa', 'color': 'green'},
            'Yellow': {'icon': 'circle', 'prefix': 'fa', 'color': 'orange'},
        }
        
        # Calculate map center from all stations - handle multiple naming conventions
        lats = []
        lons = []
        for _, station in stations_df.iterrows():
            lat, lon = get_lat_lon(station)
            if lat is not None and lon is not None:
                lats.append(lat)
                lons.append(lon)
        
        if not lats or not lons:
            # Fallback to a default location for Bengaluru
            center_lat, center_lon = 12.97, 77.59
        else:
            center_lat = np.mean(lats)
            center_lon = np.mean(lons)
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles=None,
            prefer_canvas=True
        )
        
        # Add multiple tile layers (Google Maps latest versions)
        # OpenStreetMap (default)
        TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            show=True,
            control=True
        ).add_to(m)
        
        # Google Maps Street View
        TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps',
            show=False,
            control=True,
            overlay=False
        ).add_to(m)
        
        # Google Maps Satellite View
        TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Satellite',
            show=False,
            control=True,
            overlay=False
        ).add_to(m)
        
        # Google Maps Hybrid View (satellite + labels)
        TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Hybrid',
            show=False,
            control=True,
            overlay=False
        ).add_to(m)
        
        # Esri Street Map
        TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri',
            name='Esri Street Map',
            show=False,
            control=True
        ).add_to(m)
        
        # Esri Satellite View
        TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri',
            name='Esri Satellite',
            show=False,
            control=True
        ).add_to(m)
        
        # CartoDB Positron (light map)
        TileLayer(
            tiles='https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
            attr='&copy; OpenStreetMap &copy; CartoDB',
            name='CartoDB Light',
            show=False,
            control=True
        ).add_to(m)
        
        # CartoDB Voyager (detailed map)
        TileLayer(
            tiles='https://cartodb-basemaps-a.global.ssl.fastly.net/rastered_voyager/{z}/{x}/{y}.png',
            attr='&copy; OpenStreetMap &copy; CartoDB',
            name='CartoDB Voyager',
            show=False,
            control=True
        ).add_to(m)
        
        # Group stations by line
        for line in ['Purple', 'Green', 'Yellow']:
            line_stations = stations_df[
                (stations_df['Line'] == line) | 
                (stations_df['Line'] == f'{line} Line')
            ].copy()
            
            if line_stations.empty:
                continue
            
            # Get line color
            color = line_colors.get(line, '#95a5a6')
            
            # Draw line connection between sequential stations - handle multiple naming conventions
            coords = []
            for _, station in line_stations.iterrows():
                lat, lon = get_lat_lon(station)
                if lat is not None and lon is not None:
                    coords.append([lat, lon])
            
            if len(coords) > 1:
                PolyLine(
                    coords,
                    color=color,
                    weight=4,
                    opacity=0.8,
                    dash_array='',
                    popup=f'{line} Line'
                ).add_to(m)
            
            # Add markers for each station with small labels
            for idx, (_, station) in enumerate(line_stations.iterrows()):
                try:
                    station_name = station.get('Station_Name', station.get('Station', 'Unknown'))
                    lat, lon = get_lat_lon(station)
                    
                    # Skip if coordinates not found
                    if lat is None or lon is None:
                        continue
                    
                    # Create HTML tooltip with small font
                    popup_html = f"""
                    <div style="font-family: Arial, sans-serif; width: 180px;">
                        <b style="font-size: 11px; color: {color};">{line} Line</b><br>
                        <b style="font-size: 12px;">{station_name}</b><br>
                        <span style="font-size: 9px; color: #666;">
                            Lat: {lat:.4f}<br>
                            Lon: {lon:.4f}
                        </span>
                    </div>
                    """
                    
                    # Add colored circle marker with station icon
                    CircleMarker(
                        location=[lat, lon],
                        radius=4,
                        popup=folium.Popup(popup_html, max_width=200),
                        tooltip=f"<span style='font-size: 10px;'>{station_name}</span>",
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.8,
                        weight=2,
                        opacity=1
                    ).add_to(m)
                    
                    # Add small text label near marker (for stations with fewer overlaps)
                    if idx % 2 == 0:  # Show every other label to reduce clutter
                        label_html = f"""
                        <div style="font-size: 8px; color: {color}; font-weight: bold; 
                                    background: white; padding: 1px 3px; border-radius: 2px;
                                    opacity: 0.85; white-space: nowrap;">
                            {station_name.split()[0]}
                        </div>
                        """
                        folium.Marker(
                            location=[lat, lon],
                            icon=folium.DivIcon(html=label_html),
                            popup=folium.Popup(popup_html, max_width=200),
                        ).add_to(m)
                        
                except Exception as e:
                    continue
        
        # Add layer control
        LayerControl(collapsed=False, position='topright').add_to(m)
        
        # Add custom CSS for better styling
        m.get_root().html.add_child(folium.Element("""
            <style>
                .leaflet-popup-content { font-family: Arial, sans-serif; }
                .leaflet-tooltip { font-size: 10px; }
            </style>
        """))
        
        return m
        
    except Exception as e:
        print(f"Error creating metro network map: {e}")
        return None


def create_interactive_route_map(route, stations_df, connections_df):
    """
    Create an interactive route map with accurate Google Maps coordinates.
    
    Args:
        route: List of station names in route order
        stations_df: DataFrame with station information
        connections_df: DataFrame with connections
    
    Returns:
        folium.Map object showing the route
    """
    try:
        line_colors = {
            'Purple': '#9b59b6',
            'Green': '#27ae60',
            'Yellow': '#f39c12',
        }
        
        # Get coordinates for route stations
        route_coords = []
        route_info = []
        
        for i, station_name in enumerate(route):
            station_row = stations_df[
                (stations_df['Station'] == station_name) |
                (stations_df['Station_Name'] == station_name)
            ]
            
            if not station_row.empty:
                row = station_row.iloc[0]
                lat, lon = get_lat_lon(row)
                
                # Skip if coordinates not found
                if lat is None or lon is None:
                    continue
                    
                line = row.get('Line', 'Unknown')
                
                # Clean line name
                if 'Line' in str(line):
                    line = line.replace(' Line', '')
                
                route_coords.append([lat, lon])
                route_info.append({
                    'station': station_name,
                    'line': line,
                    'lat': lat,
                    'lon': lon,
                    'stop': i + 1
                })
        
        if not route_coords:
            return None
        
        # Calculate center and create map
        center_lat = np.mean([c[0] for c in route_coords])
        center_lon = np.mean([c[1] for c in route_coords])
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles=None,
            prefer_canvas=True
        )
        
        # Add multiple tile layers (Google Maps latest versions)
        TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            show=True,
            control=True
        ).add_to(m)
        
        TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps',
            show=False,
            control=True
        ).add_to(m)
        
        TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Satellite',
            show=False,
            control=True
        ).add_to(m)
        
        TileLayer(
            tiles='https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
            attr='&copy; CartoDB',
            name='CartoDB Light',
            show=False,
            control=True
        ).add_to(m)
        
        # Draw route line
        PolyLine(
            route_coords,
            color='#4a90e2',
            weight=4,
            opacity=0.9,
            popup='Route Path'
        ).add_to(m)
        
        # Add start and end markers
        for i, info in enumerate(route_info):
            if i == 0:
                # Start marker
                icon = Icon(color='green', icon='play', prefix='fa')
                popup_text = f"<b style='color: green; font-size: 11px;'>START</b><br><b style='font-size: 12px;'>{info['station']}</b><br><span style='font-size: 10px;'>{info['line']}</span>"
            elif i == len(route_info) - 1:
                # End marker
                icon = Icon(color='red', icon='stop', prefix='fa')
                popup_text = f"<b style='color: red; font-size: 11px;'>END</b><br><b style='font-size: 12px;'>{info['station']}</b><br><span style='font-size: 10px;'>{info['line']}</span>"
            else:
                # Intermediate marker
                icon = Icon(color='blue', icon='circle', prefix='fa')
                popup_text = f"<b style='font-size: 11px;'>Stop {info['stop']}</b><br><b style='font-size: 12px;'>{info['station']}</b><br><span style='font-size: 10px;'>{info['line']}</span>"
            
            Marker(
                location=[info['lat'], info['lon']],
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=f"<span style='font-size: 10px;'>{info['station']}</span>",
                icon=icon
            ).add_to(m)
        
        # Fit bounds
        if len(route_coords) > 1:
            lats = [c[0] for c in route_coords]
            lons = [c[1] for c in route_coords]
            m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
        
        # Add layer control
        LayerControl(collapsed=False, position='topright').add_to(m)
        
        return m
        
    except Exception as e:
        print(f"Error creating interactive route map: {e}")
        return None


def create_line_specific_map(line_name, stations_df):
    """
    Create a map showing only stations on a specific metro line.
    
    Args:
        line_name: Name of the metro line ('Purple', 'Green', or 'Yellow')
        stations_df: DataFrame with station information
    
    Returns:
        folium.Map object showing the line
    """
    try:
        line_colors = {
            'Purple': '#9b59b6',
            'Green': '#27ae60',
            'Yellow': '#f39c12',
        }
        
        # Filter stations for the line
        line_df = stations_df[
            (stations_df['Line'] == line_name) |
            (stations_df['Line'] == f'{line_name} Line')
        ].copy()
        
        if line_df.empty:
            return None
        
        color = line_colors.get(line_name, '#95a5a6')
        
        # Calculate center - use helper function to get lat/lon
        lats = []
        lons = []
        for _, station in line_df.iterrows():
            lat, lon = get_lat_lon(station)
            if lat is not None and lon is not None:
                lats.append(lat)
                lons.append(lon)
        
        if not lats or not lons:
            return None
            
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles=None,
            prefer_canvas=True
        )
        
        # Add multiple tile layers (Google Maps latest versions)
        TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            show=True,
            control=True
        ).add_to(m)
        
        TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Maps',
            show=False,
            control=True
        ).add_to(m)
        
        TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Satellite',
            show=False,
            control=True
        ).add_to(m)
        
        TileLayer(
            tiles='https://cartodb-basemaps-a.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
            attr='&copy; CartoDB',
            name='CartoDB Light',
            show=False,
            control=True
        ).add_to(m)
        
        # Draw line - handle multiple naming conventions
        coords = []
        for _, station in line_df.iterrows():
            lat, lon = get_lat_lon(station)
            if lat is not None and lon is not None:
                coords.append([lat, lon])
        
        if len(coords) > 1:
            PolyLine(
                coords,
                color=color,
                weight=5,
                opacity=0.9,
                popup=f'{line_name} Line'
            ).add_to(m)
        
        # Add stations with small labels
        for idx, (_, station) in enumerate(line_df.iterrows()):
            station_name = station.get('Station_Name', station.get('Station', 'Unknown'))
            lat, lon = get_lat_lon(station)
            
            # Skip if coordinates not found
            if lat is None or lon is None:
                continue
            
            # Main marker
            CircleMarker(
                location=[lat, lon],
                radius=5,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.8,
                weight=2,
                popup=folium.Popup(
                    f"<b style='font-size: 12px;'>{station_name}</b>",
                    max_width=200
                ),
                tooltip=f"<span style='font-size: 10px;'>{station_name}</span>"
            ).add_to(m)
            
            # Label marker with small font
            if idx % 3 == 0:  # Show every 3rd label
                label_html = f"""
                <div style="font-size: 8px; color: {color}; font-weight: bold;
                           background: white; padding: 2px 4px; border-radius: 2px;
                           opacity: 0.9; white-space: nowrap;">
                    {station_name[:15]}
                </div>
                """
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(html=label_html)
                ).add_to(m)
        
        # Fit bounds - collect coordinates from all stations
        lats = []
        lons = []
        for _, station in line_df.iterrows():
            lat, lon = get_lat_lon(station)
            if lat is not None and lon is not None:
                lats.append(lat)
                lons.append(lon)
        
        if len(lats) > 1:
            m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
        
        # Add layer control
        LayerControl(collapsed=False, position='topright').add_to(m)
        
        return m
        
    except Exception as e:
        print(f"Error creating line-specific map: {e}")
        return None


def get_station_details(station_name, stations_df):
    """
    Get detailed information about a specific station.
    
    Args:
        station_name: Name of the station
        stations_df: DataFrame with station information
    
    Returns:
        Dictionary with station details
    """
    try:
        station = stations_df[
            (stations_df['Station'] == station_name) |
            (stations_df['Station_Name'] == station_name)
        ]
        
        if station.empty:
            return None
        
        row = station.iloc[0]
        return {
            'name': row.get('Station_Name', row.get('Station')),
            'line': row.get('Line', 'Unknown'),
            'latitude': row.get('Latitude', row.get('lat')),
            'longitude': row.get('Longitude', row.get('lon')),
            'station_id': row.get('Station_ID', 'N/A'),
        }
    except Exception as e:
        return None
