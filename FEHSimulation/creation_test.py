import pickle

support_arr = [("Dimitri", "Felix"), ("Seiðr", "Heiðr")]

# Clear File
open("supports.pkl", "w").close()

# Dump Support Array
db_file = open("supports.pkl", "ab")
pickle.dump(support_arr, db_file)
db_file.close()

loaded_file = open('supports.pkl', 'rb')
db = pickle.load(loaded_file)

print(db)