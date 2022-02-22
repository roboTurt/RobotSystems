

import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *


class MoveArm():

    def __init__(self) -> None:
        
        self.gripperAngle_closed = 500    
        self.last_target_world_X = None
        self.last_target_world_Y = None
        self.AK = ArmIK()


    # 初始位置
    def initMove(self):
        """
        move end effector to home position

        """
        Board.setBusServoPulse(1, self.gripperAngle_closed - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)


    def set_Arm_RGB_Color(self, detected_color):

        if detected_color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif detected_color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif detected_color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()
    
    def match_EF_angle_to_block(self,target_world_X, target_world_Y, target_orientation_angle):

        servo2_angle = getAngle(target_world_X, target_world_Y, target_orientation_angle)
        
        return servo2_angle

    def rotate_EF_by_angle(self, targetAngle):
        
        Board.setBusServoPulse(2, targetAngle, 500)

    def move_EF_ToTarget(self, target_world_X, target_world_Y):
        
        status = AK.setPitchRangeMoving((target_world_X, target_world_Y, 7), -90, -90, 0)
        
        if status != False:

            self.last_target_world_X = target_world_X
            self.last_target_world_Y = target_world_Y

        return status  

    def closeGripper(self):

        Board.setBusServoPulse(1, self.gripperAngle_closed, 500)
 
    
    def openGripper(self):

        Board.setBusServoPulse(1, self.gripperAngle_closed - 280, 500)  # 爪子张开 #open gripper 

    
    def adjust_EF_Z_height(self, target_Z_height):
        
        if self.last_target_world_Y and self.last_target_world_X is not None: 

            AK.setPitchRangeMoving((self.last_target_world_X, self.last_target_world_Y, target_Z_height), 
            
                                    -90, -90, 0, 1000)
   

    


    