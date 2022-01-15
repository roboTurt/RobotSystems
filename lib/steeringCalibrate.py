try:

    from picarx_improved import *

except ImportError:

    print("Unable to import from picarx_improved")




if __name__ == "__main__":
    px = Picarx()
    #set steering servo to angle 0
    px.set_dir_servo_angle(0)
    #drive forward for a short time
    px.forward(50)
    time.sleep(2)
    px.stop()