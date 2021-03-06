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
    
    obstacle_interpreter_bus = Bus(name = "move wheels true/false from ultrasonic distance sensor")
    
    Obstacle_Controller = ultrasonic_Controller()

    #create consumer/producer rossROS bus for the interpreter 
    linefollow_interpreter_message_bus = Bus(name = "interpreter class messages")

    #interpreter_message_delay = 0.01
    Linefollow_Controller = grayscale_Controller(scalingFactor = 15)
    #consumer/producer bus containing steering angle commands 
    linefollow_controller_message_bus = Bus(name = "commanded steering angles")
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
                                            output_busses = linefollow_interpreter_message_bus, 
                                            delay = 0.01, name = "sensor interpreter messages")

    grayscale_controller_service = ConsumerProducer(Linefollow_Controller.calculateSteeringAngle,
                                            input_busses = grayscale_sensor_bus,
                                            output_busses = linefollow_interpreter_message_bus, 
                                            delay = 0.01, name = "steering angles")

    steering_angle_printer = Printer(printer_bus = linefollow_controller_message_bus, delay = 1, 
                            name = "steering angle printer", print_prefix = "steering angle: " )


    ultrasonic_sensor_service = Producer(ultrasonic_sensor._read(),
                                        output_busses = ultrasonic_sensor_bus, 
                                        delay = 0.1, 
                                        name = "ultrasonic distance values" )

    ultrasonic_interpreter_service = ConsumerProducer(Obstacle_Interpreter.checkDistanceToObstacle,
                                                    input_busses = ultrasonic_sensor_bus,
                                                    output_busses = obstacle_interpreter_bus,
                                                    delay = 0.1, name = "obstacle detection from ultrasonic sensor")

    ultrasonic_controller_service = Consumer(Obstacle_Controller.stopMotorsBeforeObstacle,
                                            input_busses = obstacle_interpreter_bus,
                                            delay = 0.1,
                                            name = "consume obstacle true/false status to drive motors accordingly")

    list_of_concurrent_services  = [grayscale_sensor_service.__call__, 
                                    grayscale_interpreter_service.__call__,
                                    grayscale_controller_service.__call__, 
                                    steering_angle_printer.__call__,
                                    ultrasonic_sensor_service.__call__,
                                    ultrasonic_interpreter_service.__call__,
                                    ultrasonic_controller_service.__call__,]



    runConcurrently(list_of_concurrent_services)
    