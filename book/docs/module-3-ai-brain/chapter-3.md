# Chapter 3: Nav2 for Humanoid Navigation

## Overview

Navigation is a critical capability for humanoid robots to operate autonomously in human environments. The Navigation2 (Nav2) stack is the primary navigation framework for ROS 2, providing the tools and algorithms necessary for robots to navigate through complex environments. This chapter focuses on configuring and using Nav2 specifically for humanoid robots, addressing their unique navigation challenges.

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the architecture and components of the Nav2 stack
- Configure Nav2 for humanoid robot navigation
- Implement custom controllers and planners for bipedal locomotion
- Handle navigation challenges specific to humanoid robots
- Create navigation behaviors tailored for human environments

## Introduction to Nav2

Navigation2 (Nav2) is the navigation stack for ROS 2, providing a complete framework for autonomous robot navigation. It includes:

- **Global Planner**: Creates a path from start to goal
- **Local Planner**: Controls the robot along the path while avoiding obstacles
- **Controller**: Translates plan into low-level commands
- **Recovery Behaviors**: Handles situations where navigation fails
- **Behavior Trees**: Orchestrates navigation tasks

### Nav2 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Navigation    │    │   Behavior      │    │   Action        │
│   Server        │    │   Tree          │    │   Clients       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Navigation Stack                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ Global      │    │ Local       │    │ Sensors &           │  │
│  │ Planner     │    │ Planner     │    │ Actuators           │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Nav2 Components

### Global Planner
The global planner generates a path from the robot's current location to the goal. Common implementations include:
- NavFn (Potential Fields)
- Global Costmap
- A* and Dijkstra algorithms

### Local Planner
The local planner is responsible for:
- Following the global plan
- Avoiding obstacles in real-time
- Handling dynamic obstacles
- Adapting to terrain changes

Common local planners include:
- DWA (Dynamic Window Approach)
- TEB (Timed Elastic Band)
- MPC (Model Predictive Control)

### Controllers
Controllers translate plan points into velocity commands for the robot:
- Pure Pursuit
- PID controllers
- Model-based controllers

## Nav2 Configuration for Humanoid Robots

Humanoid robots present unique navigation challenges:

### Bipedal Locomotion
- Balance constraints during movement
- Limited step size and direction
- Dynamic stability requirements
- Different speed characteristics

### Environmental Considerations
- Doorway and furniture heights
- Stair navigation requirements
- Human-robot interaction spaces

### Configuration Files
Nav2 configuration is handled through YAML files:

```yaml
# behavior_tree.xml - Defines the navigation behavior
bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    default_bt_xml_filename: "path/to/navigate_to_pose_w_replanning_and_recovery.xml"
    plugin_lib_names:
      - nav2_compute_path_to_pose_action_bt_node
      - nav2_follow_path_action_bt_node
      - nav2_back_up_action_bt_node
      - nav2_spin_action_bt_node
      - nav2_wait_action_bt_node
      - nav2_clear_costmap_service_bt_node
      - nav2_is_stuck_condition_bt_node
      - nav2_goal_reached_condition_bt_node
      - nav2_goal_updated_condition_bt_node
      - nav2_initial_pose_received_condition_bt_node
      - nav2_reinitialize_global_localization_service_bt_node
      - nav2_rate_controller_bt_node
      - nav2_distance_controller_bt_node
      - nav2_speed_controller_bt_node
      - nav2_truncate_path_action_bt_node
      - nav2_goal_updater_node_bt_node
      - nav2_recovery_node_bt_node
      - nav2_pipeline_sequence_bt_node
      - nav2_round_robin_node_bt_node
      - nav2_transform_available_condition_bt_node
      - nav2_time_expired_condition_bt_node
      - nav2_path_expiring_timer_condition
      - nav2_distance_traveled_condition_bt_node
      - nav2_single_trigger_bt_node
      - nav2_is_battery_low_condition_bt_node
      - nav2_navigate_through_poses_action_bt_node
      - nav2_navigate_to_pose_action_bt_node
      - nav2_remove_passed_goals_action_bt_node
      - nav2_planner_selector_bt_node
      - nav2_controller_selector_bt_node
      - nav2_goal_checker_selector_bt_node
      - nav2_controller_cancel_bt_node
      - nav2_path_longer_on_approach_bt_node
      - nav2_wait_cancel_bt_node
```

