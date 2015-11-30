#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3
import Pilot
import database
import ACTester
db = database.Database()
a = ACTester.ACTester()#Pilot.Pilot(db)
# print(a.PLAN(8000, 8))
# print(a.PC(8000, 8))
# print(a.PC(1000, 8))
a.start()
