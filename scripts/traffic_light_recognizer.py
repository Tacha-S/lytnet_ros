#!/usr/bin/env python
# -*- coding:utf-8 -*-
import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np

from cv_bridge import CvBridge, CvBridgeError
import rospkg
import rospy
from sensor_msgs.msg import Image

from lytnet import LYTNet


class TrafficLightRecognizer(object):
    def __init__(self):
        cuda_available = torch.cuda.is_available()

        ros_pack = rospkg.RosPack()
        package_path = ros_pack.get_path('lytnet_ros')
        model = rospy.get_param('~model', package_path + '/models/LytNetV2_weights')

        self.net = LYTNet()
        checkpoint = torch.load(model)
        self.net.load_state_dict(checkpoint)
        self.net.eval()

        if cuda_available:
            self.net = self.net.cuda()

        self.__labels = ['red', 'green', 'countdown_green', 'countdown_blank', 'none']

        self.__cv_bridge = CvBridge()

        rospy.Subscriber('~image', Image, self.callback, queue_size=1)

    def callback(self, msg):
        try:
            color_image = self.__cv_bridge.imgmsg_to_cv2(msg, "bgr8")
        except CvBridgeError as e:
            rospy.logerr('Converting Image Error. ' + str(e))
            return

        input_image = transforms.ToTensor()(color_image)
        input_image = input_image.unsqueeze(0)
        input_image = torch.nn.functional.upsample(input_image, (567, 768))
        # input_image = torch.nn.functional.upsample(input_image, (657, 876))
        pred_classes, pred_direc = self.net(input_image.cuda())
        _, predicted = torch.max(pred_classes, 1)

        rospy.loginfo(self.__labels[predicted.cpu().numpy()[0]])


if __name__ == '__main__':
    rospy.init_node('traffic_light_recognizer')
    node = TrafficLightRecognizer()
    rospy.spin()
