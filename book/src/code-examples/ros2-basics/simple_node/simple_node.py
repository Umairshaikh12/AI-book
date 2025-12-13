#!/usr/bin/env python3

import rclpy
from rclpy.node import Node


class SimpleNode(Node):
    def __init__(self):
        # Initialize the node with a name
        super().__init__('simple_node')
        
        # Log a message indicating the node has started
        self.get_logger().info('SimpleNode has been started')
        
        # Create a timer to execute a callback periodically
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.counter = 0

    def timer_callback(self):
        """Callback function that executes every second"""
        self.get_logger().info(f'Hello ROS 2! Count: {self.counter}')
        self.counter += 1


def main(args=None):
    # Initialize the ROS 2 communication
    rclpy.init(args=args)
    
    # Create the node
    simple_node = SimpleNode()
    
    # Keep the node alive
    try:
        rclpy.spin(simple_node)
    except KeyboardInterrupt:
        pass
    
    # Clean up
    simple_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()