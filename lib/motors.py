try:

    from picarx_improved import *

except ImportError:

    print("Unable to import from picarx_improved")

class PicarMotors(Picarx):

    def __init__(self):

        self.dir_servo_pin = Servo(PWM('P2'))
        self.camera_servo_pin1 = Servo(PWM('P0'))
        self.camera_servo_pin2 = Servo(PWM('P1'))
        self.config_flie = fileDB('/home/pi/.config')
        self.dir_cal_value = int(self.config_flie.get("picarx_dir_servo", default_value=-15))
        self.cam_cal_value_1 = int(self.config_flie.get("picarx_cam1_servo", default_value=0))
        self.cam_cal_value_2 = int(self.config_flie.get("picarx_cam2_servo", default_value=0))
        self.dir_servo_pin.angle(self.dir_cal_value)
        self.camera_servo_pin1.angle(self.cam_cal_value_1)
        self.camera_servo_pin2.angle(self.cam_cal_value_2)

        self.left_rear_pwm_pin = PWM("P13")
        self.right_rear_pwm_pin = PWM("P12")
        self.left_rear_dir_pin = Pin("D4")
        self.right_rear_dir_pin = Pin("D5")


        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = self.config_flie.get("picarx_dir_motor", default_value="[1,1]")
        self.cali_dir_value = [int(i.strip()) for i in self.cali_dir_value.strip("[]").split(",")]
        self.cali_speed_value = [0, 0]
        self.dir_current_angle = 0

        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)
        
        atexit.register(self.cleanup)


    @log_on_start(logging.DEBUG , "Moving PicarX Forward... WARNING!!!! MAKE SURE CAR IS ON THE FLOOR...")
    @log_on_error(logging.DEBUG , "Error in px.forward()")
    @log_on_end(logging.DEBUG , "Motor speed commmands set successfully")
    def forward(self,speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            #If turn angle is commanded, modify motor speeds to match the turn angle in order to prevent wheel slip
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0 
            #print("power_scale:",power_scale)
            #logging.debug("power_scale:",power_scale)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, speed) # fast wheel
                self.set_motor_speed(2, -1*speed * power_scale) # slow wheel
            else:
                self.set_motor_speed(1, speed * power_scale) #slow wheel
                self.set_motor_speed(2, -1*speed ) #fast wheel
        else:
            #if no turn angle is commanded, spin both motors at the same speed
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1*speed) 

    @log_on_start(logging.DEBUG , "Moving PicarX backward... WARNING!!!! MAKE SURE CAR IS ON THE FLOOR...")
    @log_on_error(logging.DEBUG , "Error in px.backward()")
    @log_on_end(logging.DEBUG , "Motor speed commmands set successfully")
    def backward(self,speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            # if abs_current_angle >= 0:
            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0 
            #print("power_scale:",power_scale)
            #logging.debug("power_scale:",power_scale)
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, -1*speed)
                self.set_motor_speed(2, speed * power_scale)
            else:
                self.set_motor_speed(1, -1*speed * power_scale)
                self.set_motor_speed(2, speed )
        else:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, speed)  

    def stop(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)


    @log_on_start(logging.DEBUG , "Setting Motor {motor:n} to speed value: {speed:f} \n ")
    @log_on_error(logging.DEBUG , "Error while setting motor speed \n ")
    @log_on_end(logging.DEBUG , "Motor {motor:n} successfully set to speed value: {speed:f} \n ")
    def set_motor_speed(self,motor,speed):
        # global cali_speed_value,cali_dir_value
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        # if speed != 0:
        #     speed = int(speed /2 ) + 50
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    @log_on_start(logging.DEBUG , "Setting Servo Steering Angle to: {value:f} \n ")
    @log_on_error(logging.DEBUG , "Error while setting steering angle \n ")
    @log_on_end(logging.DEBUG , "Servo successfully set to angle value: {value:f} \n ")
    def set_dir_servo_angle(self,value):
        # global dir_cal_value
        self.dir_current_angle = value
        angle_value  = value + self.dir_cal_value
        #print("angle_value:",angle_value)
        # print("set_dir_servo_angle_1:",angle_value)
        # print("set_dir_servo_angle_2:",dir_cal_value)
        self.dir_servo_pin.angle(angle_value)


    def motor_speed_calibration(self,value):
        # global cali_speed_value,cali_dir_value
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(self,motor, value):
        # 0: positive direction
        # 1:negative direction
        # global cali_dir_value
        motor -= 1
        if value == 1:
            self.cali_dir_value[motor] = -1 * self.cali_dir_value[motor]
        self.config_flie.set("picarx_dir_motor", self.cali_dir_value)

    def set_power(self,speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed) 

    @log_on_start(logging.DEBUG , "End of Program, stopping motors... ")
    def cleanup(self):

        self.stop() 