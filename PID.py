# Basic PID controller

class PID:

	def __init__(sf, kp, ki, kd, initialError, initialTime):
		sf.Kp = kp
		sf.Ki = ki
		sf.Kd = kd

		sf.prevError = initialError
		sf.prevTime = initialTime
		sf.integral = 0.0

	def controlValue(sf, error, time):
		'''Returns a value to be used to set the appropriate control, given the current error and time.'''
		timeDelta = time - sf.prevTime
		errorDelta = error - sf.prevError

		# print('{} {} {} {} {}'.format(sf.Ki, timeDelta/2.0, sf.prevError, error, sf.Ki * (timeDelta / 2.0) * (sf.prevError + error)))
		sf.integral += sf.Ki * (timeDelta / 2.0) * (sf.prevError + error)
		derivative = errorDelta / timeDelta

		control = sf.Kp * error + sf.Kd * derivative + sf.integral

		# Integral decay
		sf.integral *= 0.98

		sf.prevTime = time
		sf.prevError = error

		return control

	def resetIntegral(sf):
		'''Reseting the integral can combat the effects of windup.'''
		sf.integral = 0.0