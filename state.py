#!/usr/bin/env python
import database

class State:
    def __init__(self, radius, speedDif, altitudeDif, headingDif, trajectoryDif, database):
        self.db = database

        speedDif = speedDif / 5
        speedDif = self.getStateCategory(speedDif)

        altitudeDif = altitudeDif / 2
        altitudeDif = self.getStateCategory(altitudeDif)

        headingDif = headingDif * 3
        headingDif = self.getStateCategory(headingDif)

        trajectoryDif = trajectoryDif * 2000
        trajectoryDif = self.getStateCategory(trajectoryDif)
        self.radius = self.getStateCategory(radius)
        self.speedDif = speedDif
        self.altitudeDif = altitudeDif
        self.headingDif = headingDif
        self.trajectoryDif = trajectoryDif

        dbInfo = database.getState(self)
        if dbInfo == None:
            self.objectID = database.addNewStates(self)
        else:
            self.objectID = dbInfo["_id"]

    def chooseAnAction(self):
        diction = self.db.getStateDict(self.objectID)
        print(diction)

    def calculateAward(self):
        return 1 / self.speedDif + 1 / self.altitudeDif + 1 / self.headingDif  + 1 / self.trajectoryDif

    def isDifferent(self, state):
        if self.radius == state.radius and self.speedDif == state.speedDif and self.altitudeDif == state.altitudeDif and self.headingDif == state.headingDif and self.trajectoryDif == state.trajectoryDif:
            return False
        return True

    def getStateCategory(self, num):
        if abs(num) < 0.3:
            return 0.5
        count = 1
        while not abs(num) < count**1.5:
            count = count + 1
        return count

# print db
# collection = db.my_collection
# doc = {"name":"Alberto","surname":"Negron","twitter":"@Altons"}
# print collection
# collection.insert(doc)
# print 'done'
# print post_id
