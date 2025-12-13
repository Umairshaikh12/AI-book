# Chapter 2: Environment Building

## Overview

Creating realistic environments is crucial for effective robot testing and validation. This chapter covers how to design and build custom environments in Gazebo for testing humanoid robots. We'll explore world file creation, lighting and material configuration, dynamic obstacles, and how to make environments that closely match real-world scenarios.

## Learning Objectives

By the end of this chapter, you will be able to:
- Create custom world files for Gazebo
- Configure lighting and materials for realistic environments
- Add static and dynamic obstacles for robot testing
- Build indoor and outdoor environments appropriate for humanoid robots
- Use Gazebo's built-in models and create custom ones

## Gazebo World File Structure

Gazebo world files are written in SDF (Simulation Description Format) and define the complete simulation environment:

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="my_world">
    <!-- Includes for standard models -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Custom models and objects -->
    <model name="robot_1">
      <!-- Model definition -->
    </model>
    
    <!-- Environment settings -->
    <physics type="ode">
      <!-- Physics configuration -->
    </physics>
    
    <scene>
      <!-- Scene effects -->
    </scene>
    
    <audio>
      <!-- Audio settings -->
    </audio>
    
    <wind>
      <!-- Wind effects -->
    </wind>
  </world>
</sdf>
```

## Creating Custom Models

Custom models are typically stored in the `~/.gazebo/models/` directory or in your ROS packages. Each model requires a specific structure:

```
.model_name/
├── model.config
├── model.sdf
└── meshes/
    └── *.dae, *.stl, *.obj
└── materials/
    └── textures/
        └── *.png, *.jpg
```

### model.config Example
```xml
<?xml version="1.0"?>
<model>
  <name>my_object</name>
  <version>1.0</version>
  <sdf version="1.7">model.sdf</sdf>
  <author>
    <name>Your Name</name>
    <email>your.email@example.com</email>
  </author>
  <description>A custom model for simulation</description>
</model>
```

### Basic Model Definition
```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <model name="my_object">
    <link name="link">
      <pose>0 0 0 0 0 0</pose>
      <inertial>
        <mass>1.0</mass>
        <inertia>
          <ixx>0.1</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.1</iyy>
          <iyz>0</iyz>
          <izz>0.1</izz>
        </inertia>
      </inertial>
      
      <collision name="collision">
        <geometry>
          <box>
            <size>1 1 1</size>
          </box>
        </geometry>
      </collision>
      
      <visual name="visual">
        <geometry>
          <box>
            <size>1 1 1</size>
          </box>
        </geometry>
        <material>
          <ambient>0.5 0.5 0.5 1</ambient>
          <diffuse>0.7 0.7 0.7 1</diffuse>
          <specular>0.1 0.1 0.1 1</specular>
        </material>
      </visual>
    </link>
  </model>
</sdf>
```

## Building Indoor Environments

Indoor environments require careful attention to space layout, furniture, and potential obstacles:

### Room with Furniture
```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="indoor_room">
    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <!-- Lighting -->
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Walls -->
    <model name="wall_1">
      <pose>0 5 1 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>10 0.2 2</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.1 0.1 0.1 1</specular>
          </material>
        </visual>
      </link>
    </model>
    
    <!-- Furniture (table) -->
    <model name="table">
      <pose>-2 0 0.5 0 0 0</pose>
      <link name="top">
        <collision name="collision">
          <geometry>
            <box>
              <size>1.5 0.8 0.05</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1.5 0.8 0.05</size>
            </box>
          </geometry>
          <material>
            <ambient>0.6 0.4 0.2 1</ambient>
            <diffuse>0.6 0.4 0.2 1</diffuse>
            <specular>0.2 0.2 0.2 1</specular>
          </material>
        </visual>
      </link>
      
      <link name="leg_1">
        <pose>-0.6 -0.35 0.25 0 0 0</pose>
        <collision name="collision">
          <geometry>
            <box>
              <size>0.1 0.1 0.5</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.1 0.1 0.5</size>
            </box>
          </geometry>
          <material>
            <ambient>0.6 0.4 0.2 1</ambient>
            <diffuse>0.6 0.4 0.2 1</diffuse>
          </material>
        </visual>
      </link>
      
      <!-- Additional legs -->
    </model>
    
    <!-- Navigation goal -->
    <model name="goal">
      <pose>3 0 0.25 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.2</radius>
              <length>0.5</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0 1 0 0.5</ambient>
            <diffuse>0 1 0 0.5</diffuse>
          </material>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

## Building Outdoor Environments

Outdoor environments require different considerations like terrain, weather effects, and natural obstacles:

