# Chapter 2: Topics and Services

## Overview

In this chapter, we'll explore two fundamental communication mechanisms in ROS 2: topics and services. These enable nodes to exchange information and coordinate their behavior in a distributed robotic system. Topics provide a way for nodes to publish and subscribe to streams of data, while services enable synchronous request/response communication.

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the publish/subscribe communication pattern using topics
- Create nodes that publish and subscribe to topics
- Understand the request/response communication pattern using services
- Create nodes that provide and use services
- Choose between topics and services based on communication requirements

## Topics: Publish-Subscribe Pattern

Topics are ROS 2's way of allowing nodes to exchange messages in a unidirectional manner using a publish-subscribe pattern. This pattern decouples the publisher from the subscriber, allowing multiple nodes to publish to and subscribe from the same topic.

### How Topics Work:
- Publishers send messages to a topic
- Subscribers receive messages from a topic
- Multiple publishers can publish to the same topic
- Multiple subscribers can subscribe to the same topic
- Publishers and subscribers are decoupled - they don't need to know about each other

### Example: Publisher Node

Let's create a publisher that sends messages about robot status:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random


class RobotStatusPublisher(Node):
    def __init__(self):
        super().__init__('robot_status_publisher')
        self.publisher = self.create_publisher(String, 'robot_status', 10)
        self.timer = self.create_timer(1.0, self.publish_status)
        self.status_messages = [
            "Operating normally",
            "Charging battery",
            "Navigation in progress",
            "Waiting for command",
            "Performing task"
        ]

    def publish_status(self):
        msg = String()
        msg.data = random.choice(self.status_messages)
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    publisher = RobotStatusPublisher()
    
    try:
        rclpy.spin(publisher)
    except KeyboardInterrupt:
        pass
    
    publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Example: Subscriber Node

Now, let's create a subscriber that listens to the robot status:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotStatusSubscriber(Node):
    def __init__(self):
        super().__init__('robot_status_subscriber')
        self.subscription = self.create_subscription(
            String,
            'robot_status',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'Received robot status: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    subscriber = RobotStatusSubscriber()
    
    try:
        rclpy.spin(subscriber)
    except KeyboardInterrupt:
        pass
    
    subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Running Publisher and Subscriber

1. Run the publisher in one terminal:
   ```bash
   ros2 run your_package_name robot_status_publisher
   ```

2. Run the subscriber in another terminal:
   ```bash
   ros2 run your_package_name robot_status_subscriber
   ```

## Services: Request-Response Pattern

Services in ROS 2 provide a synchronous request/response communication pattern. A service client sends a request to a service server and waits for a response. This is useful for operations that require a specific response or confirmation.

### How Services Work:
- A service server offers a specific functionality
- A service client requests that functionality
- The server processes the request and returns a response
- The client waits for the response before continuing

### Example: Service Definition

First, we need to define our service. Create a file `AddTwoInts.srv` in the `srv` folder of your package:

```
int64 a
int64 b
---
int64 sum
```

### Example: Service Server

```python
#!/usr/bin/env python3

from rclpy.node import Node
from rclpy import executors
import rclpy
from example_interfaces.srv import AddTwoInts


class AddTwoIntsService(Node):
    def __init__(self):
        super().__init__('add_two_ints_service')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning {request.a} + {request.b} = {response.sum}')
        return response


def main(args=None):
    rclpy.init(args=args)
    service = AddTwoIntsService()
    
    try:
        rclpy.spin(service)
    except KeyboardInterrupt:
        pass
    
    service.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Example: Service Client

```python
#!/usr/bin/env python3

from rclpy.node import Node
import rclpy
from example_interfaces.srv import AddTwoInts
import sys


class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')
        self.client = self.create_client(AddTwoInts, 'add_two_ints')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

        self.request = AddTwoInts.Request()

    def send_request(self, a, b):
        self.request.a = a
        self.request.b = b
        future = self.client.call_async(self.request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


def main(args=None):
    rclpy.init(args=args)
    client = AddTwoIntsClient()

    try:
        # Get numbers from command line arguments
        a = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        b = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    except ValueError:
        print("Please provide integer arguments")
        return

    response = client.send_request(a, b)
    if response:
        client.get_logger().info(f'Result of {a} + {b} = {response.sum}')
    else:
        client.get_logger().info('Service call failed')

    client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Running Service Server and Client

1. Run the service server:
   ```bash
   ros2 run your_package_name add_two_ints_service
   ```

2. Run the service client:
   ```bash
   ros2 run your_package_name add_two_ints_client 5 7
   ```

## Comparing Topics and Services

| Topic | Service |
|-------|---------|
| Asynchronous | Synchronous |
| Unidirectional publish/subscribe | Bidirectional request/response |
| Multiple publishers/subscribers allowed | One server, multiple clients |
| Decoupled timing | Client waits for response |
| Used for streaming data | Used for specific requests |

## Quality of Service (QoS) Settings

ROS 2 provides Quality of Service settings that allow you to configure how messages are delivered:

- **Reliability**: Best effort vs reliable delivery
- **Durability**: Volatile vs transient local
- **History**: Keep all vs keep last N messages
- **Depth**: Size of the message queue

Example with QoS settings:
```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

qos_profile = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    history=HistoryPolicy.KEEP_LAST
)

self.publisher = self.create_publisher(String, 'topic_name', qos_profile)
```

## Summary

In this chapter, we've learned how to use both topics and services in ROS 2. Topics enable unidirectional, asynchronous communication between multiple nodes, while services provide synchronous request/response communication. Understanding both patterns is crucial for designing effective robotic systems.

## Exercises

1. Create a publisher that sends the current time to a topic.
2. Create a subscriber that receives the time and displays it in a formatted way.
3. Create a service that takes two strings and returns their concatenation.
4. Modify the robot status example to use a custom message type instead of String.