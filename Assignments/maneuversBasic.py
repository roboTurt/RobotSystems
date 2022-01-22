import os, sys
BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path.append(BASE_DIR+"/lib")

try:

    from picarx_improved import *

except ImportError:

    print("Unable to import from picarx_improved")


class Maneuvers(Picarx):
    #super.__init__(self)
    def __init__(self):
        super().__init__()

        self.set_dir_servo_angle(0)

    def forward_backward(self):

        self.forward(50) #drive forward
        time.sleep(2)
        self.stop()    #stop 
        time.sleep(1)
        self.backward(50)  #drive backward 
        time.sleep(2)
        self.stop()         #stop 

    def parallelPark(self):

        self.set_dir_servo_angle(-15)
        self.backward(50)
        time.sleep(1)
        self.stop()
        time.sleep(2)

        self.set_dir_servo_angle(0)
        self.backward(50)
        time.sleep(1)
        self.stop()
        time.sleep(2)

        self.set_dir_servo_angle(15)
        self.backward(50)
        time.sleep(1)
        self.stop()
        time.sleep(2)


    def K_turn(self):

        self.set_dir_servo_angle(-45)
        self.backward(50)
        time.sleep(2)
        self.stop()
        time.sleep(1)
        self.set_dir_servo_angle(45)
        self.forward(50)
        time.sleep(2)
        self.stop()


    def getUserInputs(self):

        while True:
            maneuver = input("Enter FB for forward-backward maneuver, P for Parallel Parking, and K for K-turn... ")
            
            if maneuver == "FB":

                logging.debug(" Doing forward and back ")
                time.sleep(2)
                self.forward_backward()
                break 

            elif maneuver == "P":
                logging.debug(" Doing Parallel Park ")
                time.sleep(2)
                self.parallelPark()
                break 

            elif maneuver == "K":
                logging.debug(" Doing K Turn ")
                time.sleep(2)
                self.K_turn()
                break 

            else:

                logging.debug(" Invalid Maneuver! ")

if __name__ == "__main__":

    px = Maneuvers()
    px.getUserInputs()
