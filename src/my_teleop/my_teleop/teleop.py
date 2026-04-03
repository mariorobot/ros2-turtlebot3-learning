import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, termios, tty

class Teleop(Node):
    def __init__(self):
        super().__init__('teleop_python')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

    def run(self):
        print("控制：w/s/a/d，q退出")
        while True:
            key = self.get_key()
            twist = Twist()

            if key == 'w':
                twist.linear.x = 0.2
            elif key == 's':
                twist.linear.x = -0.2
            elif key == 'a':
                twist.angular.z = 0.5
            elif key == 'd':
                twist.angular.z = -0.5
            elif key == 'q':
                break

            self.pub.publish(twist)


def main():
    rclpy.init()
    node = Teleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
