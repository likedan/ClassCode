#!/usr/bin/env python
import database
from random import randint

class State:

    def __init__(self, radius, speedDif, altitudeDif, headingDif, trajectoryDif, database):
        self.db = database

        speedDif = speedDif / 10
        speedDif = self.getStateCategory(speedDif)

        altitudeDif = altitudeDif / 3
        altitudeDif = self.getStateCategory(altitudeDif)

        headingDif = headingDif * 5
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

    def chooseAnAction(self):
        diction = self.db.getStateDict(self.objectID)
        # print(diction)
        if not "actions" in diction:
            return (0,0)
        else:
            dictionM = {}
            for key in diction["actions"].keys():
                keyArr = key.split(',')
                dictionM[(int(keyArr[0]), int(keyArr[1]))] = diction["actions"][key]
            return self.chooseActionFromPolicy(dictionM)

    def chooseActionFromPolicy(self, diction):

        if len(diction) > 5:
            if 7 < randint(0, 10):
                aileron = randint(-3, 3)
                elevator = randint(-3, 3)
            else:
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                actionResult = {}
                for action in diction.keys():
                    awardCount = 0
                    total = 0
                    for state in diction[action].keys():
                        stateInfo = self.db.getStateDict(state)
                        awardCount = awardCount + 1
                        total = total + stateInfo["award"]
                        for num in diction[action][state]:
                            awardCount = awardCount + num
                            total = total + num * self.calculateAward()
                    total = total / awardCount
                    actionResult[total] = action

                resultList = sorted(actionResult, reverse = True)
                # print(actionResult)
                # print(resultList)
                return actionResult[resultList[0]]
        else:
            aileron = randint(-3, 3)
            elevator = randint(-3, 3)
        return (aileron, elevator)


    def calculateAward(self):
        return 1000 / self.speedDif / self.altitudeDif / self.headingDif / self.trajectoryDif

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
