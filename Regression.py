# demonstrate regression by ordinary least squares curve fitting
# requires the packages numpy and matplotlib (easily found on the web)

# USE: import lsf2; a=lsf2.lsf() + several <cr>; a.redo()
# both lsf and redo can be given aguments n=#sample, e=Gaussian noise std.dev

# You can try different target functions (targetFcn);
# the global targetCoefs is not used in computations, only to set the window title
# There a selection of basis functions (basisFcns) that you can change as you wish
# Most of the code is to support a nice demo except:
#		matrixF creates the matrix to be inverted
#		the last line in samp calls the numpy least squares solver lstsq
#		y0 is the vector of dependent values

import numpy as np
import matplotlib.pyplot as plt
import pickle
import pathlib
import os
import math

import imp, sys
def rel():
	imp.reload(sys.modules['Regression'])

# (fCmd.throttle, fDat.pitch, fDat.altitude, fDat.kias, fDat.rpm, fDat.vspeed, fDat.xaccel, fDat.zaccel, fDat.time)

def basisFcns(x):
	(vh, vv, gh, gv, rpm) = x
	return (1.,
		vh, vh**2,
		vv, vv**2,
		gh, gv,
		rpm)

def matrixF(x):
	nfcns = len(basisFcns((1, 1, 1, 1, 1)))
	f = np.empty((len(x), nfcns), dtype=float)
	bfs = list(map(basisFcns, x))
	for i in range(nfcns):
		f[:, i] = list(p[i] for p in bfs)
	#print(np.shape(f))
	return f

# List files
dir = 'output'
bil_files = list(p for p in pathlib.Path(dir).iterdir() if p.is_file() and not p.name.endswith('.DS_Store'))
total = len(bil_files)

data = []
for bil in bil_files:
	with open(str(bil), 'rb') as f:
		data = data + pickle.load(f)

lastTime = 0.
lastAltitude = 0.
smoothVSpeed = 0.
def resolveCoordFrame(x):
	global lastTime, lastAltitude, smoothVSpeed
	(throttle, pitch, altitude, kias, rpm, vspeed_fps, xaccel, zaccel, time) = x
	if time < lastTime:
		lastTime = time - 0.1
		lastAltitude = altitude
		smoothVSpeed = vspeed_fps
	# vspeed = 0.592484 * vspeed_fps		# Knots
	estimatedVSpeed = (altitude - lastAltitude) / (time - lastTime)
	lastTime = time
	lastAltitude = altitude
	smoothVSpeed = smoothVSpeed * 0.7 + estimatedVSpeed * 0.3
	vspeed = 0.59248 * smoothVSpeed
	hspeed = math.sqrt(max(0, kias**2 - vspeed**2))
	v_ned = np.array([vspeed, hspeed])
	pitch_rad = math.radians(pitch)		# Along pitch
	up_rad = math.radians(pitch + 90)	# Upwards in pilot orientation
	pitch_dir = np.array([math.sin(pitch_rad), math.cos(pitch_rad)])
	up_dir = np.array([math.sin(up_rad), math.cos(up_rad)])
	# Plane frame
	vh = np.dot(v_ned, pitch_dir)
	vv = np.dot(v_ned, up_dir)
	grav_ned = np.array([-1.0, 0.0])		# Gravity is vertically downwards
	gh = np.dot(grav_ned, pitch_dir)
	gv = np.dot(grav_ned, up_dir)
	return (vh, vv, gh, gv, rpm)

def getZaccel(x):
	(throttle, pitch, altitude, kias, rpm, vspeed_fps, xaccel, zaccel, time) = x
	return zaccel

def getXaccel(x):
	(throttle, pitch, altitude, kias, rpm, vspeed_fps, xaccel, zaccel, time) = x
	return xaccel

def validData(x):
	(throttle, pitch, altitude, kias, rpm, vspeed_fps, xaccel, zaccel, time) = x
	return vspeed_fps < 250 and vspeed_fps > -250

print(len(data))

data = list(filter(validData, data))
resolvedData = list(map(resolveCoordFrame, data.copy()))
f = matrixF(resolvedData)

# Manually calculate acceleration
prevVv = 0
prevTime = 0
for i in range(len(data)):
	l = list(data[i])
	#l[7] = (resolvedData[i][1] - prevVv) / (data[i][8] - prevTime)
	l[7] = -(l[7] + 32)
	#if data[i][8] > prevTime:
	data[i] = tuple(l)
	prevVv = resolvedData[i][1]
	prevTime = data[i][8]

y = list(map(getXaccel, data.copy()))
#print(np.shape(y))
coeffs, residuals, rank, s = np.linalg.lstsq(f, y)
print(residuals / len(data))
print('Coefficients: [{}]'.format(', \n'.join(map(lambda x: str(x), coeffs.tolist()))))

error = 0.
# Evaluate some accelerations
for i in range(len(data)):
	target = getXaccel(data[i])
	inputVal = np.asarray(basisFcns(resolveCoordFrame(data[i])))
	estimate = np.dot(inputVal, coeffs)
	#print('Target: {}, estimate: {}'.format(target, estimate))
	error += abs(target - estimate) / abs(target)

print('Avg percentage error: {}'.format(error / len(data)))
