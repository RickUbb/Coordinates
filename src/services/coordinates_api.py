"""
coordinates_api.py

Este módulo contiene funciones para interactuar con el servicio de OpenStreetMap (OSM) y obtener coordenadas 
geográficas (latitud y longitud) de una provincia y ciudad. Además, verifica si las coordenadas ya existen 
en la base de datos y, si no, las agrega a la colección de MongoDB.
"""

import requests  # Para hacer solicitudes HTTP al API de OpenStreetMap
# Para manejar excepciones específicas de requests
from requests.exceptions import RequestException
# Para insertar coordenadas en MongoDB
from src.utils.functions.add_coordinates import add_one_coordinate
from src.utils.functions.AddErrorsFunciton import add_one_error_coordinate


def get_coordinates_from_data(data, addresstype):
    """
    Filtra el JSON de OpenStreetMap para obtener las coordenadas basadas en el 'addresstype'.

    Args:
        data (list): Datos obtenidos de la API de OpenStreetMap.
        addresstype (str): Tipo de dirección ('city', 'state', etc.).

    Returns:
        tuple: Latitud y longitud de la dirección filtrada o None si no se encuentra.
    """
    filtered_data = next(
        (obj for obj in data if obj.get('addresstype') == addresstype), None)

    if filtered_data:
        return filtered_data['lat'], filtered_data['lon'], filtered_data["display_name"]
    else:
        if addresstype == "city":
            # Buscar en el orden de prioridad para ciudades
            filtered_data = next((obj for obj in data if obj.get('addresstype') in [
                'city', 'town', 'municipality', 'suburb', 'residential']), None)
            if filtered_data:
                return filtered_data['lat'], filtered_data['lon'], filtered_data["display_name"]
        elif addresstype == "state":
            # Buscar en el orden de prioridad para estados
            filtered_data = next((obj for obj in data if obj.get('addresstype') in [
                'state', 'province', 'administrative', 'county']), None)
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
        tuple: Latitud, longitud, y nombre de la ubicación si se encuentran, o (None, None, None) si no.
    """
    url = f"https://nominatim.openstreetmap.org/search?q={
        direction}&format=json"
    headers = {'User-Agent': 'Localizacion (su correo aquí)'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP

        data = response.json()

        if subnivel == 4:
            return get_coordinates_from_data(data, 'city')
        elif subnivel == 3:
            return get_coordinates_from_data(data, 'state')
        else:
            return None, None, None

    except RequestException as e:
        print(f"Error al realizar la solicitud HTTP a OpenStreetMap para '{direction}'. "
              f"Detalles del error: {str(e)}")
        return None, None, None

    except ValueError as e:
        print(f"Error al interpretar la respuesta de OpenStreetMap. Posiblemente los datos para "
              f"'{direction}' estén mal formateados. Detalles del error: {str(e)}")
        return None, None, None

    except Exception as e:
        print(f"Ocurrió un error inesperado al obtener coordenadas para '{direction}'. "
              f"Detalles del error: {str(e)}")
        return None, None, None


def get_coordinates_from_collection(db, collection_name, search_filter, province, city):
    """
    Busca coordenadas en una colección de la base de datos y retorna los valores de latitud y longitud.
    Si no se encuentran coordenadas válidas, devuelve None.

    :param db: La conexión a la base de datos MongoDB.
    :param collection_name: El nombre de la colección donde buscar.
    :param search_filter: Filtro de búsqueda para los documentos.
    :param province: Nombre de la provincia (para el mensaje de log).
    :param city: Nombre de la ciudad (para el mensaje de log).
    :return: Una tupla con (lat_sub_3, lon_sub_3, lat_sub_4, lon_sub_4) o None si no se encuentran coordenadas.
    """
    try:
        # Realiza la búsqueda en la colección especificada
        coordinates = db[collection_name].find_one(search_filter)

        if coordinates:
            print(f"Coordenadas encontradas en la colección '{
                  collection_name}' para {province}, {city}.")
            lat_sub_3 = coordinates.get('lat_sub_3')
            lon_sub_3 = coordinates.get('lon_sub_3')
            lat_sub_4 = coordinates.get('lat_sub_4')
            lon_sub_4 = coordinates.get('lon_sub_4')

            return lat_sub_3, lon_sub_3, lat_sub_4, lon_sub_4
        else:
            print(f"No se encontraron coordenadas en la colección '{
                  collection_name}' para {province}, {city}.")
            return None

    except Exception as e:
        print(f"Error al consultar la colección '{collection_name}': {str(e)}")
        return None


def search_coordinates(db, search_filter, collection_name, collection_error_name, province, city):
    """
    Busca coordenadas en las colecciones principal y de errores, retornando la primera coincidencia.

    :param db: La conexión a la base de datos MongoDB.
    :param search_filter: Filtro de búsqueda para los documentos.
    :param province: Nombre de la provincia.
    :param city: Nombre de la ciudad.
    :return: Una tupla con (lat_sub_3, lon_sub_3, lat_sub_4, lon_sub_4) o None si no se encuentran coordenadas.
    """

    # Intentar obtener las coordenadas de la colección principal
    coordinates = get_coordinates_from_collection(
        db, collection_name, search_filter, province, city)

    # Si no se encuentran en la colección principal, buscar en la colección de errores
    if coordinates is None:
        print(f"No se encontraron coordenadas en la colección principal. Buscando en la colección de errores.")
        coordinates = get_coordinates_from_collection(
            db, collection_error_name, search_filter, province, city)

    # Retornar las coordenadas encontradas o None si no se encuentran en ninguna colección
    if coordinates:
        return coordinates
    else:
        print(f"No se encontraron coordenadas en ninguna colección para {
              province}, {city}.")
        return None


def obtener_coordenadas(db, collection_name, collection_error_name, country: str, province: str, city: str):
    """
    Obtiene las coordenadas de una provincia y ciudad. Si no se encuentran en la base de datos, consulta OSM y las inserta.

    Args:
        db (Database): Instancia de la base de datos MongoDB.
        collection_name (str): Nombre de la colección donde se almacenarán las coordenadas.
        collection_error_name (str): Nombre de la colección de errores.
        country (str): Nombre del país.
        province (str): Nombre de la provincia.
        city (str): Nombre de la ciudad.

    Returns:
        tuple: Coordenadas de la provincia y ciudad, o (None, None, None, None) si no se encuentran.
    """
    # Construcción del filtro de búsqueda
    search_filter = {}
    if country != "NA":
        search_filter['sub_1'] = country
    if province != "NA":
        search_filter['sub_3'] = province
    if city != "NA":
        search_filter['sub_4'] = city

    try:
        # Buscar coordenadas en la base de datos (colección principal y de errores)
        coordinates = search_coordinates(
            db, search_filter, collection_name, collection_error_name, province, city)

        if coordinates:
            # Retornar las coordenadas encontradas
            return coordinates

        country_exist = country != "NA"

        # Obtener coordenadas de la provincia
        if province != 'NA':
            province_direction = f"{country}, {
                province}" if country_exist else province
            province_lat, province_lon, _ = get_coordinates_osm(
                province_direction, 3, country_exist)
        else:
            province_direction, province_lat, province_lon = None, None, None

        # Obtener coordenadas de la ciudad
        if city != 'NA':
            city_direction = f"{country}, {city}" if country_exist else city
            city_lat, city_lon, _ = get_coordinates_osm(
                city_direction, 4, country_exist)
        else:
            city_direction, city_lat, city_lon = None, None, None

        # Si se obtienen coordenadas incompletas, almacenarlas como error
        if (province_direction and not province_lat) or (city_direction and not city_lat):
            add_one_error_coordinate(db, collection_error_name, country, province, city,
                                     province_lat, province_lon, city_lat, city_lon)

        # Verificar si se obtuvieron coordenadas válidas
        if province_lat is None and province_lon is None and city_lat is None and city_lon is None:
            print(f"No se pudieron obtener coordenadas para {
                  province}, {city}.")
            return None, None, None, None

        # Si se obtienen coordenadas completas, insertar en la base de datos
        if _:
            display_name_parts = _.rsplit(', ')
            # Actualizar el nombre del país basado en el resultado de OSM
            country = display_name_parts[-1]

        add_one_coordinate(db, collection_name, country, province, city,
                           province_lat, province_lon, city_lat, city_lon)

        return province_lat, province_lon, city_lat, city_lon

    except Exception as e:
        print(f"Error al obtener o insertar coordenadas en la base de datos para {province}, {city}. "
              f"Detalles del error: {str(e)}")
        return None, None, None, None
