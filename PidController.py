__author__ = 'CoRoNa'
#Translate pid algorithm to code from this video https://www.youtube.com/watch?v=JEpWlTl95Tw
#Personally, I am working on how to apply this script to Pilot.

class PidController:
    '''
        Sample PID control
    '''
    def __init__(sf, p, i, d):
        sf.Kp = p
        sf.Ki = i
        sf.Kd = d
        sf.deri_num = 0.0
        sf.inte_num = 0.0
        sf.inte_min = -100.0
        sf.inte_max = 100.0
        sf.set_point = 0.0
        sf.error = 0.0

    def setKp(sf, p):
        sf.Kp = p

    def setKi(sf, i):
        sf.Ki = i

    def setKd(sf, d):
        sf.Kd = d

    def setDerivator(sf, derivator):
        sf.deri_num = derivator

    def getDerivator(sf):
        return sf.deri_num

    def setIntegrator(sf, integrator):
        sf.inte_num = integrator

    def getIntegrator(sf):
        return sf.inte_num

    def setMinIntegrator(sf, integrator):
        sf.inte_min = integrator

    def setMaxIntegrator(sf, integrator):
        sf.inte_max = integrator

    def setPoint(sf, point):
        sf.set_point = point

    def getPoint(sf):
        return sf.set_point

    def getError(sf):
        return sf.error

    def calculatePid(sf, process_val):
        '''
        :param sf: self
        :param process_val: The value that we want to achieve
        :return: PID value
        '''

        sf.error = sf.set_point - process_val

        sf.inte_num += sf.error
        if(sf.inte_num < sf.inte_min):
            sf.inte_num = sf.inte_min
        elif(sf.inte_num > sf.inte_max):
            sf.inte_num = sf.inte_max

        ret_val = sf.Kp * sf.error + sf.Kd * (sf.error - sf.deri_num) + sf.Ki * sf.inte_num
        sf.deri_num = sf.error

        return ret_val

    def calculateAngelPid(sf, process_val):
        '''
        :param sf: self
        :param process_val: The value that we want to achieve
        :return: PID value
        '''

        sf.error = process_val - sf.set_point

        sf.inte_num += sf.error
        if(sf.inte_num < sf.inte_min):
            sf.inte_num = sf.inte_min
        elif(sf.inte_num > sf.inte_max):
            sf.inte_num = sf.inte_max

        ret_val = sf.Kp * sf.error + sf.Kd * (sf.error - sf.deri_num) + sf.Ki * sf.inte_num
        sf.deri_num = sf.error

        if(abs(sf.error) > 180):
            sf.error -= 180
            ret_val = sf.Kp * sf.error + sf.Kd * (sf.error - sf.deri_num) + sf.Ki * sf.inte_num
            sf.deri_num = sf.error
            if(sf.error < 0):
                print('Turn left. sf.error > 180, sf.error < 0. Angle PID {:.3f} error - return val {:.3f}'.format(sf.error, ret_val))
                return ret_val
            else:
                print('Turn right. sf.error > 180, sf.error > 0. Angle PID {:.3f} error - return val {:.3f}'.format(sf.error, ret_val))
                return ret_val
        else:
            if(sf.error > 0):
                print('Turn left. sf.error < 180, sf.error > 0. Angle PID {:.3f} error - return val {:.3f}'.format(sf.error, -ret_val))
                return -ret_val
            else:
                print('Turn right. Angle PID {:.3f} error - return val {:.3f}'.format(sf.error, -ret_val))
                return -ret_val
