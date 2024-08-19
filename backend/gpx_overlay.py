import logging
import requests
import gpxpy
import folium

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GasStation:
    def __init__(self, lat, lon, tags):
        self.lat = lat
        self.lon = lon
        self.brand = tags.get('brand', '')
        self.name = tags.get('name', '')
        self.street = tags.get('addr:street', '')
        self.housenumber = tags.get('addr:housenumber', '')
        self.postcode = tags.get('addr:postcode', '')
        self.city = tags.get('addr:city', '')
        self.operator = tags.get('operator', '')
        self.opening_hours = tags.get('opening_hours', '')
    
    def format_tooltip(self):
        tooltip_parts = []
        if self.brand:
            tooltip_parts.append(f"<b>{self.brand}</b>")
        if self.name:
            tooltip_parts.append(f"{self.name}")
        if self.street or self.housenumber:
            tooltip_parts.append(f"{self.street} {self.housenumber}".strip())
        if self.postcode or self.city:
            tooltip_parts.append(f"{self.postcode} {self.city}".strip())
        if self.operator:
            tooltip_parts.append(f"{self.operator}")
        if self.opening_hours:
            tooltip_parts.append(f"{self.opening_hours}")
        return "<br>".join(tooltip_parts)

def parse_gpx_from_disk(file_path):
    logger.info(f'Parsing GPX file {file_path}...')
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        
    route = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                route.append((point.latitude, point.longitude))
    logger.info(f'Parsed {len(route)} points from GPX file')
    return route

def parse_gpx(gpx):
    logger.info(f'Parsing GPX file...')
    gpx = gpxpy.parse(gpx)    
    route = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                route.append((point.latitude, point.longitude))
    logger.info(f'Parsed {len(route)} points from GPX file')
    return route

def sample_points(route, n):
    return route[::n]

def fetch_node_coordinates(node_ids):
    overpass_url = "http://overpass-api.de/api/interpreter"
    node_ids_str = ','.join(map(str, node_ids))
    overpass_query = f"""
    [out:json];
    node(id:{node_ids_str});
    out body;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    return {node['id']: (node['lat'], node['lon']) for node in data['elements']}

def find_gas_stations_sampled(route, n, radius):
    overpass_url = "http://overpass-api.de/api/interpreter"
    gas_stations = []
    
    sampled_route = sample_points(route, n)
    
    for lat, lon in sampled_route:
        overpass_query = f"""
        [out:json];
        (
          node["amenity"="fuel"](around:{radius},{lat},{lon});
          way["amenity"="fuel"](around:{radius},{lat},{lon});
        );
        out body;
        """
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()
        
        for element in data['elements']:
            if element['type'] == 'node':
                gas_stations.append(GasStation(
                    element['lat'],
                    element['lon'],
                    element['tags']
                ))
                logger.info(f'Found gas station (ID: {element["id"]}) at {element["lat"]}, {element["lon"]}')
            elif element['type'] == 'way':
                node_ids = element['nodes']
                node_coords = fetch_node_coordinates(node_ids)
                if node_coords:
                    centroid_lat = sum(coord[0] for coord in node_coords.values()) / len(node_coords)
                    centroid_lon = sum(coord[1] for coord in node_coords.values()) / len(node_coords)
                    gas_stations.append(GasStation(
                        centroid_lat,
                        centroid_lon,
                        element['tags']
                    ))
                    logger.info(f'Found gas station (ID: {element["id"]}) at {centroid_lat}, {centroid_lon}')
    return gas_stations

def plot_route_and_gas_stations(route, gas_stations):
    logger.info('Plotting route and gas stations...')
    map_center = route[len(route)//2]
    m = folium.Map(location=map_center, zoom_start=13)
    folium.PolyLine(route, color='blue', weight=5).add_to(m)
    for station in gas_stations:
        folium.Marker(location=(station.lat, station.lon), 
                      tooltip=station.format_tooltip(), 
                      icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
    logger.info('Plotting done')
    return m

def plot_route_and_gas_stations_gm(route, gas_stations):
    logger.info('Plotting route and gas stations...')
    map_center = route[len(route)//2]
    m = folium.Map(location=map_center, zoom_start=13)
    folium.PolyLine(route, color='blue', weight=5).add_to(m)
    for station in gas_stations:
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={station.lat},{station.lon}"
        popup_html = f'<a href="{google_maps_url}" target="_blank">Open in Google Maps</a>'
        popup = folium.Popup(popup_html, max_width=250)
        folium.Marker(location=(station.lat, station.lon), 
                      tooltip=station.format_tooltip(), 
                      icon=folium.Icon(color='red', icon='info-sign'),
                      popup=popup).add_to(m)
    logger.info('Plotting done')
    return m

if __name__ == '__main__':
    # Example usage
    n = 100  # Sample every nth point of the GPX file
    radius = 5000  # Search radius in meters for each sampled point
    filename = 'yourfile.gpx' # Path to the GPX file
    route = parse_gpx_from_disk(filename)
    gas_stations = find_gas_stations_sampled(route, n, radius)
    m = plot_route_and_gas_stations_gm(route, gas_stations)
    m.save(filename.replace('.gpx', '_gas_stations.html'))