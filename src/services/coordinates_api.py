"""
coordinates_api.py

Este módulo contiene funciones para interactuar con el servicio de OpenStreetMap (OSM) y obtener coordenadas 
geográficas (latitud y longitud) de una provincia y ciudad. Además, verifica si las coordenadas ya existen 
en la base de datos y, si no, las agrega a la colección de MongoDB.
"""

import requests  # Para hacer solicitudes HTTP al API de OpenStreetMap
# Importa la función para normalizar el texto
from src.utils.functions.normalize_text import normalize
# Para insertar coordenadas en MongoDB
from src.utils.functions.add_coordinates import add_one_coordinate

# Función para obtener coordenadas desde OpenStreetMap


def get_coordinates_osm(direction: str):
    """
    Consulta el servicio de OpenStreetMap (OSM) para obtener las coordenadas de una ubicación específica.

    Args:
        direction (str): Dirección a buscar (país, provincia o ciudad).

    Returns:
        tuple: Latitud y longitud de la dirección. Si no se encuentran, retorna (None, None).
    """
    # URL para realizar la solicitud al API de OSM con el formato y límite de resultados
    url = f"https://nominatim.openstreetmap.org/search?q={
        direction}&format=json&limit=1"

    headers = {
        # Cambiar a un correo registrado en OpenStreetMap para evitar bloqueos
        'User-Agent': 'Localizacion (su correo aquí)'
    }

    # Realiza la solicitud HTTP
    response = requests.get(url, headers=headers)

    # Si la solicitud fue exitosa (código 200)
    if response.status_code == 200:
        data = response.json()  # Convierte la respuesta JSON
        if len(data) > 0:
            # Retorna la latitud y longitud del primer resultado
            latitud = data[0]['lat']
            longitud = data[0]['lon']
            return latitud, longitud
        else:
            return None, None  # Si no se encontraron resultados
    else:
        print(f"Error al realizar la solicitud HTTP: {response.status_code}")
        return None, None  # Si hubo un error en la solicitud


# Función principal para obtener las coordenadas de provincia y ciudad
def obtener_coordenadas(db, collection_name, country: str, province: str, city: str):
    """
    Obtiene las coordenadas de una provincia y ciudad. Primero busca en la base de datos, y si no se encuentran, 
    realiza una consulta al API de OpenStreetMap (OSM) y luego inserta las coordenadas en la base de datos.

    Args:
        db (Database): La instancia de la base de datos MongoDB.
        collection_name (str): El nombre de la colección donde se almacenarán las coordenadas.
        country (str): El nombre del país.
        province (str): El nombre de la provincia.
        city (str): El nombre de la ciudad.

    Returns:
        tuple: Las coordenadas de la provincia (latitud, longitud) y las coordenadas de la ciudad (latitud, longitud). 
               Si no se encuentran, retorna (None, None, None, None).
    """
    # Verificar si ya existen las coordenadas en la base de datos
    existing_coords = db[collection_name].find_one({
        'sub_1': normalize(country),  # Normaliza el nombre del país
        'sub_3': normalize(province),  # Normaliza el nombre de la provincia
        'sub_4': normalize(city)       # Normaliza el nombre de la ciudad
    })

    if existing_coords:
        # Si las coordenadas ya están en la base de datos, retornarlas
        print(f"Coordenadas encontradas en la base de datos para {
              province}, {city}.")
        return (existing_coords['lat_sub_3'], existing_coords['lon_sub_3'],
                existing_coords['lat_sub_4'], existing_coords['lon_sub_4'])
    else:
        # Si no se encuentran, consultar el API de OpenStreetMap
        print(f"Coordenadas no encontradas en la base de datos. Consultando el API para {
              province}, {city}.")
        # Formatear dirección de la provincia
        province_direction = f"{country}, {province}"
        # Formatear dirección de la ciudad
        city_direction = f"{country}, {city}"

        # Obtener las coordenadas desde OpenStreetMap
        province_lat, province_lon = get_coordinates_osm(province_direction)
        city_lat, city_lon = get_coordinates_osm(city_direction)

        # Si las coordenadas fueron obtenidas correctamente
        if province_lat and province_lon and city_lat and city_lon:
            # Insertar las coordenadas en la base de datos
            add_one_coordinate(db, collection_name, country, province, city,
                               province_lat, province_lon, city_lat, city_lon)
            return province_lat, province_lon, city_lat, city_lon
        else:
            print(f"No se pudieron obtener las coordenadas del API para {
                  province}, {city}.")
            return None, None, None, None  # Si no se obtuvieron coordenadas
