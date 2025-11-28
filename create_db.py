from api.db.database import create_database


try:
    create_database()
    print('Database created.')
except Exception as e:
    print("An error occurred while creating the database")
    print(e)