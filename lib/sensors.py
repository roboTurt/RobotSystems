try:

    from picarx_improved import *
    from motors import PicarMotors

except ImportError:

    print("Unable to import from picarx_improved")


class Sensors():
    def __init__(self):
        
        #ADC values for grayscale module
        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

    @log_on_start(logging.DEBUG , "Beginning Read of Grayscale Sensors")
    @log_on_end(logging.DEBUG , "Grayscale Sensor values captured")
    def get_adc_value(self, grayscale_sensor_bus, sleepTime):

        while True:

            adc_value_list = []
            adc_value_list.append(self.S0.read())
            adc_value_list.append(self.S1.read())
            adc_value_list.append(self.S2.read())
            
            grayscale_sensor_bus.write(adc_value_list)

            time.sleep(sleepTime)
        #return adc_value_list

import numpy as np
import statistics

class Interpreter():
    def __init__(self, sensitivity = 600, polarity = -1):
        #import numpy as np
        #Sensitivity- how different dark and light readings are expected to be
        #Polarity if the line being followed is lighter or darker than floor [-1 for darker, 1 for lighter]
        #ADC values for grayscale module
        self.sensitivity = sensitivity
        self.polarity = polarity
        #self.Interpreter_bus = Bus() 

    @log_on_start(logging.DEBUG , "Calculating Car Orientation")
    @log_on_end(logging.DEBUG , "Car Orientation Set Successfully")
    def carRelativePosition2Line(self,grayscale_sensor_bus, interpreter_message_bus, sleepTime):
    
        #ADC values will be high for light colors and low for dark colors, pure black is 0 and white is 15-1600 ish 

        #For dark surfaces, value of middleSensor should be > left and right sensor
        #For light surfaces, value of middleSensor < left/right sensor 
        while True:
            
            grayScaleValues = grayscale_sensor_bus.read()
            leftSensor = grayScaleValues[0]
            middleSensor = grayScaleValues[1]
            rightSensor = grayScaleValues[2]

            relativePosition  = 0

            if self.polarity == -1:

                #dark surface 

                left_middle_sensor_delta = middleSensor - leftSensor
                right_middle_sensor_delta = middleSensor - rightSensor

                left_right_sensor_delta = leftSensor - rightSensor 

                relPos_left_middle = np.interp(left_middle_sensor_delta, [0, self.sensitivity], [-1,0])
                relPos_right_middle = np.interp(right_middle_sensor_delta, [0, self.sensitivity], [1,0])


                relPos_left_right = np.interp(left_right_sensor_delta, [-self.sensitivity,self.sensitivity],[-1,1])
                
                readings = [relPos_left_middle,relPos_right_middle,relPos_left_right]

                absValReadings = [abs(x) for x in readings]

                max_Value = max(absValReadings)
                max_Index = absValReadings.index(max_Value)
                relativePosition = readings[max_Index]
                #relativePosition = statistics.mean([relPos_left_middle,relPos_right_middle,relPos_left_right])
                #return relativePosition

            elif self.polarity ==  1:

                #light surface 

                left_middle_sensor_delta = leftSensor - middleSensor
                right_middle_sensor_delta = rightSensor - middleSensor

                left_right_sensor_delta = rightSensor - leftSensor

                relPos_left_middle = np.interp(left_middle_sensor_delta, [0, self.sensitivity], [-1,0])
                relPos_right_middle = np.interp(right_middle_sensor_delta, [0, self.sensitivity], [1,0])


                relPos_left_right = np.interp(left_right_sensor_delta, [-self.sensitivity,self.sensitivity],[-1,1])
                
                relativePosition = statistics.mean([relPos_left_middle,relPos_right_middle,relPos_left_right])
            
            interpreter_message_bus.write(relativePosition)
            time.sleep(sleepTime)


class Controller():

    def __init__(self, scalingFactor = 10):

        self.scalingFactor = scalingFactor 
        #self.Picar_motors = PicarMotors()  
        #ADC values for grayscale module

    @log_on_start(logging.DEBUG , "Setting Steering Servo Angle")
    @log_on_end(logging.DEBUG , "Steering Servo Angle Set Successfully")
    def calculateSteeringAngle(self, interpreter_message_bus, controller_message_bus, sleepTime):

        while True:
            #relative position ranges from [-1,1]
            relativePosition = interpreter_message_bus.read()
            time.sleep(sleepTime)
            angle = np.interp(relativePosition, [-1,1],[-self.scalingFactor,self.scalingFactor])
            controller_message_bus.write(angle)


