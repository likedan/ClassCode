# Simple example of taxiing as scripted behavior
# import Pilot; a=Pilot.Pilot(); a.start()
import math
from geopy import Point
import calculation as calculation
import time
from PidController import PidController
import Ckpt as Ckpt
import Utilities as Utilities


_deg2met = 110977.			# meters in one degree latitude

class Pilot (Ckpt.Ckpt):			# subclass of the class Ckpt in the file Ckpt

	def __init__(self, database):
		super().__init__('HW4a', True, False)
		self.db = database
		self.stayTime = 0
		self.eleController = PidController(0.1, 0.001, 0.001)
		self.angleController = PidController(0.1, 0.001, 0.001)
		self.turning = False
		print("new Pilot")

	def PC(self, radius, angle):
		dest_angle = angle
		dest_radius = radius * 0.000189393939
		wanted_roll = 394500 / abs(radius) + 1.17
		estimatedTrajError = 0.0734 * wanted_roll + 0.032
		prevDiff = dest_radius * 3
		if estimatedTrajError > 10:
			if radius < 0:
				return (-6500, angle)
			else:
				return (6500, angle)
		return "OK"

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
				self.wanted_roll = -6500
				self.angleController.setPoint(self.wanted_roll)
			else:
				self.wanted_roll = 6500
				self.angleController.setPoint(self.wanted_roll)


	def setRadiusAndAngle(self, radius, angle):
		self.dest_angle = angle
		self.dest_radius = radius * 0.000189393939
		self.wanted_roll = 394500 / abs(radius) + 1.17
		estimatedTrajError = 0.0734 * self.wanted_roll + 0.032
		self.prevDiff = self.dest_radius * 3
		if radius < 0:
			self.wanted_roll = -self.wanted_roll
		print("radius:  ",self.dest_radius)

		self.angleController.setPoint(self.wanted_roll)
		self.returning = False

		if estimatedTrajError > 8:
			if radius < 0:
				self.wanted_roll = -6500
				self.angleController.setPoint(self.wanted_roll)
			else:
				self.wanted_roll = 6500
				self.angleController.setPoint(self.wanted_roll)

	def ai(self, flyData, command):
		if (self.turning):
			if self.DO(flyData, command) == "DONE":
				self.turning = False
		# calculate the dest location

	def DO(self, flyData, command):
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
			if eleValue > 0.1:
				eleValue = 0.1
			elif eleValue < 0:
				eleValue = eleValue - 0.15
			command.elevator = eleValue

			angleValue = self.angleController.calculateAngelPid(flyData.roll)
			angleValue = angleValue
			if angleValue > 0.3:
				angleValue = 0.3
			elif angleValue < -0.3:
				angleValue = -0.3
			command.aileron = angleValue / 5

			self.currentDiff = calculation.getDistanceDifference(flyData.latitude, flyData.longitude, self.dest_point)

			if self.currentDiff > self.prevDiff and self.currentDiff < abs(self.dest_radius) / 4:
				print("finishTurning")
				self.angleController.setPoint(0)
				self.returning = True
			self.prevDiff = self.currentDiff
			print("diff: ",calculation.getDistanceDifference(flyData.latitude, flyData.longitude, self.dest_point))
			if self.returning and abs(flyData.roll) < 2:
				return "DONE"
