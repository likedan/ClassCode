#!/usr/bin/env python
import datetime
import pymongo
import state
from pymongo import MongoClient
from bson.objectid import ObjectId

class Database:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        print ("Connected successfully!!!")
        self.db = client['Policy']
        # self.db["StatesTable"].remove()
        self.policy = self.db['LearningTable']

    def addNewStates(self, state):
        stateObject = {"radius": state.radius, "speed": state.speedDif, "altitude": state.altitudeDif, "heading": state.headingDif, "trajectory": state.trajectoryDif, "award": state.calculateAward()}
        state_id = self.policy.insert_one(stateObject).inserted_id
        return state_id

    # return None if state don't exist
    def getState(self, state):
        state = self.policy.find_one({"radius": state.radius, "speed": state.speedDif, "altitude": state.altitudeDif, "heading": state.headingDif, "trajectory": state.trajectoryDif})
        return state

    def getStateDict(self, id):
        if type(id) == str:
            id = ObjectId(id)
        return self.policy.find_one({"_id": id})

    def saveState(self, state):
        logText = str(state["_id"]) + "  " + str(len(state["actions"].keys())) + "\n"
        text_file = open("log.txt", "a")
        text_file.write(logText)
        text_file.close()
        self.policy.update({'_id': state["_id"]}, state)
    # def saveAction():
