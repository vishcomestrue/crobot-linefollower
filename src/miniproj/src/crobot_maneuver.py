#!/usr/bin/env python3
import rospy
import cv2 as cv
import numpy
from math import floor

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

def velPub(data):
    velocity_publisher = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
    velocity_publisher.publish(data)

def camera_callback(data):
    bridge = CvBridge()
    twist = Twist()

    try:
        cv_image = bridge.imgmsg_to_cv2(data, desired_encoding="bgr8")
    except CvBridgeError as e:
        rospy.logerr(e)

    hsv_image = cv.cvtColor(cv_image, cv.COLOR_BGR2HSV)
    lower_black = numpy.array([0, 0, 0])
    upper_black = numpy.array([10, 10, 10])

    mask_image = cv.inRange(hsv_image, lower_black, upper_black)

    h, w, d = cv_image.shape

    threshold_left = floor(3*(h/5))
    threshold_right = floor((3*(h/5)) + (w/10))

    mask_image[0:threshold_left, 0:w] = 0
    mask_image[threshold_right:h, 0:w] = 0

    M = cv.moments(mask_image)

    if M['m00'] > 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        cv.circle(mask_image, (cx, cy), 10, (0,0,255), -1)
      
        error_x = cx - (w/2)
        twist.linear.x = -0.2
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        if(abs(error_x) > 5):
            twist.linear.x = -0.1
            twist.angular.z = -(float(error_x)/800)
        velPub(twist)

    # cv.imshow("Orig Image", cv_image)
    # cv.imshow("HSV Image", hsv_image)
    cv.imshow("Mask Image", mask_image)
    # image = cv.resize(cv_image, (400, 400))
    # cv.imshow("Image", image)
    cv.waitKey(3)

def crobot():
    image_subcriber = rospy.Subscriber("/camera1/image_raw", Image, camera_callback)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        rospy.loginfo("shutting down")
    cv.destroyAllWindows()

if __name__ == "__main__":
    rospy.init_node("camera_capture_read", anonymous=False)
    try:
        crobot()
    except rospy.ROSInterruptException:
        pass