from decouple import config

mongo = {
    'mongodb_url': config('MONGODB_URL'),
    'mongodb_db_name': config('MONGODB_DB_NAME'),
    'mongodb_collection_name_coordinates': config('MONGODB_COLLECTION_NAME_COORDINATES'),

}
