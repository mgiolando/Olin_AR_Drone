#!/usr/bin/env python
# Copyright (c) 2012, Falkor Systems, Inc.  All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.  Redistributions
# in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.  THIS SOFTWARE IS
# PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import roslib
roslib.load_manifest('PredatorPrey')

import sys
import rospy
import math
import pid
#import cv2
#import numpy as np
#from cv_bridge import CvBridge, CvBridgeError

from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from sensor_msgs.msg import Joy, Image
from ardrone_autonomy.msg import Navdata
from ardrone_autonomy.srv import LedAnim

TimerDuration = .05

class ArdroneFollow:
    def __init__( self ):

        self.goal_vel_pub = rospy.Publisher( "goal_vel", Twist )
        self.led_service = rospy.ServiceProxy( "ardrone/setledanimation", LedAnim )
        self.timer = rospy.Timer( rospy.Duration( TimerDuration ), self.timer_cb, False )

        self.angularZlimit = 3.141592 / 2
        self.linearXlimit = 1.0
        self.linearZlimit = 2.0

        self.yPid = pid.Pid2( 0.0010, 0.0, 0.0)
        self.xPid = pid.Pid2( 0.0020, 0.0, 0.0)#this one works great!!!
        self.zPid = pid.Pid2( 0.0030, 0.0, 0.006)

        self.found_point = Point( 0, 0, -1 )
        self.old_cmd = self.current_cmd = Twist()

        self.manual_cmd = False
        self.auto_cmd = True
        self.lastAnim = -1;

        self.navdata_sub = rospy.Subscriber( "ardrone/navdata", Navdata, self.navdata_cb )
        self.navdata = None
        self.states = { 0: 'Unknown',
                        1: 'Init',
                        2: 'Landed',
                        3: 'Flying',
                        4: 'Hovering',
                        5: 'Test',
                        6: 'Taking Off',
                        7: 'Goto Fix Point',
                        8: 'Landing',
                        9: 'Looping' }
        #self.goal_vel_pub.publish( Twist() )

    def setLedAnim( self, animType, freq = 10 ):
        #if self.lastAnim == type:
        #    return
        self.led_service( type = animType, freq = freq, duration = 1 )
        #self.lastAnim = type

    def navdata_cb( self, data ):
        self.navdata = data

    def hover( self ):
        hoverCmd = Twist()
        self.goal_vel_pub.publish( hoverCmd )

    def hover_cmd_cb( self, data ):
        self.hover()

    def timer_cb( self, event ):

        # If we haven't received a found point in a second, let found_point be
        # (0,0,-1)
        #if ( self.found_time == None or
        #     ( rospy.Time.now() - self.found_time ).to_sec() > 1 ):
        if event.last_real == None:
            dt = 0
        else:
            dt = ( event.current_real - event.last_real ).to_sec()

        self.current_cmd = Twist()

        if self.navdata and self.navdata.tags_count == 1:
                self.current_cmd.angular.z = self.xPid.update( 500, self.navdata.tags_xc[0], dt )
                self.current_cmd.linear.z = self.yPid.update( 500, self.navdata.tags_yc[0] , dt )
                self.current_cmd.linear.x = -self.zPid.update( 100, self.navdata.tags_distance[0], dt )    
                self.setLedAnim( 3 )
        #else:
        #    self.setLedAnim( 6 )
        self.goal_vel_pub.publish( self.current_cmd )


def main():
    rospy.init_node( 'ardrone_follow' , log_level=rospy.DEBUG)
    af = ArdroneFollow()

    try:
        rospy.spin()
    except KeyboardInterrupt:
        print "Keyboard interrupted"

if __name__ == '__main__':
    main()
