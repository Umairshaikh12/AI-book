# Chapter 3: Simulated Sensors

## Overview

Robots rely on sensors to perceive and interact with their environment. In simulation, we need to accurately model these sensors to create effective digital twins. This chapter covers how to implement and configure various types of sensors in Gazebo, including LiDAR, IMU, cameras, and depth cameras. We'll explore configuration parameters, realistic simulation considerations, and integration with ROS 2.

## Learning Objectives

By the end of this chapter, you will be able to:
- Configure and implement LiDAR sensors in Gazebo
- Set up IMU sensors for orientation and acceleration measurements
- Implement RGB and depth cameras for visual perception
- Calibrate sensors for realistic simulation
- Integrate simulated sensors with ROS 2 topics

## LiDAR Sensors in Gazebo

LiDAR (Light Detection and Ranging) sensors are crucial for navigation and mapping in robotics. In Gazebo, LiDAR sensors can be implemented using the `ray` sensor type.

### Basic LiDAR Configuration
```xml
<sensor name="lidar_sensor" type="ray">
  <pose>0 0 0.2 0 0 0</pose>
  <visualize>true</visualize>
  <update_rate>10</update_rate>
  <ray>
    <scan>
      <horizontal>
        <samples>360</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>  <!-- -π radians -->
        <max_angle>3.14159</max_angle>    <!-- π radians -->
      </horizontal>
    </scan>
    <range>
      <min>0.1</min>
      <max>10.0</max>
      <resolution>0.01</resolution>
    </range>
  </ray>
  <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
    <ros>
      <namespace>/lidar</namespace>
      <remapping>~/out:=scan</remapping>
    </ros>
    <output_type>sensor_msgs/LaserScan</output_type>
    <frame_name>lidar_frame</frame_name>
  </plugin>
</sensor>
```

### Adding LiDAR to Your Robot Model
Let's add a LiDAR sensor to our humanoid robot:

```xml
<link name="lidar_link">
  <visual>
    <geometry>
      <cylinder radius="0.05" length="0.05"/>
    </geometry>
    <material name="black">
      <color rgba="0.1 0.1 0.1 1.0"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <cylinder radius="0.05" length="0.05"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.1"/>
    <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
  </inertial>
</link>

<joint name="lidar_joint" type="fixed">
  <parent link="head"/>
  <child link="lidar_link"/>
  <origin xyz="0.0 0.0 0.05" rpy="0 0 0"/>  <!-- Mount on top of head -->
</joint>

<sensor name="head_lidar" type="ray">
  <pose>0 0 0 0 0 0</pose>
  <visualize>false</visualize>
  <update_rate>10</update_rate>
  <ray>
    <scan>
      <horizontal>
        <samples>360</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>
        <max_angle>3.14159</max_angle>
      </horizontal>
    </scan>
    <range>
      <min>0.1</min>
      <max>10.0</max>
      <resolution>0.01</resolution>
    </range>
  </ray>
  <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
    <ros>
      <namespace>/humanoid</namespace>
      <remapping>~/out:=scan</remapping>
    </ros>
    <output_type>sensor_msgs/LaserScan</output_type>
    <frame_name>lidar_frame</frame_name>
  </plugin>
</sensor>
```

## IMU Sensors

Inertial Measurement Unit (IMU) sensors provide orientation and acceleration data. In Gazebo, IMU sensors are implemented using the `imu` sensor type.

### Basic IMU Configuration
```xml
<sensor name="imu_sensor" type="imu">
  <always_on>true</always_on>
  <update_rate>100</update_rate>
  <topic>imu/data</topic>
  <visualize>false</visualize>
  <plugin name="imu_plugin" filename="libgazebo_ros_imu_sensor.so">
    <ros>
      <namespace>/imu</namespace>
      <remapping>~/out:=data</remapping>
    </ros>
    <frame_name>imu_link</frame_name>
    <initial_orientation_as_reference>false</initial_orientation_as_reference>
  </plugin>
  <imu>
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.001</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.001</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.001</stddev>
        </noise>
      </z>
    </angular_velocity>
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.017</stddev>
        </noise>
      </z>
    </linear_acceleration>
  </imu>
</sensor>
```