### Outdoor Park Environment
```xml
<sdf version="1.7">
  <world name="outdoor_park">
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- Add some terrain variation -->
    <model name="hill">
      <pose>0 0 0 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <mesh>
              <uri>file://meshes/hill.dae</uri>
            </mesh>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <mesh>
              <uri>file://meshes/hill.dae</uri>
            </mesh>
          </geometry>
        </visual>
      </link>
    </model>
    
    <!-- Trees -->
    <model name="tree_1">
      <pose>-5 3 0 0 0 0</pose>
      <!-- Tree model definition -->
    </model>
    
    <model name="tree_2">
      <pose>4 -2 0 0 0 0</pose>
      <!-- Tree model definition -->
    </model>
    
    <!-- Path markers -->
    <model name="path_marker_1">
      <pose>-3 0 0.05 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry>
            <cylinder>
              <radius>0.5</radius>
              <length>0.1</length>
            </cylinder>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.2 1</ambient>
            <diffuse>0.8 0.8 0.2 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

## Advanced Environment Features

### Lighting Configuration
```xml
<scene>
  <ambient>0.4 0.4 0.4 1</ambient>
  <background>0.7 0.7 0.7 1</background>
  <shadows>true</shadows>
</scene>

<!-- Directional light -->
<light name="directional_light" type="directional">
  <pose>0 0 10 0 0 0</pose>
  <diffuse>0.8 0.8 0.8 1</diffuse>
  <specular>0.2 0.2 0.2 1</specular>
  <attenuation>
    <range>100</range>
  </attenuation>
  <direction>-0.5 0.1 -0.9</direction>
</light>
```

### Wind Effects
```xml>
<wind>
  <linear_velocity>0.5 0 0</linear_velocity>
</wind>
```

### Dynamic Obstacles
```xml
<!-- Moving obstacle -->
<model name="moving_obstacle">
  <pose>-5 0 0.5 0 0 0</pose>
  <link name="link">
    <collision name="collision">
      <geometry>
        <sphere>
          <radius>0.3</radius>
        </sphere>
      </geometry>
    </collision>
    <visual name="visual">
      <geometry>
        <sphere>
          <radius>0.3</radius>
        </sphere>
      </geometry>
      <material>
        <ambient>1 0 0 1</ambient>
        <diffuse>1 0 0 1</diffuse>
      </material>
    </visual>
    <velocity>0.2 0 0</velocity>
  </link>
</model>
```

## Humanoid Robot Specific Considerations

When building environments for humanoid robots, consider:

### Doorways and Corridors
- Ensure doorways are wide enough for humanoid robots (typically 0.8-1.0m)
- Check ceiling height for tall robots
- Consider the robot's turning radius

### Stairs and Steps
- Model stairs with appropriate dimensions
- Consider the robot's step height capability
- Add ramps as alternatives where needed

### Interaction Points
- Place objects at heights the humanoid can reach
- Ensure tables are at appropriate height for manipulation tasks
- Include handrails for stability when needed

## Using Gazebo Tools

### GUI-based Environment Building
- Use Gazebos's built-in model editor
- Drag and drop models from the database
- Adjust lighting and environment settings through the GUI

### Programmatic Environment Generation
You can also create environments programmatically using ROS and Gazebo services:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity
import os

class EnvironmentBuilder(Node):
    def __init__(self):
        super().__init__('environment_builder')
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn service...')
        
    def spawn_model(self, model_name, model_xml, pose):
        request = SpawnEntity.Request()
        request.name = model_name
        request.xml = model_xml
        request.initial_pose = pose
        future = self.spawn_client.call_async(request)
        return future

def main(args=None):
    rclpy.init(args=args)
    builder = EnvironmentBuilder()
    
    # Example: spawn a simple box
    box_sdf = '''
    <sdf version="1.6">
      <model name="test_box">
        <pose>0 0 0.5 0 0 0</pose>
        <link name="box_link">
          <collision name="collision">
            <geometry>
              <box>
                <size>1 1 1</size>
              </box>
            </geometry>
          </collision>
          <visual name="visual">
            <geometry>
              <box>
                <size>1 1 1</size>
              </box>
            </geometry>
          </visual>
        </link>
      </model>
    </sdf>'''
    
    from geometry_msgs.msg import Pose
    pose = Pose()
    pose.position.x = 1.0
    pose.position.y = 1.0
    pose.position.z = 0.5
    
    future = builder.spawn_model("test_box", box_sdf, pose)
    
    try:
        rclpy.spin_until_future_complete(builder, future)
        if future.result() is not None:
            builder.get_logger().info('Model spawned successfully')
        else:
            builder.get_logger().error('Failed to spawn model')
    except KeyboardInterrupt:
        pass
    
    builder.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Best Practices for Environment Design

1. **Start Simple**: Begin with basic geometric shapes before adding complex meshes
2. **Realistic Scaling**: Ensure all objects are correctly scaled relative to your robot
3. **Performance Considerations**: Use simpler collision geometries when possible
4. **Documentation**: Comment your world files to explain design decisions
5. **Modular Design**: Create reusable models that can be included in multiple environments
6. **Testing Different Scenarios**: Build multiple variations of similar environments to test robustness

## Summary

Creating realistic environments is critical for effective robot testing and validation. This chapter covered how to build both indoor and outdoor environments tailored for humanoid robots, including proper configuration of physics, lighting, and obstacles. In the next chapter, we'll explore simulated sensors that enable robots to perceive their environment.

## Exercises

1. Create a world file for a simple indoor office environment with furniture and obstacles.
2. Build an outdoor environment with terrain variations and dynamic obstacles.
3. Add lighting effects to your environment to simulate different times of day.
4. Create a model of a humanoid-sized door frame and include it in your environment.
5. Design a navigation course with multiple waypoints for testing humanoid robot path planning.