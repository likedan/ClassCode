# Simple example of exploring the flight dynamics
# import ExploringPilot; a=ExploringPilot.ExploringPilot(); a.start()

import ClassCode.Ckpt as Ckpt

import PID

import random, pickle
import imp, sys, math
import time

def rel():
    imp.reload(sys.modules['ExploringPilot'])
    imp.reload(sys.modules['PID'])

class ExploringPilot (Ckpt.Ckpt):			# subclass of the class Ckpt in the file Ckpt

	def __init__(self, tsk = 'HW4aExp', rc = False, gui = False):
		super().__init__(tsk, rc, gui)
		self.rollPID = None
		self.pitchPID = None
		self.throttlePID = None
		self.initialized = False
		self.counter = 0
		self.targetAirspeed = 150
		self.targetPitch = 0.0
		self.data = []

	def initializeWithFDat(self, fDat, rollError, pitchError):
		'''Initialize the Pilot's members with initial data from fDat.'''
		self.strtTime = fDat.time
		self.prevTime = fDat.time
		self.rollPID = PID.PID(1.8 / 180, 0.25 / 180, 1.0 / 180, rollError, fDat.time)
		self.pitchPID = PID.PID(6.0 / 180, 10.0 / 180, 0.1 / 180, pitchError, fDat.time)
		self.throttlePID = PID.PID(0.9 / 100, 5.0 / 100, 0.1 / 100, 0, fDat.time)
		self.initialized = True

	def holdRoll(self, fDat, fCmd):
		# Hold zero roll
		rollError = 0 - fDat.roll
		rollControl = self.rollPID.controlValue(rollError, fDat.time)
		fCmd.aileron = max(min(rollControl, 1.0), -1.0)

	def ai(self, fDat, fCmd):
		'''Override with the Pilot decision maker, args: fltData and cmdData from Utilities.py'''
		if not self.initialized:
			self.initializeWithFDat(fDat, -fDat.roll, fDat.pitch)
			return
		# if we recieved the same packet twice in a row, ignore it
		if fDat.time <= self.prevTime: return
		val = self.progress(fDat, fCmd)
		self.prevTime = fDat.time
		return val

	def progress(self, fDat, fCmd):
		self.holdRoll(fDat, fCmd)

		print('Pitch: {:.5f}, Height: {:.2f}, Airspeed: {:.2f}, Target airspeed: {:.2f}, RPM: {:.2f}, VSpeed feet/s: {:.2f}, X-accel feet/s2: {:.2f}, Z-accel feet/s2: {:.7f}, Time: {:.2f}'
			.format(fDat.pitch, fDat.altitude, fDat.kias, self.targetAirspeed, fDat.rpm, fDat.vspeed, fDat.xaccel, -fDat.zaccel - 32, fDat.time))
		pitchError = fDat.pitch - self.targetPitch
		pitchControl = self.pitchPID.controlValue(pitchError, fDat.time)
		fCmd.elevator = max(min(pitchControl, 1.0), -1.0)

		speedError = self.targetAirspeed - fDat.kias
		throttleControl = self.throttlePID.controlValue(speedError, fDat.time)
		fCmd.throttle = max(min(throttleControl, 1.0), 0.0)

		if fDat.time > 4.0:
			# Record data
			self.data.append((fCmd.throttle, fDat.pitch, fDat.altitude, fDat.kias, fDat.rpm, fDat.vspeed, fDat.xaccel, fDat.zaccel, fDat.time))

		self.counter += 1
		if self.counter % 50 == 0:
			self.targetPitch = random.uniform(-5., -10.)
			#self.pitchPID.resetIntegral()
		if self.counter % 170 == 0:
			self.targetAirspeed = random.uniform(90., 250.)

		# Emergency recovery
		if fDat.kias < 110.: self.targetPitch = random.uniform(-20., 0.)

		if fDat.altitude > 4000 or fDat.altitude < 700 or fDat.time > 120:
			with open('output/data{}'.format(round(time.time())), 'wb') as f:
				pickle.dump(self.data, f)
			return 'stop';



