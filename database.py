#!/usr/bin/env python
import datetime
import pymongo
import state
from pymongo import MongoClient

class Database:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        print ("Connected successfully!!!")
        self.db = client['Policy']
        self.db["StatesTable"].remove()
        self.policy = self.db['StatesTable']
    def addNewStates(self, state):
        stateObject = {"radius": state.radius, "speed": state.speedDif, "altitude": state.altitudeDif, "heading": state.headingDif, "trajectory": state.trajectoryDif, "award": state.calculateAward()}
        state_id = self.policy.insert_one(stateObject).inserted_id
        return state_id

    # return None if state don't exist
    def getState(self, state):
        state = self.policy.find_one({"radius": state.radius, "speed": state.speedDif, "altitude": state.altitudeDif, "heading": state.headingDif, "trajectory": state.trajectoryDif})
        return state

    def getStateDict(self, id):
        return self.policy.find_one({"_id": id})

    def saveState(self, state):
        self.policy.update({'_id': state["_id"]},state)
    # def saveAction():


# # add a pin without detail info
#     def addPinID(self, id):
#         if self.pins.find_one({"_id": id}) == None:
#             info = {"_id": id, "isPopulated" : False}
#             self.pins.insert_one(info)
#             print "inserted"
#
# # get random user that haven't been populated
#     def getAnEmptyUser(self):
#         try:
#             return self.users.find_one({"isPopulated" : False})
#         except Exception as e:
#             print "no pin"
#             return None
#
# # add the information on a User and add the pinIDs
#     def addUserInfo(self, id, info):
#         information = self.users.find_one({"_id": id})
#         print information
#         if information != None and information["isPopulated"] == False:
#             information["isPopulated"] = True
#             information['nickName'] = info['nickName']
#             information["boardCount"] = info["boardCount"]
#             information["pinCount"] = info["pinCount"]
#             information["likeCount"] = info["likeCount"]
#             information["followingCount"] = info["followingCount"]
#             information["followerCount"] = info["followerCount"]
#             if len(info["boardList"]) > 0:
#                 information["boardList"] = info["boardList"]
#             if len(info["likeDict"]) > 0:
#                 information["likeDict"] = info["likeDict"].keys()
#                 pinList = []
#                 for pin in information["likeDict"]:
#                     if self.pins.find_one({"_id": pin}) == None:
#                         pinList.append({"_id": pin, "isPopulated" : False})
#                 if len(pinList) > 0 :
#                     self.pins.insert(pinList)
#                 print pinList
#
#             if len(info["pinDict"]) > 0:
#                 information["pinDict"] = info["pinDict"].keys()
#                 pinList = []
#                 for pin in information["pinDict"] :
#                     if self.pins.find_one({"_id": pin}) == None:
#                         pinList.append({"_id": pin, "isPopulated" : False})
#                 if len(pinList) > 0 :
#                     self.pins.insert(pinList)
#                 print pinList
#
#             self.users.update({'_id': id}, information)
#
# # print db
# collection = db.my_collection
# doc = {"name":"Alberto","surname":"Negron","twitter":"@Altons"}
# print collection
# collection.insert(doc)
# print 'done'
# print post_id
