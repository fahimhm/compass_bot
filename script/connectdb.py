import pymongo
from pymongo import MongoClient

cluster = MongoClient('mongodb+srv://owl_19:dodol123@owlcluster.r0w1y.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

db = cluster['compass_chatbot']['user_profile']

# # POST
# db.insert_one({"_id": 0, "name": "Fahim", "Score": 5})
# db.insert_many([post1, post2])

# # Find
# results = db.find({"name": "Fahim"})
# print(results)
# # >> <pymongo.cursor.Cursor object at 0x0000....>

# for result in results:
#     print(result)
#     # >> {'_id': 0, 'name': 'Fahim'}

# # Delete
# results = db.delete_one({"_id":0})

# # Update
# results = db.update_one({"_id": 5}, {"$set": {"name": "Hadi"}})

# user_profile = {
#     '_id':525011359,
#     'first_name':'Fahim',
#     'username':'fahimhm',
#     'domisili':'Blitar',
#     'gender':'Pria',
#     'age':29
# }

# db.insert_one(user_profile)
for i in db.find({}):
    print(i['first_name'])