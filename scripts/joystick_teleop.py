#!/usr/bin/env python
import rospy
import pygame

from ackermann_msgs.msg import AckermannDriveStamped

import sys, select, termios, tty

# See the pygame docs for more joystick capabilities:
# https://www.pygame.org/docs/ref/joystick.html

steer_joystick = 0.0
drive_joystick = 0.0
is_enabled = False

def readJoystick():
  global joystick
  global steer_joystick
  global drive_joystick
  global is_enabled
  pygame.event.pump()
  steer_joystick = -joystick.get_axis(0)
  drive_joystick = -joystick.get_axis(4)
  is_enabled = joystick.get_button(4) == 1


def initJoystick():
  global joystick
  pygame.init()

  # Initialize the joysticks
  pygame.joystick.init()
  # Get count of joysticks
  joystick_count = pygame.joystick.get_count()

  if joystick_count < 1:
    print('No joystick found!')
    sys.exit(0)

  joystick = pygame.joystick.Joystick(0)
  joystick.init()

  # Get the name from the OS for the controller/joystick
  name = joystick.get_name()
  print("Joystick name: {}".format(name) )

  if (joystick.get_numbuttons() < 5):
    print("Error: expected buttion[4] to be valid!")
    sys.exit(1)

  if (joystick.get_numaxes() < 4):
    print("Error: expected axis[0] and axis[3] to be valid!")
    sys.exit(1)

if __name__=="__main__":
  global steer_joystick
  global drive_joystick
  global is_enabled
  pub = rospy.Publisher('commands/ackermann',
                      AckermannDriveStamped,
                      queue_size=5)
  rospy.init_node('joystick_teleop')
  rate = rospy.Rate(20) # 20hz
  initJoystick()
  speed = 1.0
  turn = 0.25
  while not rospy.is_shutdown():
    readJoystick()
    msg = AckermannDriveStamped();
    msg.header.stamp = rospy.Time.now();
    msg.header.frame_id = "base_link";

    print("Drive: {:.2f}% Steer: {:.2f}%  Enabled: {}".format(
        drive_joystick, steer_joystick, is_enabled))

    msg.drive.speed = drive_joystick * speed;
    msg.drive.acceleration = 1;
    msg.drive.jerk = 1;
    msg.drive.steering_angle = steer_joystick * turn
    msg.drive.steering_angle_velocity = 1

    pub.publish(msg)
    rate.sleep()

  msg = AckermannDriveStamped();
  msg.header.stamp = rospy.Time.now();
  msg.header.frame_id = "base_link";

  msg.drive.speed = 0;
  msg.drive.acceleration = 1;
  msg.drive.jerk = 1;
  msg.drive.steering_angle = 0
  msg.drive.steering_angle_velocity = 1
  pub.publish(msg)

  # Close the window and quit.
  # If you forget this line, the program will 'hang'
  # on exit if running from IDLE.
  pygame.quit ()