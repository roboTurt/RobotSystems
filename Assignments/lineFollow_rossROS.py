import os, sys
import concurrent.futures

from click import echo
#from RossROS.rossros import Producer, runConcurrently
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR+"/lib")
sys.path.append(BASE_DIR+"/RossROS")
from rossros import *


try:

    from grayscale_sensor import *
    from ultrasound import *
    from motors import PicarMotors
    from pin import Pin
    import math
    import time 

except ImportError:

    print("Unable to import from picarx_improved")

if __name__ == "__main__":

    ##initialize class instances
    #Picar_motors = PicarMotors()

    trig_pin = Pin("D2") 
    echo_pin = Pin("D3")
    
    grayscale_sensor = grayscale_Sensors()
    ultrasonic_sensor = ultrasonic_Sensors(trig_pin, echo_pin)

    #initialize rossROS producer sensor message bus
    grayscale_sensor_bus = Bus(name = "grayscale sensor measurements")
    ultrasonic_sensor_bus = Bus(name = "ultrasonic sensor measurements")
    #grayscale_sensor_delay = 0.005

    Linefollow_Interpreter = grayscale_Interpreter(sensitivity = 300, polarity = -1)
    Obstacle_Interpreter = ultrasonic_Interpreter(sensitivity=10)
    #create consumer/producer rossROS bus for the interpreter 
    interpreter_message_bus = Bus(name = "interpreter class messages")

    #interpreter_message_delay = 0.01
    Linefollow_Controller = grayscale_Controller(scalingFactor = 15)
    #consumer/producer bus containing steering angle commands 
    controller_message_bus = Bus(name = "commanded steering angles")
    #controller_message_delay = 0.1
    
    #create bus to hold the timer status
    termination_bus = Bus(name = "termination bus")
    
    #timer class to control runtime of the script 
    timer = Timer(timer_busses = termination_bus, duration = 20, 
                  delay = 1, name = "termination timer") 
    

    #create sensor producer 

    grayscale_sensor_service = Producer(grayscale_sensor.get_adc_value,grayscale_sensor_bus, 
                                        delay =0.01, name = "grayscale sensor bus" )
    
    grayscale_interpreter_service = ConsumerProducer(Linefollow_Interpreter.carRelativePosition2Line,
                                            input_busses = grayscale_sensor_bus, 
                                            output_busses = interpreter_message_bus, 
                                            delay = 0.01, name = "sensor interpreter messages")

    grayscale_controller_service = ConsumerProducer(Linefollow_Controller.calculateSteeringAngle,
                                            input_busses = grayscale_sensor_bus,
                                            output_busses = interpreter_message_bus, 
                                            delay = 0.01, name = "steering angles")

    steering_angle_printer = Printer(printer_bus = controller_message_bus, delay = 1, 
                            name = "steering angle printer", print_prefix = "steering angle: " )


    list_of_concurrent_services  = [grayscale_sensor_service.__call__, 
                                    grayscale_interpreter_service.__call__,
                                    grayscale_controller_service.__call__, 
                                    steering_angle_printer.__call__]





    runConcurrently(list_of_concurrent_services)
    
    #Reading Sensor values is a producer 
    #Interpreter is producer consumer
    #controller is producer consumer 

    # with concurrent.futures.ThreadPoolExecutor(max_workers = 3) as executor:
    #     """
    #     Creates workers for all functions that need to be executed concurrently 
    #     """
    #     eSensor = executor.submit(Picar_sensors.get_adc_value,grayscale_sensor_bus,grayscale_sensor_delay)
        
    #     eInterpreter = executor.submit(Linefollow_Interpreter.carRelativePosition2Line,
    #                     grayscale_sensor_bus, #read from this bus
    #                     interpreter_message_bus, #write to this bus 
    #                     interpreter_message_delay)
        
    #     eController = executor.submit(Linefollow_Controller.calculateSteeringAngle, 
    #                     interpreter_message_bus,#read from this bus
    #                     controller_message_bus, #write to this bus 
    #                     controller_message_delay)
        

    #eSensor.result ()
    
    # while True:
    #     """
    #     Control Loop for line following 
    #     """
    #     sensorReadings = grayscale_sensor_bus.read() #read sensors
    #     servoAngle = controller_message_bus.read()

    #     if math.isclose(sensorReadings[0],sensorReadings[1], abs_tol = 20) and math.isclose(sensorReadings[0],sensorReadings[2], abs_tol = 20): 
    #         #if all 3 sensor readings are approximately equal, then picar is probably not sitting on a line. Stop Condition 
    #         Picar_motors.set_dir_servo_angle(0)
    #         Picar_motors.stop()

    #     else:
    #         #Adjust steering angle accordingly and drive forward 
    #         Picar_motors.set_dir_servo_angle(servoAngle)
    #         Picar_motors.forward(40)
    #         time.sleep(0.05)