### Costmap Configuration for Humanoids
```yaml
# costmap_2d.yaml
global_costmap:
  global_frame: map
  robot_base_frame: base_link
  update_frequency: 1.0
  publish_frequency: 1.0
  static_map: true
  rolling_window: false
  resolution: 0.05  # Higher resolution for precise navigation
  inflation_radius: 0.5  # Adjust based on humanoid size
  plugins:
    - {name: static_layer, type: "nav2_costmap_2d::StaticLayer"}
    - {name: obstacle_layer, type: "nav2_costmap_2d::ObstacleLayer"}
    - {name: inflation_layer, type: "nav2_costmap_2d::InflationLayer"}

local_costmap:
  global_frame: odom
  robot_base_frame: base_link
  update_frequency: 5.0
  publish_frequency: 2.0
  static_map: false
  rolling_window: true
  width: 4  # Adjust for humanoid perception range
  height: 4
  resolution: 0.05
  inflation_radius: 0.5
  plugins:
    - {name: obstacle_layer, type: "nav2_costmap_2d::ObstacleLayer"}
    - {name: voxel_layer, type: "nav2_costmap_2d::VoxelLayer"}
    - {name: inflation_layer, type: "nav2_costmap_2d::InflationLayer"}
```

## Implementing Humanoid-Specific Navigation

### Custom Controller for Bipedal Motion
For humanoid robots, we may need custom controllers that account for bipedal locomotion:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav2_core.controller import Controller
from nav2_util import lifecycle
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path
import math
import numpy as np


