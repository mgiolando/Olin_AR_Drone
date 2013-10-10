#!/usr/bin/env python

# The Joystick Controller Node for the tutorial "Up and flying with the AR.Drone and ROS | Joystick Control"
# https://github.com/mikehamer/ardrone_tutorials

# This controller implements the base DroneVideoDisplay class, the DroneController class and subscribes to joystick messages

# Import the ROS libraries, and load the manifest file which through <depend package=... /> will give us access to the project dependencies
import roslib; roslib.load_manifest('ardrone_tutorials')
import rospy

# Load the DroneController class, which handles interactions with the drone, and the DroneVideoDisplay class, which handles video display
from drone_controller import BasicDroneController
from drone_video_display import DroneVideoDisplay

# Import the joystick message
from sensor_msgs.msg import Joy

# Finally the GUI libraries
from PySide import QtCore, QtGui


def RunScript():
	rospy.loginfo("Starting Script")
	rospy.Timer(5.0, controller.CallFlattrim(),True)
	controller.Flattrim()
	# rospy.sleep(5.)
	rospy.loginfo("Takeing Off")
	controller.SendTakeoff()
	controller.SendHover()
	rospy.Timer(5.0, controller.SendLand(), True)
	# rospy.sleep(5.)
	controller.SendLand()
	rospy.loginfo("Landed")

# Setup the application
if __name__=='__main__':
	import sys
	# Firstly we setup a ros node, so that we can communicate with the other packages
	rospy.init_node('script_controller')


	# Now we construct our Qt Application and associated controllers and windows
	app = QtGui.QApplication(sys.argv)
	display = DroneVideoDisplay()
	controller = BasicDroneController()

	# print'running script'
	# RunScript()
	
	# executes the QT application
	display.show()
	RunScript()
	status = app.exec_()

	# and only progresses to here once the application has been shutdown
	rospy.signal_shutdown('Great Flying!')
	sys.exit(status)