### Adding IMU to Humanoid Robot
```xml
<link name="imu_link">
  <inertial>
    <mass value="0.01"/>
    <inertia ixx="0.000001" ixy="0" ixz="0" iyy="0.000001" iyz="0" izz="0.000001"/>
  </inertial>
</link>

<joint name="imu_joint" type="fixed">
  <parent link="torso"/>
  <child link="imu_link"/>
  <origin xyz="0 0 0.2" rpy="0 0 0"/>  <!-- Mount in torso -->
</joint>

<sensor name="torso_imu" type="imu">
  <pose>0 0 0 0 0 0</pose>
  <plugin name="imu_controller" filename="libgazebo_ros_imu_sensor.so">
    <ros>
      <namespace>/humanoid</namespace>
      <remapping>~/out:=imu/data</remapping>
    </ros>
    <frame_name>imu_link</frame_name>
  </plugin>
</sensor>
```

## Camera Sensors

Cameras are essential for visual perception in robotics. Gazebo supports both RGB and depth cameras.

### RGB Camera Configuration
```xml
<sensor name="camera" type="camera">
  <visualize>true</visualize>
  <update_rate>30</update_rate>
  <camera name="head">
    <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>/humanoid</namespace>
      <remapping>image_raw:=image</remapping>
      <remapping>camera_info:=camera_info</remapping>
    </ros>
    <frame_name>camera_frame</frame_name>
  </plugin>
</sensor>
```

### Depth Camera Configuration
```xml
<sensor name="depth_camera" type="depth">
  <visualize>true</visualize>
  <update_rate>30</update_rate>
  <camera name="depth_cam">
    <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>10</far>
    </clip>
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.05</stddev>
    </noise>
  </camera>
  <plugin name="depth_camera_controller" filename="libgazebo_ros_openni_kinect.so">
    <ros>
      <namespace>/humanoid</namespace>
      <remapping>image_raw:=depth/image</remapping>
      <remapping>camera_info:=depth/camera_info</remapping>
      <remapping>points:=depth/points</remapping>
    </ros>
    <frame_name>depth_camera_frame</frame_name>
    <baseline>0.2</baseline>
    <distortion_k1>0.0</distortion_k1>
    <distortion_k2>0.0</distortion_k2>
    <distortion_k3>0.0</distortion_k3>
    <distortion_t1>0.0</distortion_t1>
    <distortion_t2>0.0</distortion_t2>
  </plugin>
</sensor>
```

### Adding Cameras to Humanoid Robot
```xml
<link name="camera_link">
  <visual>
    <geometry>
      <box size="0.05 0.05 0.02"/>
    </geometry>
    <material name="black">
      <color rgba="0.1 0.1 0.1 1.0"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <box size="0.05 0.05 0.02"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="0.01"/>
    <inertia ixx="0.000001" ixy="0" ixz="0" iyy="0.000001" iyz="0" izz="0.000001"/>
  </inertial>
</link>

<joint name="camera_joint" type="fixed">
  <parent link="head"/>
  <child link="camera_link"/>
  <origin xyz="0.05 0 0" rpy="0 0 0"/>  <!-- Mount on front of head -->
</joint>

<sensor name="head_camera" type="camera">
  <pose>0 0 0 0 0 0</pose>
  <visualize>true</visualize>
  <update_rate>30</update_rate>
  <camera name="front_camera">
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace>/humanoid</namespace>
      <remapping>image_raw:=camera/image_raw</remapping>
      <remapping>camera_info:=camera/camera_info</remapping>
    </ros>
    <frame_name>camera_link</frame_name>
  </plugin>
</sensor>
```

## Sensor Integration with ROS 2

Sensors in Gazebo are typically integrated with ROS 2 using plugins that publish data to ROS topics. Here's an example of how to work with sensor data in ROS 2:

### LiDAR Data Subscriber
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math


class LidarProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')
        
        # Subscribe to LiDAR data
        self.lidar_subscription = self.create_subscription(
            LaserScan,
            '/humanoid/scan',
            self.lidar_callback,
            10
        )
        
        self.lidar_subscription  # prevent unused variable warning
        
        # Timer for processing data
        self.timer = self.create_timer(0.1, self.process_data)
        
        self.latest_scan = None

    def lidar_callback(self, msg):
        """Process incoming LiDAR data"""
        self.latest_scan = msg
        self.get_logger().info(f'Received scan with {len(msg.ranges)} points')

    def process_data(self):
        """Process the latest scan data"""
        if self.latest_scan is None:
            return
            
        # Example: find the closest obstacle
        min_distance = min(
            dist for dist in self.latest_scan.ranges 
            if not math.isinf(dist) and not math.isnan(dist)
        )
        
        self.get_logger().info(f'Closest obstacle: {min_distance:.2f}m')

        # Example: detect obstacles within 1 meter
        obstacle_angles = []
        for i, dist in enumerate(self.latest_scan.ranges):
            if not math.isinf(dist) and not math.isnan(dist) and dist < 1.0:
                angle = self.latest_scan.angle_min + i * self.latest_scan.angle_increment
                obstacle_angles.append(angle)
        
        if obstacle_angles:
            avg_angle = sum(obstacle_angles) / len(obstacle_angles)
            self.get_logger().info(f'Obstacles detected at average angle: {avg_angle:.2f} radians')


