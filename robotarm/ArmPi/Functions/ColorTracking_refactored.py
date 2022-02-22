#!/usr/bin/python3
# coding=utf8
import sys
import os

from Functions.MoveArm import MoveArm

sys.path.append(os.path.dirname(os.getcwd()))
#sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from Perception import *
from CameraCalibration.CalibrationConfig import *
from RossROS import rossros 

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

#AK = ArmIK()

if __name__ == '__main__':
    # init()
    # start()
    __target_color = ('red', )
    my_camera = Camera.Camera()
    my_camera.camera_open()

    done = False # arm state variable to end program
    id_blocks = Perception(__target_color) # 
    arm_IK = MoveArm()


    #Create RossROS busses
    raw_camera_image_bus = Bus(name = "raw camera image frames to be processed")
    smoothed_camera_image_bus = Bus(name = "smoothed and cropped camera frames to run CV on")
    processed_camera_image_bus = Bus(name = "image frame post CV object detection")

    world_X_target_coord_bus = Bus(name = "world frame X coordinate of detected object")
    world_Y_target_coord_bus = Bus(name = "world frame Y coordinate of detected object")
    object_orientation_bus = Bus(name = "angle of detected object")

    detected_color_bus = Bus(name = "color string of detected object")

    pickAndPlace_status_bus = Bus(name = "status of pick and place maneuver")

    termination_bus = Bus(name = "termination bus")

    #timer class to control runtime of the script
    timer = Timer(timer_busses = termination_bus, duration = 20, 
                  delay = 1, name = "termination timer") 

    #Creating perception RossROS services 

    camera_feed_service = Producer(my_camera.frame, 
                                    output_busses = raw_camera_image_bus,
                                    delay = 1,
                                    name = "raw camera images")

    parse_camera_frames_service = Consumer(id_blocks.readImageFrame, 
                                                    input_busses = raw_camera_image_bus,
                                                    delay = 1,
                                                    name = "read raw camera images")

    smooth_camera_frames_service = Producer(id_blocks.resizeAndSmoothImage, 
                                                    output_busses = smoothed_camera_image_bus,
                                                    delay = 1,
                                                    name = "smooth and crop raw camera images")

    runCV_on_processed_camera_frames_service = ConsumerProducer(id_blocks.detectObject,
                                                                input_busses = smoothed_camera_image_bus,
                                                                output_busses = [processed_camera_image_bus,
                                                                                detected_color_bus,
                                                                                world_X_target_coord_bus,
                                                                                world_Y_target_coord_bus],
                                                                delay = 1,
                                                                name = "do CV object detection on processed frames")


    # set_endEffector_target_coordinate_service = Consumer(arm_IK.capture_block_location_and_color,
    #                                             input_busses = [world_X_target_coord_bus, 
    #                                                             world_Y_target_coord_bus, 
    #                                                             detected_color_bus],
    #                                             delay = 1,
    #                                             name = "sets target coordinates for arm")

    pick_and_place_service = ConsumerProducer(arm_IK.pickAndPlace,
                                            input_busses = [world_X_target_coord_bus, 
                                                                    world_Y_target_coord_bus, 
                                                                    detected_color_bus],
                                            output_busses = pickAndPlace_status_bus, 
                                            delay = 1,
                                            name = "executes pick and place maneuver")

    list_of_concurrent_services  = [camera_feed_service.__call__, 
                                    parse_camera_frames_service.__call__,
                                    smooth_camera_frames_service.__call__, 
                                    runCV_on_processed_camera_frames_service.__call__,
                                    #pick_and_place_service.__call__,
                                    ]


    runConcurrently(list_of_concurrent_services)

    cv2.imshow('Frame', processed_camera_image_bus.message)

