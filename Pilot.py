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
from PidController import PidController

_deg2met = 110977.			# meters in one degree latitude

class Pilot (Ckpt.Ckpt):			# subclass of the class Ckpt in the file Ckpt

	def __init__(self, database):
		super().__init__('HW4a', True, False)
		self.db = database
		self.stayTime = 0
		self.eleController = PidController(0.1, 0.001, 0.001)
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
			print("pitch: ",flyData.pitch)
			print("roll: ",flyData.roll)

			pidVal = self.eleController.calculatePid(self.altitudeDiff)
			command.elevator = pidVal / 50

			if hasattr(self, 'currentState'):
				self.prevState = self.currentState
				self.stayTime = self.stayTime + 1


			self.currentState = state.State(self.dest_radius, self.speedDiff, self.altitudeDiff, self.headingDiff, self.trajecDiff, self.db)
			if hasattr(self, 'prevState') and self.prevState.isDifferent(self.currentState):
				self.prevState.recordAction(self.currentAction, str(self.currentState.objectID), self.stayTime)
				self.stayTime = 0
				print(self.currentState.calculateAward())
				self.currentAction = self.currentState.chooseAnAction()
				# command.aileron = self.currentAction[0] / 10


			if abs(self.currentState.trajectoryDif) > 50 or abs(self.currentState.headingDif) > 50 or abs(self.currentState.altitudeDif) > 50 or abs(self.currentState.speedDif) > 50:
				if abs(self.currentState.trajectoryDif) > 50:
					print("traj Died")
				elif abs(self.currentState.headingDif) > 50:
					print("head Died")
				elif abs(self.currentState.altitudeDif) > 50:
					print("alt Died")
				else:
					print("speed Died")
				# self.fg.exitFgfs()
				# os.environ['probe1'] = 'endblablabla'
				# os.system('echo $probe1')
				# call(["sudo", "killall", "Python"])
				# os.kill(0, signal.SIGINT)
				# bashCommand = "python start."
				# process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
				# output = process.communicate()[0]

				# self.controller.startNewLearning()
