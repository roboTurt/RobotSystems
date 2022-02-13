import os, sys
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR+"/lib")

try:

    from sensors import *
    from motors import PicarMotors
    import math
    import statistics
    import time 

except ImportError:

    print("Unable to import from picarx_improved")



if __name__ == "__main__":

    ##initialize class instances

    Picar_motors = PicarMotors()
    Picar_sensors = Sensors()
    Linefollow_Interpreter = Interpreter(sensitivity = 300, polarity = -1)
    Linefollow_Controller = Controller(scalingFactor = 15)


    while True:
        """
        Control Loop for line following 
        """
        
        #userInput = input("Press x to quit   ")

        sensorReadings = Picar_sensors.get_adc_value() #read sensors
        
        time.sleep(0.001)
        
        carRelativePosToLine = Linefollow_Interpreter.carRelativePosition2Line(sensorReadings) #determine position
        #logging.debug(sensorReadings)
        time.sleep(0.001)
        #logging.debug(f"position of car: {carRelativePosToLine}")
        servoAngle = Linefollow_Controller.adjustSteeringAngle(carRelativePosToLine) #adjust steering servo angle
        
        time.sleep(0.001)

        logging.debug(f"servo angle:  {servoAngle}")
            
        averageSensorValue = statistics.mean(sensorReadings)

        if math.isclose(sensorReadings[0],sensorReadings[1], abs_tol = 20) and math.isclose(sensorReadings[0],sensorReadings[2], abs_tol = 20): 
                #if all 3 sensor readings are approximately equal, then picar is probably not sitting on a line. Stop Condition 
                Picar_motors.set_dir_servo_angle(0)
                Picar_motors.stop()

        else:
            #Adjust steering angle accordingly and drive forward 
            Picar_motors.set_dir_servo_angle(servoAngle)
            Picar_motors.forward(40)
            time.sleep(0.005)
