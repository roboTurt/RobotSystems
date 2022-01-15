try:

    from picarx_improved import *

except ImportError:

    print("Unable to import from picarx_improved")

import time
# try:
#     from ezblock import *
#     from ezblock import __reset_mcu__
#     from servo import Servo 
#     from pwm import PWM
#     from pin import Pin
#     from adc import ADC
#     from filedb import fileDB
#     __reset_mcu__ ()
#     time.sleep (0.01)
# except ImportError:
#     print ("This computer does not appear to be a PiCar -X system (ezblock is not present)." 
#             "Shadowing hardware calls with substitute functions")
#     from sim_ezblock import *

# #import logging library
# import atexit
# import logging
# from logdecorator import log_on_start , log_on_end , log_on_error
# logging_format = "%(asctime)s: %(message)s"
# logging.basicConfig(format=logging_format , level=logging.INFO , datefmt ="%H:%M:%S")

# logging.getLogger ().setLevel(logging.DEBUG)   


if __name__ == "__main__":

    px = Picarx()
    #set steering servo angle
    px.set_dir_servo_angle(-15)
    #drive forward for a short time
    px.forward(50)
    time.sleep(2)
    px.stop()


