import ClassCode.Utilities
import math
import PilotUtils

TOLERANCE = 2.0
FINAL_TOLERANCE = 2.0

class Planner:
	def __init__(sf, waypoints):
		sf.waypoints = waypoints
		sf.shouldResetIntegral = False

	def updatePosition (sf, lat, lon):
		sf.shouldResetIntegral = False
		sf.currPosition = [lat, lon]
		if len(sf.waypoints) == 1:
			return
		dist = PilotUtils.distanceApproximate(sf.currPosition[0], sf.currPosition[1], sf.waypoints[0][0], sf.waypoints[0][1])
		if dist < TOLERANCE:
			# Pop one waypoint
			sf.waypoints.pop(0)
			sf.shouldResetIntegral = True
			print('>>>>>>> REACHED waypoint <<<<<<<')
			print('>>>>>>> REACHED waypoint <<<<<<<')
			print('>>>>>>> REACHED waypoint <<<<<<<')
			print('>>>>>>> REACHED waypoint <<<<<<<')
			print('>>>>>>> REACHED waypoint <<<<<<<')
			print('>>>>>>> REACHED waypoint <<<<<<<')
			print('>>>>>>> REACHED waypoint <<<<<<<')
			print(sf.waypoints)

	def getTargetHeading (sf):
		return PilotUtils.desiredHeadingCalib(sf.currPosition[0], sf.currPosition[1], sf.waypoints[0][0], sf.waypoints[0][1])

	def shouldStop (sf):
		# Less than 5 meters from the target
		if len(sf.waypoints) == 1 and PilotUtils.distanceApproximate(sf.currPosition[0], sf.currPosition[1], sf.waypoints[0][0], sf.waypoints[0][1]) < FINAL_TOLERANCE:
			return True
		else:
			return False
