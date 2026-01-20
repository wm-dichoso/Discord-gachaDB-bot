from database_manager import DatabaseManager

db = DatabaseManager()

if db.connect_db():
    print("Ready to use database!")
else:
    print("Database failed to connect.")

# run if no tables ?
def init():
    if db.create_tables():
        print("tables created!")
    else:
        print("couldnt create tables.")
    
    db.add_version(0.1)

# # create_tb()

# res = db.banner_exists(1)
# print(f"banner with banner id 1 exists?: {res}")

# pity = db.get_current_pity(1)
# print(f"pity of banner id 1: {pity}")


# increase = 10
# inc = db.increment_pity(1, increase)
# if inc:
#     print(f"success reseting: {inc}")



# new_pity = 70
# # inc = db.reset_pity(1, new_pity)
# # if inc:
# #     print(f"success reseting: {inc}")



# pity = db.get_current_pity(1)
# print(f"pity of banner id 1: {pity}")


# db.add_version(0.1)