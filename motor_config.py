import odrive
from odrive.enums import *
import time
import asyncio

class odriveTools():
    def __init__(self):
        pass

    def giveCurrent(self, odrv):
        current = []
        current.append(odrv.axis0.motor.current_control.Iq_measured)
        current.append(odrv.axis1.motor.current_control.Iq_measured)
        print("Motor0_measured_current: " + str(current[0]))
        print("Motor1_measured_current: " + str(current[1]))
        return current

    def giveVoltage(self, odrv):
        voltage = []
        voltage.append(odrv.axis0.motor.current_control.v_current_control_integral_d)
        voltage.append(odrv.axis0.motor.current_control.v_current_control_integral_q)
        print("Motor0_measured_voltage: " + str(voltage[0]))
        print("Motor1_measured_voltage: " + str(voltage[1]))
        return voltage

    def checkErrors(self, odrv):
        print(odrive.dump_errors(odrv))

    def clearErrors(self, odrv):
        odrv.clear_errors()

    def setMode(self, odrv, mode:int):
        if  0 <= mode < 15 and mode != 5:
            odrv.axis0.controller.config.control_mode = mode
            odrv.axis1.controller.config.control_mode = mode
        else:
            print("invalid_mode")

    def getTemperature(self):
        print("Если когда-нибудь появятся термисторы на моторах, дай мне знать ;)")

    def getVelocity(self, odrv):
        velocity = []
        velocity.append(odrv.axis0.encoder.vel_estimate)
        velocity.append(odrv.axis0.encoder.vel_estimate)
        return velocity

    def getPos(self, odrv):
        position = []
        position.append(odrv.axis0.encoder.pos_estimate)
        position.append(odrv.axis1.encoder.pos_estimate)
        print("Motor0_current_position: " + str(position[0]))
        print("Motor1_current_position: " + str(position[1]))
        return position

class motorFlipper(odriveTools):
    def __init__(self, SERIAL_NUMBER, axis_pos_arr:[float]):
        super().__init__()
        self.odrv = odrive.find_any(serial_number = SERIAL_NUMBER) # Flipper
        self._setStartPos(axis_pos_arr)

    def _setStartPos(self, axis_pos_arr:[float]):
        if  -6 <= axis_pos_arr[0] <= 6:
            print(axis_pos_arr[0])
            self.odrv.axis0.requested_state = 8 #AXIS_STATE_CLOSED_LOOP_CONTROL
            self.odrv.axis0.controller.config.control_mode = 3 #CONTROL_MODE_POSITION_CONTROL
            self.odrv.axis0.controller.input_pos = axis_pos_arr[0]
            
        if  -6 <= axis_pos_arr[1] <= 6:
            print(axis_pos_arr[1])
            self.odrv.axis1.requested_state = 8 #AXIS_STATE_CLOSED_LOOP_CONTROL
            self.odrv.axis1.controller.config.control_mode = 3 #CONTROL_MODE_POSITION_CONTROL
            self.odrv.axis1.controller.input_pos = axis_pos_arr[1]
    
    def setPosition(self, axis_pos_arr:[float]):
        if  -6.0 <= axis_pos_arr[0] <= 6.0:
            self.odrv.axis0.requested_state = 8 #AXIS_STATE_CLOSED_LOOP_CONTROL
            self.odrv.axis0.controller.config.control_mode = 3 #CONTROL_MODE_POSITION_CONTROL
            self.odrv.axis0.controller.input_pos = axis_pos_arr[0]

        if  -6.0 <= axis_pos_arr[1] <= 6.0:
            self.odrv.axis1.requested_state = odrive.enums.AXIS_STATE_CLOSED_LOOP_CONTROL
            self.odrv.axis1.controller.config.control_mode = odrive.enums.CONTROL_MODE_POSITION_CONTROL
            self.odrv.axis1.controller.input_pos = axis_pos_arr[1]
            

    #async def _positionOffsetTask(self, targetPos, presentPos):
    #    while presentPos != targetPos:
    #        incPos = presentPos + 2
    #        self.odrv.axis1.controller.input_pos = incPos
    #        await asyncio.sleep(0.25)

class motorCaterpillar(odriveTools):
    def __init__(self, SERIAL_NUMBER):
        super().__init__()
        self.odrv = odrive.find_any(serial_number = SERIAL_NUMBER) # Caterpillar

    def setVelocity(self, axis_vel_arr:[float]):
        if axis_vel_arr[0] == 0:
            self.odrv.axis0.controller.input_vel = 0
            self.odrv.axis0.requested_state = odrive.enums.AXIS_STATE_IDLE
        elif axis_vel_arr[0] > -self.odrv.axis0.controller.config.vel_limit and axis_vel_arr[0] < self.odrv.axis0.controller.config.vel_limit:
            self.odrv.axis0.requested_state = odrive.enums.AXIS_STATE_CLOSED_LOOP_CONTROL
            self.odrv.axis0.controller.config.control_mode = odrive.enums.CONTROL_MODE_VELOCITY_CONTROL
            self.odrv.axis0.controller.input_vel = axis_vel_arr[0]
        else:
            print("Invalid velocity")

        if axis_vel_arr[1] == 0:
            self.odrv.axis1.controller.input_vel = 0
            self.odrv.axis1.requested_state = odrive.enums.AXIS_STATE_IDLE
        elif axis_vel_arr[1] > -self.odrv.axis0.controller.config.vel_limit and axis_vel_arr[1] < self.odrv.axis0.controller.config.vel_limit:
            self.odrv.axis1.requested_state = odrive.enums.AXIS_STATE_CLOSED_LOOP_CONTROL
            self.odrv.axis1.controller.config.control_mode = odrive.enums.CONTROL_MODE_VELOCITY_CONTROL
            self.odrv.axis1.controller.input_vel = axis_vel_arr[1]
        else:
            print("Invalid velocity")
