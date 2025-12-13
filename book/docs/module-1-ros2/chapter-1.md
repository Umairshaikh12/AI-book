# Chapter 1: Introduction to Nodes

## Overview

In this chapter, we'll dive deep into ROS 2 nodes, the fundamental building blocks of any ROS system. We'll learn what nodes are, how they function within the ROS ecosystem, and how to create our first ROS 2 node using Python.

## Learning Objectives

By the end of this chapter, you will be able to:
- Define what a ROS 2 node is
- Create a simple ROS 2 node in Python
- Understand the lifecycle of a ROS 2 node
- Explain how nodes fit into the overall ROS architecture

## What is a Node?

A node is an executable that uses ROS 2 to communicate with other nodes. Nodes are the processes that perform computation. In a distributed system, many nodes can run on different devices or machines. ROS 2 is designed to have many nodes working together to form a complete robot application.

### Key Characteristics of Nodes:
- A node is a single executable that uses the ROS 2 client library
- Multiple nodes can be combined to form a complete robotic application
- Each node can perform specific tasks, such as sensor data processing, actuator control, or planning
- Nodes are the fundamental unit of computation in ROS 2

## Node Architecture

ROS 2 nodes communicate with each other through a graph architecture. The ROS 2 graph includes:
- Nodes: The computational elements
- Topics: Streams of data that can be published or subscribed to
- Services: Synchronous request/response communication
- Actions: Synchronous request/reply with feedback and goal control
- Parameters: Configuration values that are shared among nodes

Nodes are managed by the ROS 2 execution model, which handles their lifecycle and communication.

## Creating Your First Node

Let's create a simple ROS 2 node in Python. We'll create a node that simply logs a message periodically.

First, create the file structure:
```
book/src/code-examples/ros2-basics/
├── simple_node/
│   ├── __init__.py
│   └── simple_node.py
```

In `simple_node.py`, we'll create our first node:

```python
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
```

## Understanding the Node Structure

Let's break down the components of our node:

1. **Import Statements**:
   - `rclpy`: The Python client library for ROS 2
   - `Node`: The base class for creating ROS 2 nodes

2. **Node Class**:
   - Inherits from `rclpy.node.Node`
   - The `__init__` method initializes the node with a name
   - The `get_logger()` method provides an interface for logging

3. **Timer**:
   - Creates a timer that executes a callback function at regular intervals
   - In this example, it executes every 1.0 second

4. **Main Function**:
   - Initializes the ROS 2 communication
   - Creates and runs the node
   - Handles cleanup when the node is shut down

## Node Lifecycle

ROS 2 nodes have a specific lifecycle that includes:

1. **Unconfigured**: The node has been created but not yet configured
2. **Inactive**: The node is configured but not executing
3. **Active**: The node is fully operational and executing
4. **Finalized**: The node has been shut down and is no longer active

## Running the Node

To run this node:

1. Make sure your ROS 2 environment is sourced:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. Navigate to your ROS 2 workspace:
   ```bash
   cd ~/physical_ai_ws
   ```

3. Source your workspace:
   ```bash
   source install/setup.bash
   ```

4. Run the node:
   ```bash
   ros2 run simple_node simple_node
   ```

## Common Node Patterns

### Publisher Node
A node that publishes messages to topics:
```python
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
```

### Subscriber Node
A node that subscribes to topics:
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SubscriberNode(Node):
    def __init__(self):
        super().__init__('subscriber_node')
        self.subscription = self.create_subscription(
            String,
            'topic_name',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')
```

## Summary

In this chapter, we've learned about ROS 2 nodes, which are the fundamental building blocks of any ROS system. We created a simple node and learned about its structure and lifecycle. In the next chapter, we'll explore topics and how nodes communicate through publish-subscribe patterns.

## Exercises

1. Modify the simple node to publish a message instead of just logging.
2. Create a second node that subscribes to the message published by the first node.
3. Add a parameter to control the frequency of the timer callback in the simple node.