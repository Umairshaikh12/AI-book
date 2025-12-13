# Module 1 Exercises

## Exercise 1: Node Creation

Create a ROS 2 node that publishes the current time to a topic called "current_time". The message should be formatted as a string in the format "YYYY-MM-DD HH:MM:SS".

### Requirements:
1. Create a publisher that publishes to the topic "current_time"
2. Publish the current time every 2 seconds
3. Format the time as "YYYY-MM-DD HH:MM:SS"
4. Print a log message each time a message is published

### Solution Outline:
- Use the `rclpy` library to create a node
- Use Python's `datetime` module to get current time
- Publish to the "current_time" topic using String messages

## Exercise 2: Publisher-Subscriber System

Create a publisher node that sends random temperature readings and a subscriber that processes these readings to detect abnormal values.

### Requirements:
1. Publisher node that publishes random temperature values between 15°C and 35°C every 1 second
2. Subscriber node that listens to temperature readings
3. The subscriber should log an alert if temperature is below 18°C or above 32°C
4. The subscriber should also calculate and publish average temperature over the last 10 readings

### Solution Outline:
- Create two separate nodes: temperature_publisher and temperature_subscriber
- Use a queue to store the last 10 temperature readings in the subscriber
- Use separate topics for temperature readings and average temperature

## Exercise 3: Service Implementation

Create a service that takes two integers and returns their greatest common divisor (GCD).

### Requirements:
1. Create a service definition file for GCD
2. Implement a service server that calculates GCD
3. Implement a service client that requests GCD calculations
4. Test the service with various number pairs

### Solution Outline:
- Define a custom service file with two integers as request and one integer as response
- Implement Euclidean algorithm for GCD calculation
- Use rclpy's service and client APIs

## Exercise 4: Parameter Handling

Create a node that uses parameters to control its behavior and can have its parameters changed during runtime.

### Requirements:
1. Create a node that publishes messages at an interval defined by a parameter
2. The parameter should default to 1 second
3. Add a parameter for message content that defaults to "Hello, ROS 2!"
4. Allow parameters to be reconfigured at runtime
5. Log whenever a parameter is changed

### Solution Outline:
- Use `declare_parameter` to define parameters
- Add a parameter callback function to handle changes
- Use the parameter values to control publishing behavior

## Exercise 5: URDF Modification

Modify the simple humanoid URDF to add a camera sensor to the head and define appropriate inertial properties.

### Requirements:
1. Add a camera link to the head of the humanoid
2. Create a joint to attach the camera to the head
3. Define visual and collision properties for the camera
4. Calculate and specify appropriate inertial properties for the camera
5. Add Gazebo-specific tags for the camera sensor

### Solution Outline:
- Add a camera link with box geometry to represent the camera
- Add a fixed joint to attach the camera to the head
- Use reasonable dimensions for a camera (e.g., 0.05x0.05x0.03 meters)
- Calculate mass and inertia based on the camera's geometry and material

## Exercise 6: Action Server

Create an action server that simulates moving a robot to a specified position (x, y coordinates).

### Requirements:
1. Define an action that takes x, y coordinates as goal
2. Implement an action server that provides feedback on progress
3. Simulate movement by updating position gradually
4. Provide feedback including percentage complete and estimated time remaining
5. Implement a client that sends goals to the action server

### Solution Outline:
- Define a custom action with x, y coordinates as goal
- Implement an action server using rclpy's action APIs
- Use a timer to simulate gradual movement
- Calculate progress and estimated time based on distance and assumed velocity