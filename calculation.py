import math


def getDesiredHeadingToApproachTheTower(lat, lon):
    supposed_bearing = getBearingBetweenTwoPoints(lat, lon, 37.61703, -122.383585)
    return supposed_bearing

def getDesiredHeadingToApproachTurningPoint(lat, lon):
    supposed_bearing = getBearingBetweenTwoPoints(lat, lon, 37.643863677978516, -122.43621063232422)
    return supposed_bearing

def getDesiredHeadingToApproachModifyingPoint(lat, lon):
    supposed_bearing = getBearingBetweenTwoPoints(lat, lon, 37.63372802734375,  -122.40889739990234)
    return supposed_bearing

def getDesiredHeadingToApproachLandingPoint(lat, lon):
    supposed_bearing = getBearingBetweenTwoPoints(lat, lon, 37.613555908203125,  -122.35719299316406)
    return supposed_bearing

def getTrajectoryDifference(lat, lon, centerPoint, destMiles):
    return distance.distance(Point(lat, lon), centerPoint).miles - destMiles

def getDistanceDifference(lat, lon, centerPoint):
    return distance.distance(Point(lat, lon), centerPoint).miles

def getDistance(lat, lon, lat1, lon1):
    return math.sqrt(((lon1 - lon) / 0.794) * ((lon1 - lon) / 0.794) + (lat1 - lat) * (lat1 - lat)) * 50

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
