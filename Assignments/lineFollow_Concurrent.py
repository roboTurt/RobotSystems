import os, sys
import concurrent.futures
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR+"/lib")

try:

    from sensors import *
    from motors import PicarMotors
    import math
    import statistics
    import time 
    from Bus import Bus

except ImportError:

    print("Unable to import from picarx_improved")

if __name__ == "__main__":

    ##initialize class instances
    Picar_motors = PicarMotors()
    Picar_sensors = Sensors()
    #initialize sensor message bus
    grayscale_sensor_bus = Bus()
    grayscale_sensor_delay = 0.005

    Linefollow_Interpreter = Interpreter(sensitivity = 300, polarity = -1)
    interpreter_message_bus = Bus()
    interpreter_message_delay = 0.01
    Linefollow_Controller = Controller(scalingFactor = 15)
    controller_message_bus = Bus()
    controller_message_delay = 0.1

    with concurrent.futures.ThreadPoolExecutor(max_workers = 3) as executor:
        """
        Creates workers for all functions that need to be executed concurrently 
        """
        eSensor = executor.submit(Picar_sensors.get_adc_value,grayscale_sensor_bus,grayscale_sensor_delay)
        
        eInterpreter = executor.submit(Linefollow_Interpreter.carRelativePosition2Line,
                        grayscale_sensor_bus, #read from this bus
                        interpreter_message_bus, #write to this bus 
                        interpreter_message_delay)
        
        eController = executor.submit(Linefollow_Controller.calculateSteeringAngle, 
                        interpreter_message_bus,#read from this bus
                        controller_message_bus, #write to this bus 
                        controller_message_delay)
        

    eSensor.result ()
    
    while True:
        """
        Control Loop for line following 
        """
        sensorReadings = grayscale_sensor_bus.read() #read sensors
        servoAngle = controller_message_bus.read()

        if math.isclose(sensorReadings[0],sensorReadings[1], abs_tol = 20) and math.isclose(sensorReadings[0],sensorReadings[2], abs_tol = 20): 
            #if all 3 sensor readings are approximately equal, then picar is probably not sitting on a line. Stop Condition 
            Picar_motors.set_dir_servo_angle(0)
            Picar_motors.stop()

        else:
            #Adjust steering angle accordingly and drive forward 
            Picar_motors.set_dir_servo_angle(servoAngle)
            Picar_motors.forward(40)
            time.sleep(0.05)
