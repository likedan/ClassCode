# Simple example of taxiing as scripted behavior
# import Pilot; a=Pilot.Pilot(); a.start()
import math
import calculation as calculation
import Ckpt as Ckpt
import Utilities as Utilities
from PidController import PidController
from geopy import Point
import state
import imp, sys
import database

def rel():
	imp.reload(sys.modules['Pilot'])

_deg2met = 110977.			# meters in one degree latitude

class Pilot (Ckpt.Ckpt):			# subclass of the class Ckpt in the file Ckpt

	def __init__(self, database):
		super().__init__('HW4a', True, False)
		self.db = database

	def setRadiusAndAngle(self, radius, angle):
		self.dest_angle = angle
		self.dest_radius = radius * 0.000189393939

	def ai(self, flyData, command):
		# calculate the dest location
		if flyData.running and not hasattr(self, 'dest_point'):
			points = calculation.getDestinationCoordinateWith(flyData.latitude, flyData.longitude, flyData.head, self.dest_angle, self.dest_radius)
			print(points)
			self.dest_point = points[0]
			self.center_point = points[1]
			self.dest_speed = flyData.kias
			self.dest_altitude = flyData.altitude
			self.dest_heading = flyData.head

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
			self.currentState = state.State(self.dest_radius, self.speedDiff, self.altitudeDiff, self.headingDiff, self.trajecDiff, self.db)

			if hasattr(self, 'prevState') and self.prevState.isDifferent(self.currentState):
				self.currentState.chooseAnAction()
				print("working")
		# '''Override with the Pilot decision maker, args: fltData and cmdData from Utilities.py'''
		# print("time : " , flyData.time)
		# print("air speed : " , flyData.kias)
		# print("altitude : " , flyData.altitude)
		# print("head : " , flyData.head)
		# print("pitch : " , flyData.pitch)
		# print("roll : " , flyData.roll)
		#
		# print("running : ", flyData.running)

#
# 		currentTickLength = 0
# 		if self.duration:
# 			currentTickLength = flyData.time - self.strtTime - self.duration
#
# 		self.duration = flyData.time - self.strtTime
# 		if abs(flyData.roll) > 5.:			# first check for excessive roll
# 			print('Points lost for tipping; {:.1f} degrees at {:.1f} seconds'.format(flyData.roll, self.duration))
#
# 		if currentTickLength == 0:
# 			return 'noop' # something dummy
#
# 		print('------------------------------------------------------')
# 		print('Current time = {:.1f} seconds, actual = {:.1f} value'.format(self.duration, flyData.time))
#
# # speed calculation start
# 		currentSpeed = 0
# 		newLocation = [flyData.latitude, flyData.longitude]
#
# 		if self.lastKnownLocation:
# 			currentSpeed = (_deg2met * Utilities.dist(self.lastKnownLocation, newLocation)) / currentTickLength
#
# 		self.lastKnownLocation = newLocation
# # speed calculation end
#
# # angle calculation start
# 		startLat = math.radians(newLocation[0])
# 		startLong = math.radians(newLocation[1])
# 		endLat = math.radians(self.waypoints[self.nextWayPointIndex][0])
# 		endLong = math.radians(self.waypoints[self.nextWayPointIndex][1])
#
# 		dLong = endLong - startLong
#
# 		dPhi = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))
# 		if abs(dLong) > math.pi:
# 			if dLong > 0.0:
# 				dLong = -(2.0 * math.pi - dLong)
# 			else:
# 				dLong = (2.0 * math.pi + dLong)
#
# # problems here
# 		bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0
# 		distanceFromNextWaypoint = Utilities.dist(self.lastKnownLocation, self.waypoints[self.nextWayPointIndex]) * _deg2met
# 		print('Distance to next waypoint {:.5f} meters'.format(distanceFromNextWaypoint))
#
# # angle calculation end
# 		if(distanceFromNextWaypoint < 50.):
# 			self.throttlePidController.set_point = self.speedTurn
# 		else:
# 			self.throttlePidController.set_point = self.speedMax
# 		pidValue = self.throttlePidController.calculatePid(currentSpeed)
# 		print('Current {:.2f} / Expected {:.2f} / Throttle pidValue = {:.5f}'.format(currentSpeed, self.throttlePidController.set_point, pidValue))
# 		command.throttle = (pidValue / self.throttlePidController.set_point)
#
# # rudder PidController start
#
# 		self.rudderPidController.set_point = bearing
# 		rudderValue = self.rudderPidController.calculateAngelPid(flyData.head)
#
# 		if(rudderValue > 0.5):
# 			command.rudder = 0.5
# 		elif(rudderValue < -0.5):
# 			command.rudder = -0.5
# 		else:
# 			command.rudder = rudderValue * 2
# 		print('Heading {:.2f} / Waypoint {:.2f} / Rudder pidValue = {:.5f}'.format(flyData.head, bearing, command.rudder))
# # rudder PidController end
#
# 		if (distanceFromNextWaypoint < 1.):
# 			print("moving to next waypoint")
# 			self.nextWayPointIndex += 1
# 			#print(sf.nextWayPointIndex)
# 			self.correctWay = False
# 			self.throttlePidController = PidController(1, 0.001, 0.01)
# 			self.rudderPidController = PidController(0.01, 0.0001, 0.001)
#
# 		if self.nextWayPointIndex == len(self.waypoints):
# 			return 'stop'
