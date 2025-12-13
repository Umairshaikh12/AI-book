# Chapter 3: rclpy Integration

## Overview

In this chapter, we'll dive deep into rclpy, the Python client library for ROS 2. We'll explore how to use rclpy to create sophisticated nodes, handle parameters, use actions, and manage complex robotic systems. rclpy provides the Python interface to the ROS 2 ecosystem, allowing you to write ROS 2 nodes in Python.

## Learning Objectives

By the end of this chapter, you will be able to:
- Effectively use rclpy to create complex ROS 2 nodes
- Implement parameter handling in ROS 2 nodes
- Create and use actions for goal-oriented tasks
- Handle exceptions and errors in ROS 2 nodes
- Apply advanced rclpy patterns and best practices

## Advanced Node Creation with rclpy

So far, we've seen basic node creation using rclpy. Now let's explore more advanced node patterns:

### Creating a Node with Multiple Publishers and Subscribers

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class AdvancedRobotController(Node):
    def __init__(self):
        super().__init__('advanced_robot_controller')
        
        # Publishers
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_publisher = self.create_publisher(String, '/robot_status', 10)
        
        # Subscribers
        self.laser_subscriber = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            10)
        
        self.velocity_subscriber = self.create_subscription(
            Twist,
            '/cmd_vel_input',
            self.velocity_callback,
            10)
        
        # Timer for control loop
        self.control_timer = self.create_timer(0.1, self.control_loop)  # 10 Hz
        
        # Internal state
        self.current_velocity = Twist()
        self.laser_scan = None
        self.status = "Idle"
        
        self.get_logger().info('Advanced Robot Controller node initialized')

    def laser_callback(self, msg):
        """Handle laser scan data"""
        self.laser_scan = msg
        # Process laser data to detect obstacles
        if self.detect_obstacle():
            self.status = "Obstacle Detected"
        else:
            self.status = "Clear Path"

    def velocity_callback(self, msg):
        """Handle external velocity commands"""
        self.current_velocity = msg

    def detect_obstacle(self):
        """Detect obstacles in laser scan"""
        if self.laser_scan is None:
            return False
            
        # Check if there are obstacles within 1 meter
        for range_val in self.laser_scan.ranges:
            if 0.1 < range_val < 1.0:  # Obstacle within 1 meter
                return True
        return False

    def control_loop(self):
        """Main control loop"""
        # Publish current status
        status_msg = String()
        status_msg.data = self.status
        self.status_publisher.publish(status_msg)
        
        # Publish velocity command
        self.cmd_vel_publisher.publish(self.current_velocity)


def main(args=None):
    rclpy.init(args=args)
    controller = AdvancedRobotController()
    
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    
    controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Parameter Handling

Parameters in ROS 2 allow you to configure nodes without recompiling. rclpy provides functionality to declare, get, and set parameters:

### Declaring and Using Parameters

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import String


class ParameterizedNode(Node):
    def __init__(self):
        super().__init__('parameterized_node')
        
        # Declare parameters with default values
        self.declare_parameter('robot_name', 'robot1')
        self.declare_parameter('max_speed', 1.0)
        self.declare_parameter('safety_distance', 0.5)
        self.declare_parameter('debug_mode', False)
        
        # Access parameter values
        self.robot_name = self.get_parameter('robot_name').value
        self.max_speed = self.get_parameter('max_speed').value
        self.safety_distance = self.get_parameter('safety_distance').value
        self.debug_mode = self.get_parameter('debug_mode').value
        
        # Create publisher
        self.publisher = self.create_publisher(String, 'robot_info', 10)
        
        # Create timer
        self.timer = self.create_timer(1.0, self.publish_info)
        
        if self.debug_mode:
            self.get_logger().info(f'Debug mode enabled for {self.robot_name}')

    def publish_info(self):
        """Publish robot information based on parameters"""
        msg = String()
        msg.data = f'{self.robot_name} - Max Speed: {self.max_speed} m/s, Safety Distance: {self.safety_distance} m'
        self.publisher.publish(msg)

    def parameter_callback(self, parameter_list):
        """Handle parameter changes"""
        for param in parameter_list:
            if param.name == 'robot_name':
                self.robot_name = param.value
            elif param.name == 'max_speed':
                self.max_speed = param.value
            elif param.name == 'safety_distance':
                self.safety_distance = param.value
            elif param.name == 'debug_mode':
                self.debug_mode = param.value
        
        if self.debug_mode and param.name == 'debug_mode':
            self.get_logger().info(f'Debug mode enabled for {self.robot_name}')
        
        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = ParameterizedNode()
    
    # Add parameter callback
    node.add_on_set_parameters_callback(node.parameter_callback)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Actions

Actions in ROS 2 are used for long-running tasks that provide feedback and can be canceled. They're ideal for navigation, manipulation, and other goal-oriented tasks:

### Creating an Action Server