class HumanoidController(Controller):
    """
    Custom controller for humanoid robot navigation
    Takes into account balance and step constraints
    """
    
    def __init__(self, name):
        super().__init__(name)
        self.linear_speed = 0.3  # m/s - conservative for balance
        self.angular_speed = 0.5  # rad/s
        self.step_size = 0.2  # Max step size in meters
        self.balance_threshold = 0.1  # Balance deviation threshold

    def configure(self, tf_buffer, costmap_ros, local_planner):
        """Configure the controller with necessary components"""
        self.costmap_ros = costmap_ros
        self.local_planner = local_planner
        self.tf_buffer = tf_buffer
        self.logger = self.get_logger()
        self.logger.info(f"{self.get_name()} controller configured")

    def cleanup(self):
        """Clean up resources"""
        pass

    def activate(self):
        """Activate the controller"""
        self.logger.info(f"{self.get_name()} controller activated")
        
    def deactivate(self):
        """Deactivate the controller"""
        self.logger.info(f"{self.get_name()} controller deactivated")

    def setPlan(self, path: Path):
        """Set the plan to follow"""
        self.path = path
        self.current_waypoint = 0
        self.logger.info(f"Set plan with {len(path.poses)} waypoints")

    def computeVelocityCommands(self, pose: PoseStamped, velocity: Twist) -> Twist:
        """Compute velocity commands to follow the path"""
        
        # Get current path
        if not hasattr(self, 'path') or len(self.path.poses) == 0:
            cmd_vel = Twist()
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0
            return cmd_vel

        # Find closest waypoint
        current_pos = np.array([pose.pose.position.x, pose.pose.position.y])
        min_dist = float('inf')
        closest_idx = self.current_waypoint

        for i in range(self.current_waypoint, min(self.current_waypoint + 10, len(self.path.poses))):
            wp_pos = np.array([self.path.poses[i].pose.position.x, 
                              self.path.poses[i].pose.position.y])
            dist = np.linalg.norm(current_pos - wp_pos)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        # Update current waypoint if we're close enough
        if min_dist < 0.2:  # 20 cm threshold
            self.current_waypoint = min(closest_idx + 1, len(self.path.poses) - 1)

        # Get target waypoint (lookahead point)
        target_idx = min(self.current_waypoint + 2, len(self.path.poses) - 1)
        target_pos = np.array([self.path.poses[target_idx].pose.position.x,
                              self.path.poses[target_idx].pose.position.y])

        # Calculate desired direction
        direction = target_pos - current_pos
        distance = np.linalg.norm(direction)
        
        if distance < 0.1:  # Very close to target
            cmd_vel = Twist()
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0
            return cmd_vel

        # Normalize direction
        direction = direction / distance

        # Calculate robot's orientation
        q = pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        # Calculate angle to target
        target_angle = math.atan2(direction[1], direction[0])
        angle_diff = target_angle - yaw

        # Normalize angle
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        # Create velocity command respecting humanoid constraints
        cmd_vel = Twist()
        
        # Limit angular speed for balance
        angular_speed = max(-self.angular_speed, min(self.angular_speed, angle_diff * 1.0))
        
        # Only move forward if roughly aligned with target direction
        if abs(angle_diff) < 0.3:  # About 17 degrees
            cmd_vel.linear.x = min(self.linear_speed, distance * 0.8)
        else:
            cmd_vel.linear.x = 0.0  # Don't move forward when turning significantly

        cmd_vel.angular.z = angular_speed

        # Apply humanoid-specific constraints
        cmd_vel.linear.x = max(-self.linear_speed, min(self.linear_speed, cmd_vel.linear.x))
        cmd_vel.angular.z = max(-self.angular_speed, min(self.angular_speed, cmd_vel.angular.z))

        # Step size constraint (simplified)
        if cmd_vel.linear.x > 0:
            cmd_vel.linear.x = min(cmd_vel.linear.x, self.step_size * 5)  # 5 steps per second max

        return cmd_vel


def main(args=None):
    rclpy.init(args=args)
    
    # This would normally be loaded as a plugin by Nav2
    # For demonstration only
    controller = HumanoidController("HumanoidController")
    
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    
    controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Humanoid-Specific Navigation Parameters
```yaml
# controller_server.yaml
controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 5.0  # Lower frequency for more stable humanoid movement
    min_x_velocity_threshold: 0.05
    min_y_velocity_threshold: 0.05
    min_theta_velocity_threshold: 0.05
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["FollowPath"]

    # Humanoid-specific controller
    FollowPath:
      plugin: "nav2_mppi_controller::MppiController"  # Or custom controller
      time_steps: 25
      control_horizon: 3
      trajectory_horizon: 6.0
      discretization: 0.2
      reference_trajectory_generator: "nav_2d_utils::SimplePathTrajectory"
      kino_dynamic_model: "nav2_mppi_controller::KinoModel"
      optimization_method: "csqp"
      csqp_termination_criteria: 0.0001
      csqp_penalty_initial: 10.0
      csqp_penalty_multiplier: 2.0
      control_cost_weight: 0.1
      goal_cost_weight: 3.0
      path_cost_weight: 2.0
      goal_tolerance: 0.2  # Adjust for humanoid precision
      xy_goal_tolerance: 0.3
      stateful_cost_function: "nav2_mppi_controller::PathFollowing"
      collision_cost_weight: 10.0
      collision_threshold: 0.25
      heading_scale: 1.0
      oscillation_non_oriented_path_angle_threshold: 0.3
      oscillation_non_oriented_goal_angle_threshold: 0.2

progress_checker:
  ros__parameters:
    use_sim_time: True
    plugin: "nav2_controller::SimpleProgressChecker"
    required_movement_radius: 0.5  # Adjust for humanoid movement characteristics
    movement_time_allowance: 10.0

goal_checker:
  ros__parameters:
    use_sim_time: True
    plugin: "nav2_controller::SimpleGoalChecker"
    xy_goal_tolerance: 0.3  # Humanoid-specific tolerance
    yaw_goal_tolerance: 0.1
    stateful: True
```

