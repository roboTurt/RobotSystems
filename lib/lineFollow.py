
try:

    from sensors import *
    from motors import PicarMotors
    import math
    import statistics
    import time 

except ImportError:

    print("Unable to import from picarx_improved")



if __name__ == "__main__":

    Picar_motors = PicarMotors()
    Picar_sensors = Sensors()
    Linefollow_Interpreter = Interpreter(sensitivity = 1200, polarity = -1)
    Linefollow_Controller = Controller(scalingFactor = 15)

    while True:
        
        
        userInput = input("Press x to quit   ")

        sensorReadings = Picar_sensors.get_adc_value() #read sensors
        
        time.sleep(0.01)
        
        carRelativePosToLine = Linefollow_Interpreter(sensorReadings) #determine position
        
        time.sleep(0.01)
        
        servoAngle = Linefollow_Controller(carRelativePosToLine) #adjust steering servo angle
        
        time.sleep(0.01)


        averageSensorValue = statistics.mean(sensorReadings)
        if math.isclose(0,sensorReadings[0] - averageSensorValue, 100) and math.isclose(0,sensorReadings[1] - averageSensorValue, 100) \
            and math.isclose(0,sensorReadings[2] - averageSensorValue, 100):

                Picar_motors.stop()
                time.sleep(1)

        else:

            Picar_motors.forward(40)
            time.sleep(0.5)

        if userInput == "x":

            break 