```python
#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            callback_group=None,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)

    def destroy(self):
        self._action_server.destroy()
        super().destroy_node()

    def goal_callback(self, goal_request):
        """Accept or reject a client request to begin an action"""
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Accept or reject a client request to cancel an action"""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """Execute the goal and provide feedback"""
        self.get_logger().info('Executing goal...')
        
        # Create feedback and result messages
        feedback_msg = Fibonacci.Feedback()
        result = Fibonacci.Result()
        
        # Initialize fibonacci sequence
        feedback_msg.sequence = [0, 1]
        
        # Compute fibonacci sequence up to requested order
        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                result.sequence = feedback_msg.sequence
                return result
            
            # Check if goal was aborted
            if not rclpy.ok():
                result.sequence = feedback_msg.sequence
                return result
            
            # Calculate next fibonacci number
            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])
            
            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Feedback: {feedback_msg.sequence}')
        
        # Set result and return
        goal_handle.succeed()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f'Result: {result.sequence}')
        return result


def main(args=None):
    rclpy.init(args=args)
    action_server = FibonacciActionServer()
    
    try:
        rclpy.spin(action_server)
    except KeyboardInterrupt:
        pass
    
    action_server.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Creating an Action Client

```python
#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):
    def __init__(self):
        super().__init__('fibonacci_action_client')
        self._action_client = ActionClient(
            self,
            Fibonacci,
            'fibonacci')

    def send_goal(self, order):
        # Wait for the action server to be available
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()
        
        # Create a goal message
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order
        
        # Send the goal
        self.get_logger().info(f'Sending goal with order {order}')
        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        
        # Add callbacks
        send_goal_future.add_done_callback(self.goal_response_callback)
        return send_goal_future

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback.sequence}')


def main(args=None):
    rclpy.init(args=args)
    action_client = FibonacciActionClient()
    
    # Send a goal
    action_client.send_goal(10)
    
    try:
        rclpy.spin(action_client)
    except KeyboardInterrupt:
        pass
    
    action_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Error Handling and Best Practices

### Exception Handling in ROS 2 Nodes

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import traceback


class RobustNode(Node):
    def __init__(self):
        super().__init__('robust_node')
        self.publisher = self.create_publisher(String, 'robust_topic', 10)
        self.timer = self.create_timer(1.0, self.robust_timer_callback)
        self.counter = 0

    def robust_timer_callback(self):
        """Timer callback with exception handling"""
        try:
            # Simulate potential failure
            if self.counter == 5:
                raise ValueError("Simulated error at counter 5")
            
            # Try to publish message
            msg = String()
            msg.data = f'Robust message #{self.counter}'
            self.publisher.publish(msg)
            self.get_logger().info(f'Published: {msg.data}')
            self.counter += 1
            
        except ValueError as e:
            self.get_logger().error(f'ValueError in timer callback: {e}')
            # Optionally reset or take corrective action
            self.counter += 1  # Skip the error point
        except Exception as e:
            self.get_logger().error(f'Unexpected error in timer callback: {e}')
            self.get_logger().error(traceback.format_exc())
            # Handle other exceptions appropriately


def main(args=None):
    rclpy.init(args=args)
    robust_node = RobustNode()
    
    try:
        rclpy.spin(robust_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        robust_node.get_logger().error(f'Fatal error: {e}')
    finally:
        robust_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Advanced rclpy Patterns

### Composition of Nodes (Multiple nodes in one process)

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ComposedNode(Node):
    def __init__(self):
        super().__init__('composed_node')
        
        # Initialize multiple logical nodes within this single process
        self.publisher_node1 = self.create_publisher(String, 'node1_topic', 10)
        self.publisher_node2 = self.create_publisher(String, 'node2_topic', 10)
        
        self.subscription_node1 = self.create_subscription(
            String, 'input_topic', self.input_callback, 10)
        
        self.timer = self.create_timer(1.0, self.publish_messages)
        self.counter = 0
        
    def input_callback(self, msg):
        """Handle input from external nodes"""
        self.get_logger().info(f'Received message: {msg.data}')
        
    def publish_messages(self):
        """Publish messages from both logical nodes"""
        msg1 = String()
        msg1.data = f'Node1 message #{self.counter}'
        self.publisher_node1.publish(msg1)
        
        msg2 = String()
        msg2.data = f'Node2 message #{self.counter}'
        self.publisher_node2.publish(msg2)
        
        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    composed_node = ComposedNode()
    
    try:
        rclpy.spin(composed_node)
    except KeyboardInterrupt:
        pass
    
    composed_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Summary

In this chapter, we've explored the advanced capabilities of rclpy, the Python client library for ROS 2. We've covered parameter handling, actions for goal-oriented tasks, error handling, and advanced node composition patterns. These techniques are essential for developing robust and sophisticated robotic systems in Python.

## Exercises

1. Create a node that uses parameters to control the behavior of a simple robot simulator.
2. Implement an action server that simulates moving to a specific location with feedback.
3. Create a node with proper exception handling that processes sensor data and continues operation even when errors occur.
4. Design a composed node that handles multiple robot sensors and actuators within a single process.