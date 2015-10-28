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
        # self.db["TrajectoryTable"].remove()
        self.policy = self.db['TrajectoryTable']

    def addNewRadius(self, radius):
        stateObject = {"radius": radius}
        self.policy.insert_one(stateObject)

    def removeRadius(self, radius):
        self.policy.remove({"radius": radius})
    # return None if state don't exist
    def getRadius(self, radius):
        state = self.policy.find_one({"radius": radius})
        return state

    def saveRadius(self, radiusState):
        self.policy.update({'_id': radiusState["_id"]}, radiusState)
    # def saveAction():