def main(args=None):
    rclpy.init(args=args)
    lidar_processor = LidarProcessor()
    
    try:
        rclpy.spin(lidar_processor)
    except KeyboardInterrupt:
        pass
    
    lidar_processor.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### IMU Data Subscriber
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3
from tf2_ros import TransformBroadcaster
import math


class ImuProcessor(Node):
    def __init__(self):
        super().__init__('imu_processor')
        
        # Subscribe to IMU data
        self.imu_subscription = self.create_subscription(
            Imu,
            '/humanoid/imu/data',
            self.imu_callback,
            10
        )
        
        self.imu_subscription  # prevent unused variable warning
        
        # Timer for processing data
        self.timer = self.create_timer(0.1, self.process_data)
        
        self.latest_imu = None

    def imu_callback(self, msg):
        """Process incoming IMU data"""
        self.latest_imu = msg

    def process_data(self):
        """Process the latest IMU data"""
        if self.latest_imu is None:
            return
            
        # Extract orientation (quaternion)
        orientation = self.latest_imu.orientation
        w, x, y, z = orientation.w, orientation.x, orientation.y, orientation.z
        
        # Convert to Euler angles (roll, pitch, yaw)
        roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        pitch = math.asin(2 * (w * y - z * x))
        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        
        self.get_logger().info(f'Orientation - Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}')

        # Extract angular velocity
        angular_velocity = self.latest_imu.angular_velocity
        self.get_logger().info(f'Angular velocity: ({angular_velocity.x:.2f}, {angular_velocity.y:.2f}, {angular_velocity.z:.2f})')

        # Extract linear acceleration
        linear_acceleration = self.latest_imu.linear_acceleration
        self.get_logger().info(f'Linear acceleration: ({linear_acceleration.x:.2f}, {linear_acceleration.y:.2f}, {linear_acceleration.z:.2f})')


def main(args=None):
    rclpy.init(args=args)
    imu_processor = ImuProcessor()
    
    try:
        rclpy.spin(imu_processor)
    except KeyboardInterrupt:
        pass
    
    imu_processor.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Sensor Calibration and Realistic Simulation

### Noise Modeling
Real sensors have noise characteristics that should be modeled in simulation:

```xml
<sensor name="noisy_lidar" type="ray">
  <ray>
    <!-- ... other config ... -->
    <noise>
      <type>gaussian</type>
      <mean>0.0</mean>
      <stddev>0.01</stddev>  <!-- 1cm standard deviation -->
    </noise>
  </ray>
  <!-- ... -->
</sensor>
```

### Sensor Accuracy Considerations
- Model sensor resolution limitations
- Include sensor range limitations
- Add appropriate noise models
- Consider environmental factors (dust, rain for LiDAR, etc.)

## Troubleshooting Common Sensor Issues

1. **No Data Publication**: Check that sensor plugins are correctly specified and loaded
2. **Incorrect Frame IDs**: Ensure TF frames are properly set up
3. **Performance Issues**: Reduce update rates or resolution if necessary
4. **Calibration Problems**: Verify sensor mounting position and orientation
5. **Noise Levels**: Adjust noise parameters to match real sensor characteristics

## Best Practices for Sensor Implementation

1. **Proper Frame Conventions**: Use appropriate coordinate frames (typically right-handed)
2. **Realistic Parameters**: Match sensor parameters to real hardware when possible
3. **Performance Optimization**: Balance accuracy with simulation performance
4. **Consistent Naming**: Use consistent naming conventions for sensor topics
5. **Modular Design**: Create reusable sensor definitions that can be easily added to different robots
6. **Documentation**: Comment sensor configurations to explain parameters

## Summary

Simulated sensors are crucial for creating effective digital twins and testing robot perception systems. This chapter covered how to implement LiDAR, IMU, and camera sensors in Gazebo and integrate them with ROS 2. Properly simulated sensors enable effective testing of perception, navigation, and control algorithms in a safe virtual environment.

## Exercises

1. Add a LiDAR sensor to your humanoid robot model and configure it for navigation.
2. Implement an IMU sensor for balance and orientation sensing.
3. Create a depth camera for object recognition and manipulation tasks.
4. Write a ROS 2 node that processes sensor data to detect obstacles.
5. Model sensor noise characteristics based on real sensor specifications.