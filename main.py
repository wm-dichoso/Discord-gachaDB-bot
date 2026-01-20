from database_manager import DatabaseManager

db = DatabaseManager()

if db.connect_db():
    print("Ready to use database!")
else:
    print("Database failed to connect.")

# run if no tables ?
def create_tb():
    if db.create_tables():
        print("tables created!")
    else:
        print("couldnt create tables.")

