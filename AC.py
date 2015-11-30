import PID
import numpy as np
import math

def flight_generator(fDat, deltaAlt, angle, finalSpeed, getFields):
	angle = abs(angle)
	if deltaAlt < 0:
		angle =- angle
		direction = -1
	else:
		direction = 1

	ACC_FACTOR = 1.26

	fDat = None
	fCmd = None
	time_span = 0.2
	prev_time = 0
	lastAltitude = 0.
	smoothVSpeed = 0.
	def updateFlightParams():
		nonlocal time_span, fDat, fCmd, prev_time, lastAltitude, smoothVSpeed
		(fDat, fCmd) = getFields()
		if fDat.time > prev_time:
			time_span = fDat.time - prev_time
			prev_time = fDat.time
		estimatedVSpeed = (fDat.altitude - lastAltitude) / time_span
		prev_time = fDat.time
		lastAltitude = fDat.altitude
		smoothVSpeed = smoothVSpeed * 0.7 + estimatedVSpeed * 0.3

	updateFlightParams()
	pitchPID = PID.PID(5.0 / 180, 10.0 / 180, 0.1 / 180, fDat.pitch - 0., fDat.time)
	rollPID = PID.PID(1.8 / 180, 0.25 / 180, 1.0 / 180, fDat.roll - 0., fDat.time)
	throttlePID = PID.PID(0.5 / 100, 0.1 / 100, 0.2 / 100, 0., fDat.time)

	lastTargetPitch = 0.
	def holdPitch(targetPitch):
		nonlocal lastTargetPitch
		if abs(targetPitch - lastTargetPitch) > 20.: pitchPID.resetIntegral()
		lastTargetPitch = targetPitch
		pitchError = fDat.pitch - targetPitch
		pitchControl = pitchPID.controlValue(pitchError, fDat.time)
		fCmd.elevator = max(min(pitchControl, 1.0), -1.0)

	lastTargetRoll = 0.
	def holdRoll(targetRoll):
		nonlocal lastTargetRoll
		if abs(targetRoll - lastTargetRoll) > 10.: rollPID.resetIntegral()
		lastTargetRoll = targetRoll
		rollError = targetRoll - fDat.roll
		rollControl = rollPID.controlValue(rollError, fDat.time)
		fCmd.aileron = max(min(rollControl, 1.0), -1.0)

	lastTargetRpm = 0.
	def holdRpm(targetRpm):
		nonlocal lastTargetRpm
		if abs(targetRpm - lastTargetRpm) > 100.: throttlePID.resetIntegral()
		lastTargetRpm = targetRpm
		rpmError = targetRpm - fDat.rpm
		throttleControl = throttlePID.controlValue(rpmError, fDat.time)
		fCmd.throttle = max(min(throttleControl, 1.0), 0.0)

	# Get into level flight first
	while abs(fDat.pitch) > 1.5:
		yield
		updateFlightParams()
		holdPitch(0.)
		holdRoll(0.)
		holdRpm(2000.)
	print('In level flight')

	# Start our maneuvre
	finalAltitude = fDat.altitude + deltaAlt
	startingSpeed = fDat.kias

	def getVelocityNED():
		vspeed = 0.59248 * smoothVSpeed
		hspeed = math.sqrt(max(0, fDat.kias**2 - vspeed**2))
		return np.array([vspeed, hspeed])

	if abs(deltaAlt) > 2000:
		NUM_DIV = 15.
	else:
		if abs(deltaAlt) > 1000:
			NUM_DIV = 8.
		else:
			if abs(deltaAlt) > 300:
				NUM_DIV = 5.
			else:
				NUM_DIV = 3.
	def getTargetVelocityNED(leveling=False):
		if leveling:
			diff = fDat.altitude - finalAltitude
			if diff > 5.:
				targetAngle = -5.
			else:
				if diff < -5.:
					targetAngle = 5.
				else:
					targetAngle = 0.
			speed = finalSpeed
		else:
			proportionComplete = min(max(1. - abs(fDat.altitude - finalAltitude) / abs(deltaAlt), 0), 1)**2
			# Final part of journey?
			if proportionComplete > (1. - 1. / NUM_DIV):
				# Linear interpolate angle
				targetAngle = angle * (1. - proportionComplete) * NUM_DIV
			else:
				targetAngle = angle
			# Linear interpolate speed then deduce velocity
			speed = startingSpeed + (finalSpeed - startingSpeed) * proportionComplete
		# print(proportionComplete, targetAngle, speed)
		return (np.array([np.sin(math.radians(targetAngle)), np.cos(math.radians(targetAngle))]) * speed, targetAngle)

	def findRpmForPitch(pitch, accNED, fDat, horiz=False, angle=0):
		v_ned = getVelocityNED()
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
		# Use (vh, vv, gh, gv) to find rpm
		targetXacc = np.dot(accNED, pitch_dir)
		targetZacc = np.dot(accNED, up_dir)

		basis = (1.,
			vh, vh**2,
			vv, vv**2,
			gh, gv)

		ZaccEqn = [-39.457138442376305,
0.36013477615131795,
-0.0005382009773636557,
-2.2171728829032027,
0.016280247218062188,
-6.559542260860914,
11.87151652643883]
		ZaccConst = np.dot(basis, ZaccEqn)
		ZaccRpmCoeff = 0.003876614964535742

		XaccEqn = [-0.29724129399643046,
-0.022687622332763693,
-7.455403017804464e-05,
-0.1881044060078697,
0.005276751589367672,
0.17228416716564804,
1.7340981651693024]
		XaccConst = np.dot(basis, XaccEqn)
		XaccRpmCoeff = 0.006465015439070549

		if horiz:
			# Vector arithmetic tells us the closest point is
			rpm = (ZaccRpmCoeff * targetZacc - ZaccRpmCoeff * ZaccConst + XaccRpmCoeff * targetXacc - XaccRpmCoeff * XaccConst) / (ZaccRpmCoeff**2 + XaccRpmCoeff**2)
			rpm = max(min(rpm, 2500), 1500)
			x_plane = fDat.rpm * XaccRpmCoeff + XaccConst
			z_plane = fDat.rpm * ZaccRpmCoeff + ZaccConst
			x_ned = math.cos(pitch_rad) * x_plane + math.sin(pitch_rad) * z_plane
			z_ned = math.sin(pitch_rad) * x_plane + math.cos(pitch_rad) * z_plane
			diff = (accNED[0] - z_ned)**2
		else:
			# Rpm such that acceleration is in the direction of desired acceleration
			x_r = (targetZacc / targetXacc - ZaccConst + ZaccRpmCoeff / XaccRpmCoeff * XaccConst) * XaccRpmCoeff / ZaccRpmCoeff
			rpm = max(min((x_r - XaccConst) / XaccRpmCoeff, 2500), 1500)
			x_plane = fDat.rpm * XaccRpmCoeff + XaccConst
			z_plane = fDat.rpm * ZaccRpmCoeff + ZaccConst
			x_ned = math.cos(pitch_rad) * x_plane + math.sin(pitch_rad) * z_plane
			z_ned = math.sin(pitch_rad) * x_plane + math.cos(pitch_rad) * z_plane
			diff = abs(math.degrees(math.atan2(z_ned, x_ned)) - angle)

		return (rpm, diff)

	while (finalAltitude - fDat.altitude) * direction > 5.:
		yield
		updateFlightParams()
		# print("Target velocity: {}".format(getTargetVelocityNED()))
		vel_ned = getVelocityNED()
		(vel_t_ned, targetAngle) = getTargetVelocityNED()
		vel_diff = vel_t_ned - vel_ned
		accNED = vel_diff / ACC_FACTOR
		# Figure out best pitch
		def pitchSteps(pitch):
			for x in range(-15, 16):
				yield float(x) / 2. + pitch
		bestDeltaAcc = float("inf")
		bestPitch = 0.
		bestRpm = 2000.
		for p in pitchSteps(fDat.pitch):
			(tempRpm, diff) = findRpmForPitch(p, accNED, fDat, targetAngle)
			if diff < bestDeltaAcc:
				bestDeltaAcc = diff
				bestRpm = tempRpm
				bestPitch = p

		print("acc_t: {}, pitch_t: {:.4}, rpm_t: {}, curr rpm: {:.5}, AoF: {:.4}, AoF_t: {:.4}, height: {:.5}, height_t: {:.5}".format(
			accNED, bestPitch, bestRpm, fDat.rpm,
			math.degrees(math.atan2(vel_ned[0], vel_ned[1])),
			math.degrees(math.atan2(vel_t_ned[0], vel_t_ned[1])),
			fDat.altitude, finalAltitude))

		holdRoll(0.)
		holdPitch(bestPitch)
		holdRpm(bestRpm)


	# Get back into level flight
	print("Leveling out")
	while abs(fDat.pitch) > 2 or abs(fDat.kias - finalSpeed) > 3:
		yield
		updateFlightParams()

		vel_ned = getVelocityNED()
		(vel_t_ned, targetAngle) = getTargetVelocityNED()
		vel_diff = vel_t_ned - vel_ned
		accNED = vel_diff / ACC_FACTOR

		def pitchSteps(pitch):
			for x in range(-16, 16):
				yield float(x) / 8. + pitch

		bestDeltaAcc = float("inf")
		bestPitch = 0.
		# Saturate the controller
		if fDat.kias > finalSpeed: bestRpm = 500
		if fDat.kias < finalSpeed: bestRpm = 3000
		for p in pitchSteps(0.):
			(tempRpm, diff) = findRpmForPitch(p, accNED, fDat, horiz=True)
			if diff < bestDeltaAcc:
				bestDeltaAcc = diff
				bestPitch = p
		print("acc_t: {}, cur speed: {:.5}, tgt speed: {:.5}, pitch_t: {:.4}, height: {:.4}".format(
			accNED, float(fDat.kias), float(finalSpeed), bestPitch, fDat.altitude))

		holdRoll(0.)
		holdPitch(bestPitch)
		holdRpm(bestRpm)


	yield 'DONE'

class AC:

	def __init__(self):
		self.flightState = None
		self.fDat = None
		self.fCmd = None
		self.prevTime = 0.

	def PC(self, fDat, deltaAlt, angle, finalSpeed):
		changed = False
		if angle > 40:
			changed = True
			angle = 40
		if finalSpeed > 250:
			changed = True
			finalSpeed = 250
		if finalSpeed < 70:
			changed = True
			finalSpeed = 70
		if changed: return (angle, finalSpeed)
		return 'OK'

	def PLAN(self, fDat, deltaAlt, angle, finalSpeed):
		self.flightState = flight_generator(fDat, deltaAlt, angle, finalSpeed, lambda: self.getFields())

	def getFields(self):
		return (self.fDat, self.fCmd)

	def DO(self, fDat, fCmd):
		if self.flightState == None: raise ValueError('No plan')
		self.fDat = fDat
		self.fCmd = fCmd
		if fDat.time <= self.prevTime: return
		self.prevTime = fDat.time
		val = next(self.flightState)
		if val == 'DONE':
			self.flightState = None
			return 'DONE'
		return
