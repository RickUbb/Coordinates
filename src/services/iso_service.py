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
        str: El nombre traducido del país.
    """
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translation = translator.translate(country)
        return translation if translation else None
    except Exception as e:
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
    for entry in data:
        if entry['name']['common'].strip().lower() == country.strip().lower():
            return {'cca2': entry['cca2'], 'cca3': entry['cca3']}

        native_names = entry['name'].get('nativeName', {})
        for names in native_names.values():
            if names['common'].strip().lower() == country.strip().lower():
                return {'cca2': entry['cca2'], 'cca3': entry['cca3']}

    return None


def search_country_in_api(country):
    """
    Busca un país en la API externa.

    Args:
        country (str): Nombre del país a buscar.

    Returns:
        dict: Diccionario con los códigos 'cca2' y 'cca3' del país encontrado, o None si no se encuentra.
    """
    api_url = f'https://restcountries.com/v3.1/name/{country}'
    response = requests.get(api_url)

    if response.status_code == 200:
        country_data = response.json()

        # Encontrar la entrada exacta
        exact_match = None
        for item in country_data:
            if item['name']['common'].strip().lower() == country.strip().lower():
                exact_match = item
                break
            native_names = item['name'].get('nativeName', {})
            for names in native_names.values():
                if names['common'].strip().lower() == country.strip().lower():
                    exact_match = item
                    break

        return exact_match

    return None


def save_new_entry(data, storage_path, new_entry):
    """
    Guarda una nueva entrada en el archivo JSON local.

    Args:
        data (list): Lista de países del archivo JSON local.
        storage_path (str): Ruta al archivo JSON local.
        new_entry (dict): Nueva entrada a guardar.
    """
    data.append(new_entry)
    with open(storage_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_iso_from_country(country):
    """
    Función que obtiene los códigos ISO 3166-1 de un país dado, ya sea localmente o consultando una API externa.
    """
    storage_path = os.path.join(os.path.dirname(
        __file__), '..', 'storage', 'Isos3166-1.json')

    try:
        # Cargar archivo JSON local
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Verificar si el país ya está en el archivo
        result = find_country_in_data(country, data)
        if result:
            return result

        # Consultar API externa si no está en el archivo
        exact_match = search_country_in_api(country)
        if exact_match:
            new_entry = {
                'name': exact_match['name'],
                'cca2': exact_match['cca2'],
                'cca3': exact_match['cca3'],
            }

            # Verificar nuevamente antes de agregar al archivo JSON
            if not find_country_in_data(new_entry['name']['common'], data):
                save_new_entry(data, storage_path, new_entry)

            return {'cca2': new_entry['cca2'], 'cca3': new_entry['cca3']}

        # Intentar con traducción al inglés
        translated_country = translate_country_name(country, 'en')
        if translated_country:
            exact_match = search_country_in_api(translated_country)
            if exact_match:
                new_entry = {
                    'name': exact_match['name'],
                    'cca2': exact_match['cca2'],
                    'cca3': exact_match['cca3'],
                }

                if not find_country_in_data(new_entry['name']['common'], data):
                    save_new_entry(data, storage_path, new_entry)

                return {'cca2': new_entry['cca2'], 'cca3': new_entry['cca3']}

        # Intentar con traducción al español
        translated_country = translate_country_name(country, 'es')
        if translated_country:
            exact_match = search_country_in_api(translated_country)
            if exact_match:
                new_entry = {
                    'name': exact_match['name'],
                    'cca2': exact_match['cca2'],
                    'cca3': exact_match['cca3'],
                }

                if not find_country_in_data(new_entry['name']['common'], data):
                    save_new_entry(data, storage_path, new_entry)

                return {'cca2': new_entry['cca2'], 'cca3': new_entry['cca3']}

        return {'error': 'Country not found in external API'}

    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}
