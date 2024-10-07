"""
coordinates_api.py

Este módulo contiene funciones para interactuar con el servicio de OpenStreetMap (OSM) y obtener coordenadas 
geográficas (latitud y longitud) de una provincia y ciudad. Además, verifica si las coordenadas ya existen 
en la base de datos y, si no, las agrega a la colección de MongoDB.
"""

import requests  # Para hacer solicitudes HTTP al API de OpenStreetMap
# Para insertar coordenadas en MongoDB
from src.utils.functions.add_coordinates import add_one_coordinate


def get_coordinates_from_data(data, addresstype):
    """
    Filtra el JSON de OpenStreetMap para obtener las coordenadas basadas en el 'addresstype'.

    Args:
        data (list): Datos obtenidos de la API de OpenStreetMap.
        addresstype (str): Tipo de dirección ('city', 'state', etc.).

    Returns:
        tuple: Latitud y longitud de la dirección filtrada.
    """
    filtered_data = next(
        (obj for obj in data if obj.get('addresstype') == addresstype), None)
    if filtered_data:
        return filtered_data['lat'], filtered_data['lon'], filtered_data["display_name"]
    else:
        if addresstype == "city":
            filtered_data = next((obj for obj in data if obj.get('addresstype') in [
                                 'municipality', 'town']), None)
            if filtered_data:
                return filtered_data['lat'], filtered_data['lon'], filtered_data["display_name"]

        elif addresstype == "state":
            filtered_data = next((obj for obj in data if obj.get('addresstype') in [
                                 'administrative', 'county']), None)
            if filtered_data:
                return filtered_data['lat'], filtered_data['lon'], filtered_data["display_name"]

    return None, None, None


def get_coordinates_osm(direction: str, subnivel: int, country_exist: bool):
    """
    Consulta el servicio de OpenStreetMap (OSM) para obtener las coordenadas de una ubicación específica.

    Args:
        direction (str): Dirección a buscar (país, provincia o ciudad).
        subnivel (int): Nivel de la ubicación (3 para provincia, 4 para ciudad).
        country_exist (bool): Si el país es parte de la búsqueda.

    Returns:
        tuple: Latitud, longitud, y nombre del país si no existía.
    """
    url = f"https://nominatim.openstreetmap.org/search?q={
        direction}&format=json"
    headers = {'User-Agent': 'Localizacion (su correo aquí)'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        data = response.json()

        if subnivel == 4:
            return get_coordinates_from_data(data, 'city')
        elif subnivel == 3:
            return get_coordinates_from_data(data, 'state')
        else:
            return None, None, None
    except requests.RequestException as e:
        print(f"Error al realizar la solicitud HTTP: {e}")
        return None, None, None


def obtener_coordenadas(db, collection_name, country: str, province: str, city: str):
    """
    Obtiene las coordenadas de una provincia y ciudad. Si no se encuentran en la base de datos, consulta OSM y las inserta.

    Args:
        db (Database): Instancia de la base de datos MongoDB.
        collection_name (str): Nombre de la colección donde se almacenarán las coordenadas.
        country (str): Nombre del país (opcional).
        province (str): Nombre de la provincia.
        city (str): Nombre de la ciudad.

    Returns:
        tuple: Coordenadas de la provincia y ciudad, o (None, None, None, None) si no se encuentran.
    """
    # Construir el filtro dinámicamente según los valores proporcionados
    search_filter = {}
    if country != "NA":
        search_filter['sub_1'] = country
    if province != "NA":
        search_filter['sub_3'] = province
    if city != "NA":
        search_filter['sub_4'] = city

    # Verificar si ya existen las coordenadas en la base de datos
    existing_coords = db[collection_name].find_one(search_filter)

    if existing_coords:
        print(f"Coordenadas encontradas en la base de datos para {
              province}, {city}.")
        return (existing_coords.get('lat_sub_3'), existing_coords.get('lon_sub_3'),
                existing_coords.get('lat_sub_4'), existing_coords.get('lon_sub_4'))

    print(f"Coordenadas no encontradas en la base de datos. Consultando el API para {
          province}, {city}.")

    # Preparar las direcciones según si el país existe
    province_direction = f"{country}, {
        province}" if country != "NA" else province
    city_direction = f"{country}, {city}" if country != "NA" else city
    country_exist = country != "NA"

    if (province != 'NA'):
        # Obtener las coordenadas de la provincia y la ciudad
        province_lat, province_lon, _ = get_coordinates_osm(
            province_direction, 3, country_exist)
    else:
        province_lat, province_lon = None, None

    if (city != 'NA'):
        city_lat, city_lon, _ = get_coordinates_osm(
            city_direction, 4, country_exist)
    else:
        city_lat, city_lon = None, None

    if province_lat == None and province_lon == None and city_lat == None and city_lon == None:
        return None, None, None, None 

    # if province_lat and province_lon or city_lat and city_lon:
    if country_exist and country != "NA":
        add_one_coordinate(db, collection_name, country, province, city,
                           province_lat, province_lon, city_lat, city_lon)
        return province_lat, province_lon, city_lat, city_lon

    else:
        display_name_parts = _.rsplit(', ')
        country = display_name_parts[-1]
        add_one_coordinate(db, collection_name, country, province, city,
                           province_lat, province_lon, city_lat, city_lon)
        return province_lat, province_lon, city_lat, city_lon

    # print(f"No se pudieron obtener las coordenadas del API para {
    #     province}, {city}.")
    # return None, None, None, None
