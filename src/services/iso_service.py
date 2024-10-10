"""
iso_service.py

Este módulo proporciona las funciones necesarias para obtener los códigos ISO 3166-1 de un país, 
ya sea localmente desde un archivo JSON o consultando una API externa. También se incluyen 
funciones para traducir nombres de países, guardar nuevos registros en el archivo local, 
y manejar posibles errores en las solicitudes.

Se utiliza `deep_translator` para traducir nombres de países cuando es necesario.
"""

import requests
import json
import os
from deep_translator import GoogleTranslator


def translate_country_name(country, target_language):
    """
    Traduce el nombre de un país al idioma objetivo utilizando Google Translate a través de deep-translator.

    Args:
        country (str): El nombre del país a traducir.
        target_language (str): El idioma objetivo para la traducción ('en' para inglés, 'es' para español).

    Returns:
        str: El nombre traducido del país, o None si ocurre un error.
    """
    try:
        # Crear una instancia del traductor con el idioma objetivo
        translator = GoogleTranslator(source='auto', target=target_language)
        # Traducir el nombre del país
        translation = translator.translate(country)
        return translation if translation else None
    except Exception as e:
        # Imprimir el error si ocurre una excepción durante la traducción
        print(f"Error en la traducción: {e}")
        return None


def find_country_in_data(country, data):
    """
    Busca un país en el archivo JSON local.

    Args:
        country (str): Nombre del país a buscar.
        data (list): Lista de países del archivo JSON local.

    Returns:
        dict: Diccionario con los códigos 'cca2' y 'cca3' del país encontrado, o None si no se encuentra.
    """
    # Convertir el nombre del país a minúsculas y eliminar espacios en blanco
    country_lower = country.strip().lower()

    # Iterar sobre cada entrada en los datos locales
    for entry in data:
        # Verificar el nombre común en el campo 'common'
        if entry['name']['common'].strip().lower() == country_lower:
            return {'cca2': entry['cca2'], 'cca3': entry['cca3']}

        # Verificar en el campo 'nativeName'
        native_names = entry['name'].get('nativeName', {})
        for names in native_names.values():
            if names['common'].strip().lower() == country_lower:
                return {'cca2': entry['cca2'], 'cca3': entry['cca3']}

    # Devolver None si no se encuentra el país en los datos locales
    return None


def search_country_in_api(country):
    """
    Busca un país en la API externa.

    Args:
        country (str): Nombre del país a buscar.

    Returns:
        dict: Diccionario con los datos del país encontrado, o None si no se encuentra.
    """
    try:
        # Crear la URL de la API con el nombre del país
        api_url = f'https://restcountries.com/v3.1/name/{country}'
        # Realizar una solicitud GET a la API
        response = requests.get(api_url)

        # Si la respuesta es exitosa (código 200)
        if response.status_code == 200:
            country_data = response.json()
            country_lower = country.strip().lower()

            # Iterar sobre los datos del país en la respuesta de la API
            for item in country_data:
                # Verificar el nombre común en el campo 'name'
                if item['name']['common'].strip().lower() == country_lower:
                    return item

                # Verificar en el campo 'nativeName'
                native_names = item['name'].get('nativeName', {})
                for names in native_names.values():
                    if names['common'].strip().lower() == country_lower:
                        return item

        return None
    except requests.RequestException as e:
        # Imprimir el error si ocurre una excepción durante la solicitud a la API
        print(f"Error en la solicitud a la API: {e}")
        return None


def save_new_entry(data, storage_path, new_entry):
    """
    Guarda una nueva entrada en el archivo JSON local.

    Args:
        data (list): Lista de países del archivo JSON local.
        storage_path (str): Ruta al archivo JSON local.
        new_entry (dict): Nueva entrada a guardar.
    """
    try:
        # Añadir la nueva entrada a los datos
        data.append(new_entry)
        # Guardar los datos actualizados en el archivo JSON
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        # Imprimir el error si ocurre una excepción durante el guardado
        print(f"Error al guardar la nueva entrada: {e}")


def get_iso_from_country(country):
    """
    Función que obtiene los códigos ISO 3166-1 de un país dado, ya sea localmente o consultando una API externa.

    Args:
        country (str): Nombre del país a buscar.

    Returns:
        dict: Diccionario con los códigos 'cca2' y 'cca3' del país encontrado, o un mensaje de error si ocurre un problema.
    """
    # Definir la ruta del archivo JSON local
    storage_path = os.path.join(os.path.dirname(
        __file__), '..', 'storage', 'Isos3166-1.json')

    try:
        # Cargar el archivo JSON local
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Verificar si el país ya está en el archivo local
        result = find_country_in_data(country, data)
        if result:
            return result

        # Consultar la API externa si no está en el archivo local
        exact_match = search_country_in_api(country)
        if exact_match:
            # Crear una nueva entrada con los datos del país encontrado
            new_entry = {
                'name': exact_match['name'], 'cca2': exact_match['cca2'], 'cca3': exact_match['cca3']}

            # Guardar la nueva entrada en el archivo local si no está presente
            if not find_country_in_data(new_entry['name']['common'], data):
                save_new_entry(data, storage_path, new_entry)

            return {'cca2': new_entry['cca2'], 'cca3': new_entry['cca3']}

        # Intentar con traducción al inglés
        translated_country = translate_country_name(country, 'en')
        if translated_country:
            exact_match = search_country_in_api(translated_country)
            if exact_match:
                new_entry = {
                    'name': exact_match['name'], 'cca2': exact_match['cca2'], 'cca3': exact_match['cca3']}
                if not find_country_in_data(new_entry['name']['common'], data):
                    save_new_entry(data, storage_path, new_entry)
                return {'cca2': new_entry['cca2'], 'cca3': new_entry['cca3']}

        # Intentar con traducción al español
        translated_country = translate_country_name(country, 'es')
        if translated_country:
            exact_match = search_country_in_api(translated_country)
            if exact_match:
                new_entry = {
                    'name': exact_match['name'], 'cca2': exact_match['cca2'], 'cca3': exact_match['cca3']}
                if not find_country_in_data(new_entry['name']['common'], data):
                    save_new_entry(data, storage_path, new_entry)
                return {'cca2': new_entry['cca2'], 'cca3': new_entry['cca3']}

        return {'error': 'Country not found in external API'}

    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}
