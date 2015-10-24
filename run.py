import Pilot
import database

db = database.Database()
a = Pilot.Pilot(db)
a.setRadiusAndAngle(10000, 90)
a.start()
