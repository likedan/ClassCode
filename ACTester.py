# Simple example of exploring the flight dynamics
# import ExploringPilot; a=ExploringPilot.ExploringPilot(); a.start()

import Ckpt as Ckpt

import AC
import random, pickle
import imp, sys, math
import time
from geopy import Point
import calculation as calculation
from PidController import PidController

def rel():
    imp.reload(sys.modules['ACTester'])

class ACTester (Ckpt.Ckpt):			# subclass of the class Ckpt in the file Ckpt

    def __init__(self, tsk = 'HW4a', rc = False, gui = False):
        super().__init__(tsk, rc, gui)
        self.ac = AC.AC()
        self.planned = False
        self.distEnough = False
        self.eleController = PidController(0.1, 0.001, 0.001)
        self.angleController = PidController(0.1, 0.001, 0.001)
        self.passTower = 0
        self.canAdd = True
    def ai(self, fDat, fCmd):

        dist = calculation.getDistance(fDat.latitude,fDat.longitude,37.61703, -122.383585)
        desiredHeading = calculation.getDesiredHeadingToApproachTheTower(fDat.latitude,fDat.longitude)
        currentHeading = fDat.head

        diff = abs(desiredHeading - currentHeading)
        if diff > 180:
            diff = 360 - diff

        if self.canAdd and dist < 0.25:
            self.passTower = self.passTower + 1
            self.canAdd = False

        if dist > 0.3:
            self.canAdd = True

        if self.passTower >= 2:
            self.ac.DO(fDat, fCmd)
        else:
            print("diffff   ", diff)
            print("disttttt   ", dist)
            if fDat.time > 2.0:
                if not self.planned:
                    desLat = 300 - fDat.altitude
                    self.ac.PLAN(fDat, desLat, -10, 200)
                    self.planned = True
                    self.circling = False
                    self.approaching = False
                    self.distE = False
                    self.fin = False
                else:
                    if not self.approaching:
                        if not self.circling:
                            if fDat.altitude <= 500:
                                self.PLAN(1000000, 10)
                                self.DO(fDat, fCmd, False, 0.6)
                                if dist > 1.5:
                                    self.distEnough = True
                                if self.distEnough:
                                    self.circling = True
                                    if calculation.getDegree(desiredHeading - currentHeading) >= 180:
                                        self.ang = -7000
                                    else:
                                        self.ang = 7000
                                    self.PLAN(self.ang, 10)
                                    self.returning = False
                                    print("start circling")
                            else:
                                self.ac.DO(fDat, fCmd)

                        else:
                            print("circl")
                            if self.fin and fDat.altitude < 220:
                                self.ac.DO(fDat, fCmd)
                            else:
                                self.fin = False
                                if self.DO(fDat, fCmd, self.returning, 1) == "DONE":
                                    if not self.returning:
                                        self.PLAN(self.ang, 10)

                                if not self.returning and diff <= 5:
                                    self.returning = True
                                    self.circling = False
                                    self.approaching = True
                                    desLat = 250 - fDat.altitude
                                    self.ac.PLAN(fDat, desLat, -8, 200)
                                    self.buzzing = False
                                    self.lastPositive = False

                                print("returning^^^^^^^^^^^^^^^^^^^^^")
                    else:
                        if fDat.altitude < 200 and fDat.altitude > 250:
                            desLat = 180 - fDat.altitude
                            if desLat > 0:
                                self.ac.PLAN(fDat, desLat, 2, 200)
                            else:
                                self.ac.PLAN(fDat, desLat, -2, 200)
                            self.ac.DO(fDat, fCmd)
                        elif diff >= 30:
                            if calculation.getDegree(desiredHeading - currentHeading) >= 180:
                                self.ang = -7000
                            else:
                                self.ang = 7000
                            self.PLAN(self.ang, 10)
                            self.circling = True
                            self.approaching = False
                            self.height250 = False
                            self.returning = False
                            self.ac.PLAN(fDat, 500, 15, 200)
                            self.fin = True
                        else:
                            if self.ac.DO(fDat, fCmd) == "DONE":
                                self.ac.PLAN(fDat, 20, 0.5, 200)



    def PLAN(self, radius, angle):
        self.returning = False
        self.turning = True
        self.dest_angle = angle
        self.dest_radius = radius * 0.000189393939
        self.wanted_roll = 394500 / abs(radius) + 1.17
        estimatedTrajError = 0.0734 * self.wanted_roll + 0.032
        self.prevDiff = self.dest_radius * 3
        if radius < 0:
            self.wanted_roll = -self.wanted_roll
        print("radius:  ",self.dest_radius)
        self.angleController.setPoint(self.wanted_roll)

        if estimatedTrajError > 8:
            if radius < 0:
                self.wanted_roll = -8000
                self.angleController.setPoint(self.wanted_roll)
            else:
                self.wanted_roll = 8000
                self.angleController.setPoint(self.wanted_roll)

    def DO(self, flyData, command, turnBack, speed):
        if flyData.running and not hasattr(self, 'dest_point'):
            points = calculation.getDestinationCoordinateWith(flyData.latitude, flyData.longitude, flyData.head, self.dest_angle, self.dest_radius)
            self.dest_point = points[0]
            self.center_point = points[1]
            self.last_altitude = flyData.altitude
            self.last_roll = flyData.roll
            self.dest_heading = flyData.head
            command.throttle = 0.6

        if hasattr(self, 'center_point'):
            self.trajecDiff = calculation.getTrajectoryDifference(flyData.latitude, flyData.longitude, self.center_point, self.dest_radius)
            self.headingDiff = calculation.getHeadingDifference(flyData.latitude, flyData.longitude, self.center_point, self.dest_radius, flyData.head)
            self.altitudeDiff = flyData.altitude - self.last_altitude
            self.last_altitude = flyData.altitude
            print("Roll",flyData.roll)

            eleValue = self.eleController.calculatePid(self.altitudeDiff)
            if eleValue > 0.15:
                eleValue = 0.15
            elif eleValue < 0:
                eleValue = eleValue - 0.15
            command.elevator = eleValue

            angleValue = self.angleController.calculateAngelPid(flyData.roll)
            angleValue = angleValue
            if angleValue > 0.3:
                angleValue = 0.3
            elif angleValue < -0.3:
                angleValue = -0.3
            command.aileron = angleValue / 4

            self.currentDiff = calculation.getDistanceDifference(flyData.latitude, flyData.longitude, self.dest_point)

            if self.currentDiff > self.prevDiff and self.currentDiff < abs(self.dest_radius) / 4:
                if not turnBack:
                    return "DONE"
                self.angleController.setPoint(0)
                self.returning = True
            self.prevDiff = self.currentDiff
            if self.returning and abs(flyData.roll) < 2:
                return "DONE"
    def DOB(self, flyData, command, turnBack, speed):
        if flyData.running and not hasattr(self, 'dest_point'):
            points = calculation.getDestinationCoordinateWith(flyData.latitude, flyData.longitude, flyData.head, self.dest_angle, self.dest_radius)
            self.dest_point = points[0]
            self.center_point = points[1]
            self.last_altitude = flyData.altitude
            self.last_roll = flyData.roll
            self.dest_heading = flyData.head
            command.throttle = 0.6

        if hasattr(self, 'center_point'):
            self.trajecDiff = calculation.getTrajectoryDifference(flyData.latitude, flyData.longitude, self.center_point, self.dest_radius)
            self.headingDiff = calculation.getHeadingDifference(flyData.latitude, flyData.longitude, self.center_point, self.dest_radius, flyData.head)
            self.altitudeDiff = flyData.altitude - self.last_altitude
            self.last_altitude = flyData.altitude
            print("Roll",flyData.roll)

            eleValue = self.eleController.calculatePid(self.altitudeDiff)
            if eleValue > 0.17:
                eleValue = 0.17
            elif eleValue < 0:
                eleValue = eleValue - 0.17
            command.elevator = eleValue

            angleValue = self.angleController.calculateAngelPid(flyData.roll)
            angleValue = angleValue
            if angleValue > 0.12:
                angleValue = 0.12
            elif angleValue < -0.12:
                angleValue = -0.12
            command.aileron = angleValue

            self.currentDiff = calculation.getDistanceDifference(flyData.latitude, flyData.longitude, self.dest_point)

            if self.currentDiff > self.prevDiff and self.currentDiff < abs(self.dest_radius) / 4:
                if not turnBack:
                    return "DONE"
                self.angleController.setPoint(0)
                self.returning = True
            self.prevDiff = self.currentDiff
            if self.returning and abs(flyData.roll) < 2:
                return "DONE"
