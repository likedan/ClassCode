import math

def distanceAccurate(lat1, lon1, lat2, lon2):
	'''Computes the distance between two points given in latitude and longitude, using the actual arc around the earth.'''
	# translated from javascript found at http://www.movable-type.co.uk/scripts/latlong.html
	earthRadius = 6371000;     #radius of the earth, in meters
	φ1 = math.radians(lat1)
	φ2 = math.radians(lat2)
	Δφ = math.radians(lat2 - lat1)
	Δλ = math.radians(lon2 - lon1)

	a = math.sin(Δφ / 2.0) * math.sin(Δφ / 2.0) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2.0) * math.sin(Δλ / 2.0)
	c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a));

	return earthRadius * c;

def distanceLat(lat1,lat2):
	py = lat1 * 110989.25
	cy = lat2 * 110989.25
	return cy - py

def distanceLon(lon1,lon2):
	px = lon1 * 88285.43
	cx = lon2 * 88285.43
	return cx - px

def distanceApproximate(lat1, lon1, lat2, lon2):
	'''Computes the approximate distance between two points given in latitude and longitude, using ratios that hold local to the airport.'''
	latDist = distanceLat(lat1,lat2)
	lonDist = distanceLon(lon1,lon2)
	return math.sqrt((lonDist*lonDist) + (latDist*latDist))

def desiredHeadingCalib (currLat, currLon, targetLat, targetLon):
	#Calculates and returns desired heading (in degrees 0-360) from current coords and target coords
    latDist = distanceLat(currLat, targetLat) #Like "y" displacement
    lonDist = distanceLon(currLon, targetLon) #Like "x" displacement

    if(lonDist > 0): #If heading East
        desiredHeading = 90 - math.degrees(math.atan(latDist / lonDist))
    else:            #If heading West
        desiredHeading = -90 - math.degrees(math.atan(latDist / lonDist))

    desiredHeading = 90 - math.degrees(math.atan2(latDist, lonDist))

    return desiredHeading
