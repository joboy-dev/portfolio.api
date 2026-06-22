from decouple import config


firebase_config = {
    'apiKey': "AIzaSyCUzTFWjsDW816NT8JgNQiCMgmGwUxkGj0",
    'authDomain': "python-storage-d1e10.firebaseapp.com",
    'databaseURL': "https://python-storage-d1e10-default-rtdb.firebaseio.com",
    'projectId': "python-storage-d1e10",
    'storageBucket': "python-storage-d1e10.appspot.com",
    'messagingSenderId': "253588525093",
    'appId': "1:253588525093:web:b983734a4caf1ea32c6fcc",
    'measurementId': "G-VPQSJXB8W5",
    'serviceAccount': 'serviceAccount.json' if config("PYTHON_ENV") == "dev" else '/etc/secrets/serviceAccount.json',
    'databaseURL': "https://python-storage-d1e10-default-rtdb.firebaseio.com"
}

# firebase_config = {
#     'apiKey': config('FIREBASE_API_KEY'),
#     'authDomain': config('FIREBASE_AUTH_DOMAIN'),
#     'databaseURL': config('FIREBASE_DATABASE_URL'),
#     'projectId': config('FIREBASE_PROJECT_ID'),
#     'storageBucket': config('FIREBASE_STORAGE_BUCKET'),
#     'messagingSenderId': config('FIREBASE_MESSAGING_SENDER_ID'),
#     'appId': config('FIREBASE_APP_ID'),
#     'measurementId': config('FIREBASE_MEASUREMENT_ID'),
#     'serviceAccount': config('FIREBASE_SERVICE_ACCOUNT'),
# }
