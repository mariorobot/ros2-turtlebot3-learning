import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, termios, tty, select, time

class Teleop(Node):
    def __init__(self):
        super().__init__('teleop_v2')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # 当前速度
        self.linear = 0.0
        self.angular = 0.0

        # 目标速度
        self.target_linear = 0.0
        self.target_angular = 0.0

        # 参数
        self.max_linear = 0.22
        self.max_angular = 1.0
        self.step = 0.02   # 加速步长

    def get_key(self):
        # 非阻塞读取键盘
        dr, dw, de = select.select([sys.stdin], [], [], 0.1)
        if dr:
            return sys.stdin.read(1)
        return None

    def run(self):
        print("控制：w/s/a/d，空格停止，q退出")

        while True:
            key = self.get_key()

     
            if key == 'w':
                self.target_linear = self.max_linear
            elif key == 's':
                self.target_linear = -self.max_linear
            elif key == 'a':
                self.target_angular = self.max_angular
            elif key == 'd':
                self.target_angular = -self.max_angular
            elif key == ' ':
                self.target_linear = 0.0
                self.target_angular = 0.0
            elif key == 'q':
                break

            self.linear = self._approach(self.linear, self.target_linear)
            self.angular = self._approach(self.angular, self.target_angular)


            twist = Twist()
            twist.linear.x = self.linear
            twist.angular.z = self.angular
            self.pub.publish(twist)

            print(f"\r线速度: {self.linear:.2f} 角速度: {self.angular:.2f}", end="")

            time.sleep(0.1)

        self.stop_robot()

    def _approach(self, current, target):
        if current < target:
            current = min(current + self.step, target)
        elif current > target:
            current = max(current - self.step, target)
        return current

    def stop_robot(self):
        twist = Twist()
        for _ in range(5):
            self.pub.publish(twist)
        print("\n已停止机器人")


def main():
    rclpy.init()

    old_attr = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    node = Teleop()
    try:
        node.run()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_attr)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()