#!/usr/bin/env python3
import rospy
import cv2 as cv

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

def camera_callback(data):
    bridge = CvBridge()

    try:
        cv_image = bridge.imgmsg_to_cv2(data, desired_encoding="bgr8")
    except CvBridgeError as e:
        rospy.logerr(e)

    image = cv.resize(cv_image, (360, 360))

    cv.imshow("Image", image)
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