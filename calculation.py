
from geopy import Point
from geopy.distance import distance, VincentyDistance
from geopy import distance
from geopy.distance import vincenty
from geographiclib.geodesic import Geodesic
import math

def getDestinationCoordinateWith(lat, lon, bearing, changeBearing, destMiles):
    startPoint = Point(lat, lon)
    circleCenterDirection = 0
    if destMiles < 0:
        circleCenterDirection = getDegree(bearing - 90)
    elif destMiles > 0:
        circleCenterDirection = getDegree(bearing + 90)
    circleCenter = VincentyDistance(miles = destMiles).destination(startPoint, circleCenterDirection)
    return (VincentyDistance(feet = destMiles).destination(circleCenter, getDegree(circleCenterDirection - 180 + changeBearing)), circleCenter)

def getTrajectoryDifference(lat, lon, centerPoint, destMiles):
    return distance.distance(Point(lat, lon), centerPoint).miles - destMiles

def getHeadingDifference(lat, lon, centerPoint, destMiles, currentHeading):
    circleCenterDirection = 0
    if destMiles < 0:
        circleCenterDirection = getDegree(currentHeading - 90)
    elif destMiles > 0:
        circleCenterDirection = getDegree(currentHeading + 90)
    supposed_bearing = getBearingBetweenTwoPoints(lat, lon, centerPoint.latitude, centerPoint.longitude)
    return supposed_bearing - circleCenterDirection

def getBearingBetweenTwoPoints(lat1, lon1, lat2, lon2):

	rlat1 = math.radians(lat1)
	rlat2 = math.radians(lat2)
	rlon1 = math.radians(lon1)
	rlon2 = math.radians(lon2)
	dlon = math.radians(lon2-lon1)

	b = math.atan2(math.sin(dlon)*math.cos(rlat2),math.cos(rlat1)*math.sin(rlat2)-math.sin(rlat1)*math.cos(rlat2)*math.cos(dlon)) # bearing calc
	bd = math.degrees(b)
	br,bn = divmod(bd+360,360) # the bearing remainder and final bearing

	return bn

def getDegree(degree):
    if degree > 360:
        return degree - 360
    if degree < 0:
        return degree + 360
    return degree
