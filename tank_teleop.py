import os
import select
import sys

from motor_control import *
import odrive
from odrive.enums import *
import time
from motor_config import *

if os.name == 'nt':
    import msvcrt
else:
    import termios
    import tty

tankControl = DifControl()

TANK_MAX_LIN_VEL = 10
TANK_MAX_ANG_VEL = 32

LIN_VEL_STEP_SIZE = 2
ANG_VEL_STEP_SIZE = 4

TANK_POS_STEP_SIZE = 1
TANK_POS_LIMIT = 6

msg = """
Instruction control!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease linear velocity (TANK : ~ 10)
a/d : increase/decrease angular velocity (TANK : ~ 22)

space key, s : force stop

CTRL-C to quit
"""

e = """
Communications Failed
"""



def get_key(settings):
    if os.name == 'nt':
        return msvcrt.getch().decode('utf-8')
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def print_vels(target_linear_velocity, target_angular_velocity):
    print('currently:\tlinear velocity {0}\t angular velocity {1} '.format(
        target_linear_velocity,
        target_angular_velocity))


def make_simple_profile(output, input, slop):
    if input > output:
        output = min(input, output + slop)
    elif input < output:
        output = max(input, output - slop)
    else:
        output = input

    return output


def constrain(input_vel, low_bound, high_bound):
    if input_vel < low_bound:
        input_vel = low_bound
    elif input_vel > high_bound:
        input_vel = high_bound
    else:
        input_vel = input_vel

    return input_vel


def check_linear_limit_velocity(velocity):
    return constrain(velocity, -TANK_MAX_LIN_VEL, TANK_MAX_LIN_VEL)


def check_angular_limit_velocity(velocity):
    return constrain(velocity, -TANK_MAX_ANG_VEL, TANK_MAX_ANG_VEL)

def check_limit_position(position):
    return constrain(position, -TANK_POS_LIMIT, TANK_POS_LIMIT)


def main():
    global tankControl
    settings = None
    if os.name != 'nt':
        settings = termios.tcgetattr(sys.stdin)

    status = 0
    target_linear_velocity = 0.0
    target_angular_velocity = 0.0
    control_linear_velocity = 0.0
    control_angular_velocity = 0.0
    target_pos_left_forward = 0.0
    target_pos_right_forward = 0.0
    target_pos_left_backward = 0.0
    target_pos_right_backward = 0.0

    try:
        print(msg)
        while(1):
            key = get_key(settings)
            if key == 'w':
                target_linear_velocity =\
                    check_linear_limit_velocity(target_linear_velocity - LIN_VEL_STEP_SIZE)
                status = status + 1
                print_vels(target_linear_velocity, target_angular_velocity)
            elif key == 'x':
                target_linear_velocity =\
                    check_linear_limit_velocity(target_linear_velocity + LIN_VEL_STEP_SIZE)
                status = status + 1
                print_vels(target_linear_velocity, target_angular_velocity)
            elif key == 'a':
                target_angular_velocity =\
                    check_angular_limit_velocity(target_angular_velocity + ANG_VEL_STEP_SIZE)
                status = status + 1
                print_vels(target_linear_velocity, target_angular_velocity)
            elif key == 'd':
                target_angular_velocity =\
                    check_angular_limit_velocity(target_angular_velocity - ANG_VEL_STEP_SIZE)
                status = status + 1
                print_vels(target_linear_velocity, target_angular_velocity)
            elif key == 'q':
                target_pos_left_forward =\
                    check_limit_position(target_pos_left_forward + TANK_POS_STEP_SIZE)
                print("Current_left_position:" + str(target_pos_left_forward))
                tankControl.flippers[0].setPosition([target_pos_left_backward, target_pos_left_forward])
            elif key == 'z':
                target_pos_left_backward =\
                    check_limit_position(target_pos_left_backward + TANK_POS_STEP_SIZE)
                print("Current_left_position:" + str(target_pos_left_backward))
                tankControl.flippers[0].setPosition([target_pos_left_backward, target_pos_left_forward])
            elif key == 'e':
                target_pos_right_forward =\
                    check_limit_position(target_pos_right_forward + TANK_POS_STEP_SIZE)
                print("Current_left_position:" + str(target_pos_right_forward))
                tankControl.flippers[1].setPosition([target_pos_right_forward, target_pos_right_backward])
            elif key == 'c':
                target_pos_right_backward =\
                    check_limit_position(target_pos_right_backward + TANK_POS_STEP_SIZE)
                print("Current_left_position:" + str(target_pos_right_backward))
                tankControl.flippers[1].setPosition([target_pos_right_forward, target_pos_right_backward])

            elif key == 'r':
                target_pos_left_forward =\
                    check_limit_position(target_pos_left_forward - TANK_POS_STEP_SIZE)
                print("Current_pos_left_forward:" + str(target_pos_left_forward))
                tankControl.flippers[0].setPosition([target_pos_left_backward, target_pos_left_forward])
            elif key == 'y':
                target_pos_right_forward =\
                    check_limit_position(target_pos_right_forward - TANK_POS_STEP_SIZE)
                print("Current_left_position:" + str(target_pos_right_forward))
                tankControl.flippers[1].setPosition([target_pos_right_forward, target_pos_right_backward])
            elif key == 'v':
                target_pos_left_backward =\
                    check_limit_position(target_pos_left_backward - TANK_POS_STEP_SIZE)
                print("Current_left_position:" + str(target_pos_left_backward))
                tankControl.flippers[0].setPosition([target_pos_left_backward, target_pos_left_forward])
            elif key == 'n':
                target_pos_right_backward =\
                    check_limit_position(target_pos_right_backward - TANK_POS_STEP_SIZE)
                print("Current_left_position:" + str(target_pos_right_backward))
                tankControl.flippers[1].setPosition([target_pos_right_forward, target_pos_right_backward])
            elif key == ' ' or key == 's':
                target_linear_velocity = 0.0
                control_linear_velocity = 0.0
                target_angular_velocity = 0.0
                control_angular_velocity = 0.0
                target_pos_left_forward = 0.0
                target_pos_right_forward = 0.0
                target_pos_left_backward = 0.0
                target_pos_right_backward = 0.0
                print_vels(target_linear_velocity, target_angular_velocity)
            else:
                if (key == '\x03'):
                    break

            if status == 20:
                print(msg)
                tankControl.caterpillar.giveCurrent(tankControl.caterpillar.odrv)
                tankControl.caterpillar.giveVoltage(tankControl.caterpillar.odrv)
                status = 0

            #twist = Twist()
            control_linear_velocity = make_simple_profile(
                control_linear_velocity,
                target_linear_velocity,
                (LIN_VEL_STEP_SIZE / 2.0))
            tankControl.set_speed(control_linear_velocity, 0, control_angular_velocity)
            #print(target_pos_left_backward)
            #print(target_pos_left_forward)
            arr = tankControl.flippers[0].getPos(tankControl.flippers[0].odrv)
            arr = tankControl.flippers[1].getPos(tankControl.flippers[0].odrv)
            #twist.linear.x = control_linear_velocity
            #twist.linear.y = 0.0
            #twist.linear.z = 0.0

            control_angular_velocity = make_simple_profile(
                control_angular_velocity,
                target_angular_velocity,
                (ANG_VEL_STEP_SIZE / 2.0))

            #twist.angular.x = 0.0
            #twist.angular.y = 0.0
            #twist.angular.z = control_angular_velocity

            #pub.publish(twist)

    except Exception as e:
        print(e)

    finally:
        tankControl.set_speed(0, 0, 0)
        if os.name != 'nt':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


if __name__ == '__main__':
    main()
