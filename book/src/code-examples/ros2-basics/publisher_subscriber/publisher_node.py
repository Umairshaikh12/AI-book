#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class PublisherNode(Node):
    def __init__(self):
        super().__init__('publisher_node')
        self.publisher = self.create_publisher(String, 'topic_name', 10)
        self.timer = self.create_timer(0.5, self.publish_message)
        self.count = 0

    def publish_message(self):
        msg = String()
        msg.data = f'Hello, world! {self.count}'
        self.publisher.publish(msg)
        self.count += 1
        self.get_logger().info(f'Publishing: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    publisher = PublisherNode()
    
    try:
        rclpy.spin(publisher)
    except KeyboardInterrupt:
        pass
    
    publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()