## Launching Nav2 for Humanoid Robots

### Example Launch File
```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import ReplaceString
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get the package share directory
    pkg_share = get_package_share_directory('humanoid_navigation')
    
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')
    bt_xml_file = LaunchConfiguration('bt_xml_file')
    map_sub = LaunchConfiguration('map_subscribe_transient_local')

    # Create launch description
    ld = LaunchDescription()

    # Declare launch arguments
    ld.add_action(
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use simulation time if true'))
    
    ld.add_action(
        DeclareLaunchArgument(
            'autostart', 
            default_value='True',
            description='Automatically startup the nav2 stack'))

    ld.add_action(
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_share, 'config/nav2_params.yaml'),
            description='Full path to the ROS2 parameters file to use for all launched nodes'))

    ld.add_action(
        DeclareLaunchArgument(
            'bt_xml_file',
            default_value=os.path.join(pkg_share, 'behavior_trees/navigate_w_replanning_and_recovery.xml'),
            description='Full path to the behavior tree xml file to use'))

    ld.add_action(
        DeclareLaunchArgument(
            'map_subscribe_transient_local',
            default_value='False',
            description='Whether to set the map subscriber to transient local'))

    # Map server
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        parameters=[params_file],
        remappings=[('topic', 'map'),
                    ('map_topic', 'map'),
                    ('map_service', 'map_server/load_map'),
                    ('map_subscribe_transient_local', map_sub)],
        output='screen')

    # Lifecycle manager for map server
    lifecycle_manager_map = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        parameters=[{'use_sim_time': use_sim_time},
                    {'autostart': autostart},
                    {'node_names': ['map_server']}],
        output='screen')

    # Planner server
    planner_server_node = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        parameters=[params_file],
        remappings=[('model_path', '/goal_pose'),
                    ('plan', 'plan'),
                    ('costmap', 'global_costmap/costmap_raw'),
                    (' footprint', 'global_costmap/published_footprint')],
        output='screen')

    # Controller server
    controller_server_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        parameters=[params_file],
        remappings=[('cmd_vel', 'cmd_vel'),
                    ('odom', 'odom'),
                    ('global_plan', 'received_global_plan'),
                    ('local_plan', 'local_plan'),
                    ('feedback', 'controller_feedback'),
                    ('x', 'current_x'),
                    ('y', 'current_y'),
                    ('theta', 'current_theta')],
        output='screen')

    # Behavior tree navigator
    bt_navigator_node = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        parameters=[params_file, 
                    {'default_bt_xml_filename': bt_xml_file}],
        remappings=[('goal_pose', 'goal_pose'),
                    ('navigate_to_pose', 'navigate_to_pose'),
                    ('received_global_plan', 'received_global_plan'),
                    ('received_cost_map', 'received_cost_map'),
                    ('received_local_plan', 'received_local_plan'),
                    ('received_footprint', 'received_footprint'),
                    ('feedback', 'navigation_feedback'),
                    ('result', 'navigation_result'),
                    ('status', 'navigation_status')],
        output='screen')

    # Waypoint follower
    waypoint_follower_node = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        parameters=[params_file],
        remappings=[('navigate_to_pose', 'navigate_to_pose'),
                    ('navigate_through_poses', 'navigate_through_poses')],
        output='screen')

    # Recovery server
    recovery_server_node = Node(
        package='nav2_recoveries',
        executable='recoveries_server',
        name='recoveries_server',
        parameters=[params_file],
        output='screen')

    # Lifecycle manager for navigation
    lifecycle_manager_nav = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        parameters=[{'use_sim_time': use_sim_time},
                    {'autostart': autostart},
                    {'node_names': ['planner_server',
                                    'controller_server',
                                    'bt_navigator',
                                    'waypoint_follower',
                                    'recoveries_server']}],
        output='screen')

    # Add nodes to launch description
    ld.add_action(lifecycle_manager_map)
    ld.add_action(map_server_node)
    ld.add_action(lifecycle_manager_nav)
    ld.add_action(planner_server_node)
    ld.add_action(controller_server_node)
    ld.add_action(bt_navigator_node)
    ld.add_action(waypoint_follower_node)
    ld.add_action(recovery_server_node)

    return ld
```

