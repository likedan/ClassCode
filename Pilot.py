# Simple example of taxiing as scripted behavior
# import Pilot; a=Pilot.Pilot(); a.start()
import math
from geopy import Point
import calculation as calculation
import Ckpt as Ckpt
import Utilities as Utilities
import state
import imp, sys
import database
import time
import os
import sys
from subprocess import call

_deg2met = 110977.			# meters in one degree latitude

class Pilot (Ckpt.Ckpt):			# subclass of the class Ckpt in the file Ckpt

	def __init__(self, database):
		super().__init__('HW4a', True, False)
		self.db = database
		self.stayTime = 0
		print("new Pilot")

	def setRadiusAndAngle(self, radius, angle):
		self.dest_angle = angle
		self.dest_radius = radius * 0.000189393939

	def ai(self, flyData, command):
		# calculate the dest location
		if flyData.running and not hasattr(self, 'dest_point'):
			points = calculation.getDestinationCoordinateWith(flyData.latitude, flyData.longitude, flyData.head, self.dest_angle, self.dest_radius)
			self.dest_point = points[0]
			self.center_point = points[1]
			self.dest_speed = flyData.kias
			self.dest_altitude = flyData.altitude
			self.dest_heading = flyData.head
			self.currentAction = (0, 0)

		if hasattr(self, 'center_point'):
			self.trajecDiff = calculation.getTrajectoryDifference(flyData.latitude, flyData.longitude, self.center_point, self.dest_radius)
			self.headingDiff = calculation.getHeadingDifference(flyData.latitude, flyData.longitude, self.center_point, self.dest_radius, flyData.head)
			self.altitudeDiff = self.dest_altitude - flyData.altitude
			self.speedDiff = self.dest_speed - flyData.kias
			# print("traj: ",self.trajecDiff)
			# print("head: ",self.headingDiff)
			# print("speed: ",self.speedDiff)
			# print("altitude: ",self.altitudeDiff)
			if hasattr(self, 'currentState'):
				self.prevState = self.currentState
				self.stayTime = self.stayTime + 1


			self.currentState = state.State(self.dest_radius, self.speedDiff, self.altitudeDiff, self.headingDiff, self.trajecDiff, self.db)
			if hasattr(self, 'prevState') and self.prevState.isDifferent(self.currentState):
				self.prevState.recordAction(self.currentAction, str(self.currentState.objectID), self.stayTime)
				print("different State")
				self.stayTime = 0
				self.currentAction = self.currentState.chooseAnAction()
				command.throttle = self.currentAction[0] / 5
				command.rudder = self.currentAction[1] / 5
			if abs(self.currentState.trajectoryDif) > 25 or abs(self.currentState.headingDif) > 25 or abs(self.currentState.altitudeDif) > 25 or abs(self.currentState.speedDif) > 25:
				self.fg.exitFgfs()
				os.environ['probe1'] = 'endblablabla'
				os.system('echo $probe1')
				call(["sudo", "killall", "Python"])
				# os.kill(0, signal.SIGINT)
				# bashCommand = "python start."
				# process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
				# output = process.communicate()[0]

				# self.controller.startNewLearning()
