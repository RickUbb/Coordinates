"""
normalize_text.py

Este módulo contiene una función para normalizar texto, eliminando tildes, espacios innecesarios, 
y realizando validaciones para asegurar que el texto esté en un formato limpio y estándar.
"""

import pandas as pd  # Importa pandas para trabajar con la verificación de valores NaN
import unicodedata  # Para la eliminación de tildes y normalización de caracteres Unicode
import re  # Para trabajar con expresiones regulares


def normalize(text):
    """
    Normaliza el texto de entrada eliminando tildes, espacios innecesarios y validando que el texto
    contenga caracteres válidos.

    La función realiza las siguientes operaciones:
    1. Verifica si el texto es nulo o inválido (NaN, None, vacío, etc.).
    2. Elimina tildes y normaliza el texto.
    3. Elimina espacios innecesarios y formatea el texto en formato de título.

    Args:
        text (str): El texto de entrada a normalizar.

    Returns:
        str: El texto normalizado o 'NA' si el texto es inválido.
    """

    # Verificación de texto inválido (NaN, None)
    if pd.isna(text) or text is None:
        return "NA"  # Si es inválido, retorna "NA" como valor por defecto

    # Convertir a string y eliminar espacios innecesarios al principio y al final
    text_str = str(text).strip()

    # Validaciones adicionales para identificar si el texto es válido o debe ser "NA"
    if (text_str == "" or  # El texto está vacío
        text_str.isdigit() or  # Es un número puro
        # Palabras clave o valores no útiles
        text_str in ['True', 'False', 'None', 'null', '-', 'NA', 'Na'] or
        # Si es un solo carácter y no es letra
        len(text_str) == 1 and not text_str.isalpha() or
        # Verifica que haya al menos un carácter alfanumérico en el texto
            not any(char.isalnum() for char in text_str)):
        return "NA"  # Si alguna de estas condiciones se cumple, el texto se considera inválido

    # Eliminar tildes: Normaliza el texto a formato NFD y elimina los acentos/tildes
    text_str = unicodedata.normalize('NFD', text_str).encode(
        'ascii', 'ignore').decode('utf-8')

    # Eliminar espacios extras y formatear el texto a formato de título (primera letra de cada palabra en mayúscula)
    text_str = re.sub(r'\s+', ' ', text_str).strip().title()

    return text_str  # Retorna el texto ya normalizado
