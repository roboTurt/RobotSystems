try:

    from picarx_improved import *
    from motors import PicarMotors

except ImportError:

    print("Unable to import from picarx_improved")


class ultrasonic_Sensors():
    def __init__(self, trig, echo, timeout = 0.02, attempts = 10):
        
        #Set pins for ultrasonic sensor 
        self.trig = trig
        self.echo = echo
        self.timeout = timeout
        self.attempts = attempts

    def _read(self):
        self.trig.low()
        time.sleep(0.01)
        self.trig.high()
        time.sleep(0.00001)
        self.trig.low()
        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        while self.echo.value()==0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.value()==1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1
        during = pulse_end - pulse_start
        cm = round(during * 340 / 2 * 100, 2)
        return cm

    @log_on_start(logging.DEBUG , "Beginning Read of Ultrasonic Sensor")
    @log_on_end(logging.DEBUG , "Ultrasonic sensor value captured")  
    def get_ultrasonic_value(self):
        for i in range(self.attempts):
            a = self._read()
            if a != -1 or a <= 300:
                return a
        return -1

import numpy as np

class ultrasonic_Interpreter():
    def __init__(self, sensitivity = 5):

        #Sensitivity- threshold in cm in which to send the stop signal 
        self.sensitivity = sensitivity


    @log_on_start(logging.DEBUG , "Checking Distance to Obstacle")
    @log_on_end(logging.DEBUG , "Distance Value Processed Successfully")
    def checkDistanceToObstacle(self, ultrasonic_sensor_values):
        
        if ultrasonic_sensor_values < self.sensitivity:

            return True
        
        else:

            return False 


class ultrasonic_Controller():

    def __init__(self, nominal_speed = 50):

        self.nominal_speed = nominal_speed 
        self.Picar_motors = PicarMotors()  
        #ADC values for grayscale module

    @log_on_start(logging.DEBUG , "Setting Steering Servo Angle")
    @log_on_end(logging.DEBUG , "Steering Servo Angle Set Successfully")
    def stopMotorsBeforeObstacle(self, interpreter_message_bus):

        if interpreter_message_bus is True:

            self.Picar_motors.forward(self.nominal_speed)

        else:

            self.Picar_motors.forward(0)
            


