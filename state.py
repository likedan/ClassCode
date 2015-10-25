#!/usr/bin/env python
import database
from random import randint

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

    def recordAction(self, action, nextStateID, timeInPrevState):
        action = str(action[0]) + ","+ str(action[1])
        diction = self.db.getStateDict(self.objectID)
        if not "actions" in diction:
            diction["actions"] = {action : {nextStateID: [timeInPrevState]}}
        else:
            actions = diction["actions"]
            if not action in actions:
                actions[action] = {nextStateID: [timeInPrevState]}
            else:
                theAction = actions[action]
                if not nextStateID in theAction:
                    theAction[nextStateID] = [timeInPrevState]
                else:
                    theAction[nextStateID].append(timeInPrevState)
        self.db.saveState(diction)
        print(nextStateID, " ," ,action ," recorded")

    def chooseAnAction(self):
        diction = self.db.getStateDict(self.objectID)
        print(diction)
        if not "actions" in diction:
            return (0,0)
        else:
            dictionM = {}
            for key in diction["actions"].keys():
                keyArr = key.split(',')
                dictionM[(int(keyArr[0]), int(keyArr[1]))] = diction["actions"][key]
            return self.chooseActionFromPolicy(dictionM)

    def chooseActionFromPolicy(self, diction):
        throttle = randint(0, 5)
        ruddle = randint(-5, 5)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # print(diction)
        # while(throttle <= 5):
        #     while (ruddle <= 5):
        #         if (throttle, ruddle) in diction:
        #             print ("inside")
        #             resultStates = diction[(throttle, ruddle)].keys()
        #             totalTry = 0
        #             for state in resultStates:
        #                 totalTry = totalTry + diction[(throttle, ruddle)][state]
        #             if totalTry > 1:
        #                 print ("lala")
        #             else:
        #                 return (throttle, ruddle)
        #         else:
        #             return (throttle, ruddle)
        #         ruddle = ruddle + 1
        #     throttle = throttle + 1

        return (throttle, ruddle)


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
