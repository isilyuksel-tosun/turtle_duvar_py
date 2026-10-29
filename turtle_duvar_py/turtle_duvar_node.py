#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class TurtleDuvarNode(Node):
    def __init__(self):
        super().__init__('turtle_duvar_node')

        # BONUS: Hız ve sınır değerlerini parametre yapma
        self.declare_parameter('linear_speed', 2.0)
        self.declare_parameter('angular_speed', 1.8)
        self.declare_parameter('min_limit', 1.0)
        self.declare_parameter('max_limit', 10.0)

        # 2. Abone (Subscriber): /turtle1/pose dinleniyor
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # 3. Yayıncı (Publisher): /turtle1/cmd_vel konusuna hız komutu
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Konum değişkenleri
        self.current_x = 0.0
        self.current_y = 0.0
        self.pose_received = False

        # Zamanlayıcılar (Timers)
        self.cmd_timer = self.create_timer(0.1, self.control_loop)  # 10 Hz Hareket Döngüsü
        self.log_timer = self.create_timer(1.0, self.log_position)  # 4. LOG: Saniyede bir (1 Hz)

        self.get_logger().info('Duvardan Kaçan Kaplumbağa Düğümü Başlatıldı.')

    def pose_callback(self, msg: Pose):
        self.current_x = msg.x
        self.current_y = msg.y
        self.pose_received = True

    def log_position(self):
        # 4. LOG: Konumu saniyede bir get_logger().info() ile yazdırma
        if self.pose_received:
            self.get_logger().info(
                f"[TELEMETRİ] Konum -> X: {self.current_x:.2f}, Y: {self.current_y:.2f}"
            )

    def control_loop(self):
        if not self.pose_received:
            return

        # Bonus: Parametre değerlerini dinamik okuma
        linear_speed = self.get_parameter('linear_speed').value
        angular_speed = self.get_parameter('angular_speed').value
        min_limit = self.get_parameter('min_limit').value
        max_limit = self.get_parameter('max_limit').value

        msg = Twist()

        # 3. Yayıncı Mantığı: x veya y 1.0'dan küçük ya da 10.0'dan büyükse dön
        if (self.current_x < min_limit or self.current_x > max_limit or
            self.current_y < min_limit or self.current_y > max_limit):
            # Duvara sıkışmaması ve kavis çizerek güvenli alana dönmesi için hem ileri hem açısal hız
            msg.linear.x = linear_speed * 0.4
            msg.angular.z = angular_speed
        else:
            msg.linear.x = linear_speed
            msg.angular.z = 0.0

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleDuvarNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
