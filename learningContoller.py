#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import Pilot
import database

db = database.Database()
a = Pilot.Pilot(db)
a.setRadiusAndAngle(10000, 90)
a.start()


# print db
# collection = db.my_collection
# doc = {"name":"Alberto","surname":"Negron","twitter":"@Altons"}
# print collection
# collection.insert(doc)
# print 'done'
# print post_id