## Humanoid Navigation Challenges and Solutions

### Balance and Stability
Humanoid robots require special consideration for balance during navigation:

1. **Center of Mass Management**: Keep CoM within support polygon
2. **Step Planning**: Plan footsteps to maintain stability
3. **Gait Adaptation**: Adjust walking pattern based on terrain

### Stair and Step Navigation
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, PointCloud2
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import String
from vision_msgs.msg import Detection2DArray
import numpy as np
import math


class StairNavigationNode(Node):
    """
    Handles navigation challenges specific to stairs and steps
    """
    
    def __init__(self):
        super().__init__('stair_navigation_node')
        
        # Perception inputs
        self.depth_sub = self.create_subscription(
            Image,
            '/depth_camera/depth/image_rect_raw',
            self.depth_callback,
            10
        )
        
        self.pointcloud_sub = self.create_subscription(
            PointCloud2,
            '/pointcloud',
            self.pointcloud_callback,
            10
        )
        
        # Navigation control
        self.nav_status_sub = self.create_subscription(
            String,
            '/navigation_status',
            self.nav_status_callback,
            10
        )
        
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.stair_status_pub = self.create_publisher(String, '/stair_status', 10)
        
        # State management
        self.is_approaching_stairs = False
        self.stair_height = 0.0
        self.stair_depth = 0.0
        self.current_step = 0

    def depth_callback(self, msg):
        """Process depth image to detect stairs/steps"""
        # Convert ROS image to OpenCV
        from cv_bridge import CvBridge
        bridge = CvBridge()
        depth_image = bridge.imgmsg_to_cv2(msg, desired_encoding='32fc1')
        
        # Simple approach to detect height changes
        # In a real implementation, this would use more sophisticated algorithms
        height_threshold = 0.15  # Minimum height to consider a step
        
        # Analyze central region of image
        height, width = depth_image.shape
        center_region = depth_image[height//2:, width//4:3*width//4]
        
        # Find regions with significant height changes
        height_changes = np.gradient(center_region, axis=0)
        step_candidates = np.where(np.abs(height_changes) > height_threshold)
        
        if len(step_candidates[0]) > 0:
            self.get_logger().info("Step/stair detected")
            self.is_approaching_stairs = True
        else:
            self.is_approaching_stairs = False

    def pointcloud_callback(self, msg):
        """Process point cloud for detailed step analysis"""
        # For this example, we'll just indicate that we received data
        # In a real implementation, this would process the point cloud
        # to determine exact step geometry and plan footsteps
        pass

    def nav_status_callback(self, msg):
        """Handle navigation status updates"""
        if self.is_approaching_stairs and "approaching_obstacle" in msg.data:
            # Switch to stair climbing mode
            self.handle_stair_navigation()

    def handle_stair_navigation(self):
        """Handle navigation when stairs are detected"""
        cmd_vel = Twist()
        
        if self.is_approaching_stairs:
            # Slow down approach
            cmd_vel.linear.x = 0.1  # Very slow approach
            cmd_vel.angular.z = 0.0
            
            self.get_logger().info("Approaching stairs, reducing speed")
            self.stair_status_pub.publish(String(data="approaching_stairs"))
        else:
            cmd_vel.linear.x = 0.0
            cmd_vel.angular.z = 0.0
            self.stair_status_pub.publish(String(data="clear_path"))
        
        self.cmd_vel_pub.publish(cmd_vel)

def main(args=None):
    rclpy.init(args=args)
    stair_node = StairNavigationNode()
    
    try:
        rclpy.spin(stair_node)
    except KeyboardInterrupt:
        pass
    
    stair_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Navigation Recovery Behaviors for Humanoids

Humanoid robots need specialized recovery behaviors:

### Humanoid-Specific Recovery
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import time


class HumanoidRecoveryNode(Node):
    """
    Implements recovery behaviors specific to humanoid robots
    """
    
    def __init__(self):
        super().__init__('humanoid_recovery_node')
        
        # Publishers and subscribers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/recovery_status', 10)
        self.recovery_sub = self.create_subscription(
            String,
            '/recovery_trigger',
            self.recovery_callback,
            10
        )
        
        self.active_recovery = False
        self.recovery_type = ""

    def recovery_callback(self, msg):
        """Trigger appropriate recovery behavior"""
        if self.active_recovery:
            return  # Already in recovery
            
        self.recovery_type = msg.data
        self.active_recovery = True
        self.get_logger().info(f"Starting recovery: {self.recovery_type}")
        
        if self.recovery_type == "humanoid_spin":
            self.humanoid_spin_recovery()
        elif self.recovery_type == "humanoid_wait":
            self.humanoid_wait_recovery()
        elif self.recovery_type == "humanoid_backup":
            self.humanoid_backup_recovery()
        else:
            self.get_logger().warn(f"Unknown recovery type: {self.recovery_type}")
        
        self.active_recovery = False
        self.status_pub.publish(String(data="recovery_complete"))

    def humanoid_spin_recovery(self):
        """Gentle spinning motion to clear obstacle"""
        self.status_pub.publish(String(data="spin_recovery_started"))
        
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.0
        cmd_vel.angular.z = 0.2  # Gentle rotation
        
        start_time = time.time()
        while time.time() - start_time < 5.0:  # 5 seconds spin
            if not self.active_recovery:
                break
            self.cmd_vel_pub.publish(cmd_vel)
            time.sleep(0.1)
        
        cmd_vel.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd_vel)

    def humanoid_wait_recovery(self):
        """Wait and reassess situation"""
        self.status_pub.publish(String(data="wait_recovery_started"))
        
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.0
        cmd_vel.angular.z = 0.0
        
        self.cmd_vel_pub.publish(cmd_vel)
        time.sleep(3.0)  # Wait 3 seconds

    def humanoid_backup_recovery(self):
        """Careful backward movement"""
        self.status_pub.publish(String(data="backup_recovery_started"))
        
        cmd_vel = Twist()
        cmd_vel.linear.x = -0.1  # Slow backward movement
        cmd_vel.angular.z = 0.0
        
        start_time = time.time()
        while time.time() - start_time < 2.0:  # 2 seconds backup
            if not self.active_recovery:
                break
            self.cmd_vel_pub.publish(cmd_vel)
            time.sleep(0.1)
        
        cmd_vel.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd_vel)

