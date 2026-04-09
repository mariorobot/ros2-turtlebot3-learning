#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry

from tf_transformations import euler_from_quaternion


class Turtlebot3Drive(Node):

    def __init__(self):
        super().__init__('autodrive_node')

        # ===== 状态定义 =====
        self.GET_TB3_DIRECTION = 0
        self.TB3_DRIVE_FORWARD = 1
        self.TB3_RIGHT_TURN = 2
        self.TB3_LEFT_TURN = 3

        self.state = self.GET_TB3_DIRECTION

        # ===== 数据初始化 =====
        self.scan_data = [0.0, 0.0, 0.0]  # CENTER, LEFT, RIGHT
        self.robot_pose = 0.0
        self.prev_robot_pose = 0.0

        # ===== Publisher =====
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # ===== Subscriber =====
        self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10
        )

        self.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10
        )

        # ===== Timer =====
        self.timer = self.create_timer(0.01, self.update_callback)

        self.get_logger().info("Turtlebot3 Python avoidance node started")

    # ===== ODOM 回调 =====
    def odom_callback(self, msg):
        q = msg.pose.pose.orientation
        _, _, yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.robot_pose = yaw

    # ===== SCAN 回调 =====
    def scan_callback(self, msg):
        scan_angles = [0, 30, 330]
        for i, angle_idx in enumerate(scan_angles):
            if math.isinf(msg.ranges[angle_idx]):
                self.scan_data[i] = msg.range_max
            else:
                self.scan_data[i] = msg.ranges[angle_idx]

    # ===== 发送速度 =====
    def update_cmd_vel(self, linear, angular):
        twist = Twist()
        twist.linear.x = linear
        twist.angular.z = angular
        self.cmd_vel_pub.publish(twist)

    # ===== 主状态机 =====
    def update_callback(self):
        CENTER = 0
        LEFT = 1
        RIGHT = 2

        check_forward_dist = 0.7
        check_side_dist = 0.6
        escape_range = math.radians(30.0)

        if self.state == self.GET_TB3_DIRECTION:

            if self.scan_data[CENTER] > check_forward_dist:

                if self.scan_data[LEFT] < check_side_dist:
                    self.prev_robot_pose = self.robot_pose
                    self.state = self.TB3_RIGHT_TURN

                elif self.scan_data[RIGHT] < check_side_dist:
                    self.prev_robot_pose = self.robot_pose
                    self.state = self.TB3_LEFT_TURN

                else:
                    self.state = self.TB3_DRIVE_FORWARD

            else:
                self.prev_robot_pose = self.robot_pose
                self.state = self.TB3_RIGHT_TURN

        elif self.state == self.TB3_DRIVE_FORWARD:
            self.update_cmd_vel(0.2, 0.0)
            self.state = self.GET_TB3_DIRECTION

        elif self.state == self.TB3_RIGHT_TURN:
            if abs(self.prev_robot_pose - self.robot_pose) >= escape_range:
                self.state = self.GET_TB3_DIRECTION
            else:
                self.update_cmd_vel(0.0, -0.5)

        elif self.state == self.TB3_LEFT_TURN:
            if abs(self.prev_robot_pose - self.robot_pose) >= escape_range:
                self.state = self.GET_TB3_DIRECTION
            else:
                self.update_cmd_vel(0.0, 0.5)

        else:
            self.state = self.GET_TB3_DIRECTION


def main(args=None):
    rclpy.init(args=args)
    node = Turtlebot3Drive()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()