def main(args=None):
    rclpy.init(args=args)
    recovery_node = HumanoidRecoveryNode()
    
    try:
        rclpy.spin(recovery_node)
    except KeyboardInterrupt:
        pass
    
    recovery_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Testing and Validation

### Navigation Performance Metrics
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path, Odometry
from std_msgs.msg import Float64
import math
import time


class NavigationMetricsNode(Node):
    """
    Calculates navigation performance metrics for humanoid robots
    """
    
    def __init__(self):
        super().__init__('navigation_metrics_node')
        
        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        
        self.goal_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )
        
        self.path_sub = self.create_subscription(
            Path,
            '/plan',
            self.path_callback,
            10
        )
        
        # Publishers for metrics
        self.path_efficiency_pub = self.create_publisher(Float64, '/path_efficiency', 10)
        self.navigation_time_pub = self.create_publisher(Float64, '/navigation_time', 10)
        
        # Internal state
        self.start_time = None
        self.start_pos = None
        self.current_pos = None
        self.goal_pos = None
        self.path_length = 0.0
        self.traveled_distance = 0.0
        self.previous_pos = None

    def odom_callback(self, msg):
        """Track robot position and calculate metrics"""
        if self.start_time is None:
            self.start_time = time.time()
            self.start_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
            
        self.current_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
        
        # Calculate distance traveled
        if self.previous_pos is not None:
            step_distance = math.sqrt(
                (self.current_pos[0] - self.previous_pos[0])**2 + 
                (self.current_pos[1] - self.previous_pos[1])**2
            )
            self.traveled_distance += step_distance
        
        self.previous_pos = self.current_pos
        
        # Calculate and publish metrics if goal is set
        if self.goal_pos is not None:
            # Calculate distance to goal
            dist_to_goal = math.sqrt(
                (self.current_pos[0] - self.goal_pos[0])**2 + 
                (self.current_pos[1] - self.goal_pos[1])**2
            )
            
            # Calculate path efficiency
            if self.path_length > 0:
                efficiency = self.path_length / max(self.traveled_distance, 0.001)
                self.path_efficiency_pub.publish(Float64(data=efficiency))
            
            # Calculate navigation time
            nav_time = time.time() - self.start_time
            self.navigation_time_pub.publish(Float64(data=nav_time))
    
    def goal_callback(self, msg):
        """Record goal position"""
        self.goal_pos = (msg.pose.position.x, msg.pose.position.y)
    
    def path_callback(self, msg):
        """Calculate planned path length"""
        self.path_length = 0.0
        
        if len(msg.poses) > 1:
            for i in range(1, len(msg.poses)):
                p1 = msg.poses[i-1].pose.position
                p2 = msg.poses[i].pose.position
                dist = math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
                self.path_length += dist


def main(args=None):
    rclpy.init(args=args)
    metrics_node = NavigationMetricsNode()
    
    try:
        rclpy.spin(metrics_node)
    except KeyboardInterrupt:
        pass
    
    metrics_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Best Practices for Humanoid Navigation

### Configuration Best Practices
1. **Conservative Parameters**: Use lower speeds and accelerations for stability
2. **Higher Resolution Maps**: Use finer grid resolution for precise navigation
3. **Extended Inflation**: Inflate obstacles more to account for humanoid size
4. **Regular Calibration**: Ensure sensors are properly calibrated

### Performance Optimization
1. **Tune for Balance**: Adjust parameters to maintain humanoid balance
2. **Consider Gait**: Account for walking pattern in navigation planning
3. **Validate in Simulation**: Test extensively in simulation before real deployment
4. **Gradual Complexity**: Start with simple navigation tasks and increase complexity

## Troubleshooting Common Issues

### Navigation Fails Frequently
- Check if costmap parameters are appropriate for humanoid size
- Verify sensor data quality and frequency
- Ensure proper transformations between coordinate frames
- Validate that the robot model matches the physical robot

### Robot Oscillates During Navigation
- Reduce PID controller gains
- Increase goal tolerances
- Check sensor noise levels
- Ensure proper localization

### Robot Cannot Navigate Through Narrow Spaces
- Adjust robot footprint in configuration
- Modify local planner to handle narrow spaces better
- Check inflation parameters in costmaps
- Consider using a different path planner

## Summary

Nav2 provides a comprehensive framework for humanoid navigation, but requires specialized configuration to account for the unique characteristics of bipedal robots. By understanding the architecture of Nav2 and adapting its components to humanoid-specific requirements, we can create robust navigation systems that enable humanoid robots to operate effectively in human environments.

## Exercises

1. Configure Nav2 for a specific humanoid robot model using the appropriate parameters.
2. Implement a custom controller plugin that accounts for humanoid balance constraints.
3. Create a navigation system that can handle stairs and steps appropriately.
4. Implement recovery behaviors specialized for humanoid robots.
5. Design and test a navigation system for a humanoid robot in an indoor environment with furniture and people.