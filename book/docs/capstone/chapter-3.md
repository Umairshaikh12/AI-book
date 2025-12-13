# Chapter 3: Autonomous Navigation and Manipulation

## Overview

This chapter focuses on implementing the autonomous navigation and manipulation capabilities of our humanoid robot. We'll integrate the Robot Operating System (ROS) Navigation Stack (Nav2) for path planning and obstacle avoidance, and implement manipulation capabilities for object interaction. Both systems will be orchestrated to work with the voice command processing system created in the previous chapter.

## Learning Objectives

By the end of this chapter, you will be able to:
- Configure and use the ROS Navigation Stack (Nav2) for humanoid robots
- Implement manipulation capabilities for object interaction
- Integrate navigation and manipulation with voice command processing
- Create a complete autonomous behavior that combines mobility and manipulation
- Test and validate the integrated navigation and manipulation system

## Architecture of Navigation and Manipulation System

The navigation and manipulation system comprises several key components:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              NAVIGATION AND MANIPULATION SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐     │
│  │   NAVIGATION    │    │  PERCEPTION     │    │  MANIPULATION       │     │
│  │   SYSTEM        │    │  SYSTEM         │    │  SYSTEM             │     │
│  │                 │    │                 │    │                     │     │
│  │ • Path Planning │    │ • Object Detec- │    │ • Arm Control       │     │
│  │ • Localization  │    │   tion          │    │ • Grasp Planning    │     │
│  │ • Obstacle Avoid│    │ • Mapping       │    │ • Trajectory Gen.   │     │
│  │ • Map Managemt  │    │ • Depth Sensing │    │ • Safety Checks     │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘     │
│         │                        │                        │                │
│         └────────────────────────┼────────────────────────┘                │
│                                  │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         COORDINATION LAYER                          │   │
│  │  • Behavior Trees                                                   │   │
│  │  • Task Planning                                                    │   │
│  │  • Action Execution                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          HUMANOID ROBOT                           │   │
│  │  • Hardware Interface                                               │   │
│  │  • Motion Control                                                   │   │
│  │  • Sensor Integration                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Navigation System Implementation

### 1. Nav2 Configuration for Humanoid Robots

Nav2 requires specific configuration for humanoid robots, including different velocity limits, footprint, and safety parameters:

```yaml
# config/nav2_params.yaml
amcl:
  ros__parameters:
    use_sim_time: True
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: "base_footprint"
    beam_skip_distance: 0.5
    beam_skip_error_threshold: 0.9
    beam_skip_threshold: 0.3
    do_beamskip: false
    global_frame_id: "map"
    lambda_short: 0.1
    laser_likelihood_max_dist: 2.0
    laser_max_range: 100.0
    laser_min_range: -1.0
    laser_model_type: "likelihood_field"
    max_beams: 60
    max_particles: 2000
    min_particles: 500
    odom_frame_id: "odom"
    pf_err: 0.05
    pf_z: 0.99
    recovery_alpha_fast: 0.0
    recovery_alpha_slow: 0.0
    resample_interval: 1
    robot_model_type: "nav2_amcl::DifferentialMotionModel"
    save_pose_rate: 0.5
    sigma_hit: 0.2
    tf_buffer_duration: 30.0
    transform_tolerance: 1.0
    update_min_a: 0.2
    update_min_d: 0.25
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.5
    z_short: 0.05
    scan_topic: scan

bt_navigator:
  ros__parameters:
    use_sim_time: True
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    # Specify the path where the BT XML files are located
    plugin_lib_names:
    - nav2_compute_path_to_pose_action_bt_node
    - nav2_follow_path_action_bt_node
    - nav2_back_up_action_bt_node
    - nav2_spin_action_bt_node
    - nav2_wait_action_bt_node
    - nav2_clear_costmap_service_bt_node
    - nav2_is_stuck_condition_bt_node
    - nav2_have_feedback_condition_bt_node
    - nav2_is_path_valid_condition_bt_node
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

controller_server:
  ros__parameters:
    use_sim_time: True
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    progress_checker_plugin: "progress_checker"
    goal_checker_plugin: "goal_checker"
    controller_plugins: ["FollowPath"]

    # Progress checker parameters
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    # Goal checker parameters
    goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
      stateful: True

    # Humanoid-specific controller parameters
    FollowPath:
      plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
      desired_linear_vel: 0.5
      max_linear_vel: 0.8  # Adjust for humanoid capabilities
      min_linear_vel: 0.1
      max_angular_vel: 1.0
      min_angular_vel: 0.4
      lookahead_dist: 0.6
      lookahead_time: 1.5
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: false
      min_vel_ratio: 0.1
      use_regulated_linear_velocity_scaling: true
      use_cost_regulated_linear_velocity_scaling: true
      regulated_linear_scaling_min_radius: 0.9
      regulated_linear_scaling_min_speed: 0.25
      use_rotate_to_heading: false
      rotate_to_heading_angular_vel: 1.8
      max_angular_accel: 3.2
      max_linear_accel: 2.5

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: True
      rolling_window: true
      width: 6
      height: 6
      resolution: 0.05
      robot_radius: 0.35  # Humanoid-specific size
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        publish_voxel_map: True
        origin_z: 0.0
        z_resolution: 0.2
        z_voxels: 10
        max_obstacle_height: 2.0
        unknown_threshold: 15
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
      always_send_full_costmap: True

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: True
      robot_radius: 0.35  # Humanoid-specific size
      resolution: 0.05
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      always_send_full_costmap: True

planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner::NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true

smoother_server:
  ros__parameters:
    smoother_plugins: ["simple_smoother"]
    simple_smoother:
      plugin: "nav2_smoother::SimpleSmoother"
      tolerance: 0.01
      max_its: 1000
      do_refinement: True

behavior_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["spin", "backup", "wait"]
    spin:
      plugin: "nav2_behaviors::Spin"
      spin_dist: 1.57
    backup:
      plugin: "nav2_behaviors::BackUp"
      backup_dist: 0.15
      backup_speed: 0.025
    wait:
      plugin: "nav2_behaviors::Wait"
      wait_duration: 1.0
```

### 2. Navigation Node Implementation

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import String
import json


class HumanoidNavigationNode(Node):
    def __init__(self):
        super().__init__('humanoid_navigation_node')

        # Initialize TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Publisher for navigation goals
        self.nav_goal_pub = self.create_publisher(PoseStamped, 'goal_pose', 1)

        # Subscriber for voice commands
        self.voice_cmd_sub = self.create_subscription(
            String,
            'structured_commands',
            self.voice_command_callback,
            10
        )

        # Subscriber for path planning results
        self.path_sub = self.create_subscription(
            Path,
            'plan',
            self.path_callback,
            10
        )

        # Navigation status
        self.current_goal = None
        self.is_navigating = False

        self.get_logger().info('Humanoid Navigation Node initialized')

    def voice_command_callback(self, msg):
        """Handle voice commands that involve navigation"""
        try:
            command_data = json.loads(msg.data)
            command_type = command_data.get('type', '')
            
            if command_type == 'NAVIGATION':
                self.handle_navigation_command(command_data)
            elif command_type == 'PICKUP':
                # For pickup commands, we need to navigate first, then manipulate
                object_location = self.find_object_location(command_data['parameters']['object'])
                if object_location:
                    self.navigate_to_location(object_location)
                else:
                    self.get_logger().warn(f'Object {command_data["parameters"]["object"]} not found')
            elif command_type == 'MANIPULATION':
                # For manipulation, navigate to destination
                destination = command_data['parameters']['destination']
                location = self.get_location_pose(destination)
                if location:
                    self.navigate_to_location(location)
                else:
                    self.get_logger().warn(f'Destination {destination} not found')
                    
        except json.JSONDecodeError:
            self.get_logger().error(f'Invalid JSON in voice command: {msg.data}')
        except Exception as e:
            self.get_logger().error(f'Error processing voice command: {e}')

    def handle_navigation_command(self, command_data):
        """Handle navigation command with specific location"""
        params = command_data['parameters']
        
        if 'location' in params:
            location = params['location']
            location_pose = self.get_location_pose(location)
            
            if location_pose:
                self.navigate_to_location(location_pose)
            else:
                self.get_logger().warn(f'Location {location} not defined')
        else:
            # If no specific location in the command, use coordinates if available
            if 'x' in params and 'y' in params:
                pose = PoseStamped()
                pose.header.frame_id = 'map'
                pose.header.stamp = self.get_clock().now().to_msg()
                pose.pose.position.x = params['x']
                pose.pose.position.y = params['y']
                pose.pose.position.z = 0.0
                pose.pose.orientation.w = 1.0
                
                self.navigate_to_location(pose)

    def get_location_pose(self, location_name):
        """Convert location name to PoseStamped"""
        # Predefined locations in the environment
        locations = {
            'kitchen': {'x': 5.0, 'y': 3.0, 'theta': 0.0},
            'living room': {'x': 0.0, 'y': 0.0, 'theta': 0.0},
            'bedroom': {'x': -3.0, 'y': 4.0, 'theta': 0.0},
            'office': {'x': -2.0, 'y': -2.0, 'theta': 0.0},
            'table': {'x': 1.0, 'y': 2.0, 'theta': 0.0},
            'couch': {'x': 0.5, 'y': -1.0, 'theta': 0.0}
        }

        if location_name in locations:
            loc = locations[location_name]
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position.x = loc['x']
            pose.pose.position.y = loc['y']
            pose.pose.position.z = 0.0
            # Set orientation based on theta
            import math
            pose.pose.orientation.z = math.sin(loc['theta'] / 2.0)
            pose.pose.orientation.w = math.cos(loc['theta'] / 2.0)
            return pose
        else:
            return None

    def find_object_location(self, object_name):
        """Find the location of an object in the environment"""
        # In a real implementation, this would use perception to find the object
        # For now, we'll return a placeholder location
        self.get_logger().info(f'Searching for {object_name}')
        
        # Placeholder: return a location near the center
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = 0.0
        pose.pose.position.y = 0.0
        pose.pose.position.z = 0.0
        pose.pose.orientation.w = 1.0
        return pose

    def navigate_to_location(self, goal_pose):
        """Send navigation goal to the navigation stack"""
        self.current_goal = goal_pose
        self.is_navigating = True
        
        self.nav_goal_pub.publish(goal_pose)
        self.get_logger().info(f'Navigating to ({goal_pose.pose.position.x}, {goal_pose.pose.position.y})')

    def path_callback(self, msg):
        """Handle path planning results"""
        if self.is_navigating and self.current_goal:
            self.get_logger().info(f'Path calculated with {len(msg.poses)} waypoints')

    def destroy_node(self):
        """Cleanup when node is destroyed"""
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = HumanoidNavigationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Manipulation System Implementation

### 1. Manipulation Node Implementation

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose, Point
from sensor_msgs.msg import JointState
from moveit_msgs.msg import MoveItErrorCodes
from moveit_msgs.srv import GetPositionIK, GetPositionFK
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
import json
import math


class HumanoidManipulationNode(Node):
    def __init__(self):
        super().__init__('humanoid_manipulation_node')

        # Subscriber for structured commands
        self.cmd_sub = self.create_subscription(
            String,
            'structured_commands',
            self.command_callback,
            10
        )

        # Publisher for manipulation status
        self.status_pub = self.create_publisher(String, 'manipulation_status', 10)

        # Action client for joint trajectory control
        self.joint_traj_client = ActionClient(
            self, 
            FollowJointTrajectory, 
            'joint_trajectory_controller/follow_joint_trajectory'
        )

        # Joint names for humanoid arms (adjust based on your robot's URDF)
        self.left_arm_joints = [
            'left_shoulder_pitch', 'left_shoulder_roll', 'left_shoulder_yaw',
            'left_elbow_pitch', 'left_wrist_pitch', 'left_wrist_yaw'
        ]
        self.right_arm_joints = [
            'right_shoulder_pitch', 'right_shoulder_roll', 'right_shoulder_yaw',
            'right_elbow_pitch', 'right_wrist_pitch', 'right_wrist_yaw'
        ]

        # Current joint states
        self.current_joints = JointState()

        # Predefined grasp poses
        self.grasp_poses = {
            'front': self.create_grasp_pose(0.5, 0.0, 0.8),  # x, y, z in base frame
            'left': self.create_grasp_pose(0.4, -0.3, 0.8),
            'right': self.create_grasp_pose(0.4, 0.3, 0.8)
        }

        # Current manipulation state
        self.manipulation_active = False
        self.holding_object = False

        self.get_logger().info('Humanoid Manipulation Node initialized')

    def create_grasp_pose(self, x, y, z):
        """Create a grasp pose at the specified coordinates"""
        pose = Pose()
        pose.position.x = x
        pose.position.y = y
        pose.position.z = z
        # Simple orientation (facing down for pick-up)
        pose.orientation.x = 0.0
        pose.orientation.y = 0.5
        pose.orientation.z = 0.0
        pose.orientation.w = 0.866  # 30-degree rotation around Y axis
        return pose

    def command_callback(self, msg):
        """Handle manipulation commands"""
        try:
            command_data = json.loads(msg.data)
            command_type = command_data.get('type', '')
            
            if command_type == 'PICKUP':
                object_name = command_data['parameters']['object']
                self.pickup_object(object_name)
            elif command_type == 'MANIPULATION':
                object_name = command_data['parameters']['object']
                destination = command_data['parameters']['destination']
                self.place_object(object_name, destination)
                
        except json.JSONDecodeError:
            self.get_logger().error(f'Invalid JSON in command: {msg.data}')
        except KeyError as e:
            self.get_logger().error(f'Missing key in command: {e}')
        except Exception as e:
            self.get_logger().error(f'Error processing command: {e}')

    def pickup_object(self, object_name):
        """Attempt to pick up an object with the specified name"""
        if self.holding_object:
            self.get_logger().warn('Already holding an object, cannot pick up another')
            return

        self.get_logger().info(f'Attempting to pick up {object_name}')
        
        # In a real implementation, we would use perception to find the object
        # For now, we'll assume the robot is at a location where the object is reachable
        # and perform a predefined pick-up motion
        
        # Move to pre-grasp position
        if self.move_to_pregrasp_pose():
            # Move to grasp position
            if self.move_to_grasp_pose():
                # Close gripper (or perform grasp)
                if self.execute_grasp():
                    self.holding_object = True
                    self.get_logger().info(f'Successfully picked up {object_name}')
                    
                    # Publish success status
                    status_msg = String()
                    status_msg.data = f'Successfully picked up {object_name}'
                    self.status_pub.publish(status_msg)
                else:
                    self.get_logger().error('Failed to execute grasp')
            else:
                self.get_logger().error('Failed to reach grasp pose')
        else:
            self.get_logger().error('Failed to reach pre-grasp pose')

    def place_object(self, object_name, destination):
        """Place the currently held object at the destination"""
        if not self.holding_object:
            self.get_logger().warn('Not holding an object to place')
            return

        self.get_logger().info(f'Attempting to place {object_name} at {destination}')
        
        # In a real implementation, we would navigate to the destination
        # and perform the placement maneuver
        
        # Move to pre-place position
        if self.move_to_preplace_pose():
            # Move to place position
            if self.move_to_place_pose(destination):
                # Open gripper (or release object)
                if self.execute_release():
                    self.holding_object = False
                    self.get_logger().info(f'Successfully placed {object_name} at {destination}')
                    
                    # Publish success status
                    status_msg = String()
                    status_msg.data = f'Successfully placed {object_name} at {destination}'
                    self.status_pub.publish(status_msg)
                else:
                    self.get_logger().error('Failed to release object')
            else:
                self.get_logger().error('Failed to reach place pose')
        else:
            self.get_logger().error('Failed to reach pre-place pose')

    def move_to_pregrasp_pose(self):
        """Move to a safe position before grasping"""
        # Calculate a pregrasp pose (slightly above and away from the target)
        # For this example, we'll use a hardcoded position
        pregrasp_pose = self.create_grasp_pose(0.5, 0.0, 0.9)
        return self.move_arm_to_pose(pregrasp_pose, arm='right')

    def move_to_grasp_pose(self):
        """Move to the grasping position"""
        grasp_pose = self.create_grasp_pose(0.5, 0.0, 0.8)
        return self.move_arm_to_pose(grasp_pose, arm='right')

    def move_to_preplace_pose(self):
        """Move to a safe position before placing"""
        # For this example, we'll use a position above the head
        preplace_pose = self.create_grasp_pose(0.4, 0.0, 1.2)
        return self.move_arm_to_pose(preplace_pose, arm='right')

    def move_to_place_pose(self, destination):
        """Move to the placing position"""
        # In a real implementation, this would use the destination name
        # to look up a specific place pose
        place_pose = self.create_grasp_pose(0.5, 0.0, 0.7)
        return self.move_arm_to_pose(place_pose, arm='right')

    def move_arm_to_pose(self, target_pose, arm='right'):
        """Move the specified arm to the target pose using IK"""
        try:
            # For this example, we'll send a simple joint trajectory
            # In a real implementation, we'd use MoveIt! with inverse kinematics
            
            # Determine which joints to use
            joint_names = self.right_arm_joints if arm == 'right' else self.left_arm_joints
            
            # Create a simple trajectory goal
            goal = FollowJointTrajectory.Goal()
            goal.trajectory = JointTrajectory()
            goal.trajectory.joint_names = joint_names
            
            # Create trajectory points (simplified for this example)
            point = JointTrajectoryPoint()
            
            # These values are placeholders - in reality you'd calculate them using IK
            if arm == 'right':
                # Right arm ready position (example values)
                point.positions = [0.0, 0.0, 0.0, -0.5, 0.0, 0.0]  # Elbow bent
            else:
                # Left arm ready position
                point.positions = [0.0, 0.0, 0.0, -0.5, 0.0, 0.0]
                
            point.time_from_start.sec = 2  # 2 seconds to reach pose
            goal.trajectory.points = [point]
            
            # Wait for action server
            self.joint_traj_client.wait_for_server()
            
            # Send goal
            future = self.joint_traj_client.send_goal_async(goal)
            
            # For simplicity, we'll assume success
            # In a real implementation, you'd wait for the result
            return True
            
        except Exception as e:
            self.get_logger().error(f'Error moving arm to pose: {e}')
            return False

    def execute_grasp(self):
        """Execute the grasp action"""
        # In a real implementation, this would control the gripper
        # For this example, we'll just return True
        self.get_logger().info('Grasp executed')
        return True

    def execute_release(self):
        """Execute the release action"""
        # In a real implementation, this would open the gripper
        # For this example, we'll just return True
        self.get_logger().info('Release executed')
        return True

    def destroy_node(self):
        """Cleanup when node is destroyed"""
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = HumanoidManipulationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Integration with Voice Commands

### 1. Coordinated Behavior Node

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import json


class CoordinatedBehaviorNode(Node):
    def __init__(self):
        super().__init__('coordinated_behavior_node')

        # Subscribers for different command types
        self.voice_cmd_sub = self.create_subscription(
            String,
            'structured_commands',
            self.command_callback,
            10
        )

        # Publisher for navigation goals
        self.nav_goal_pub = self.create_publisher(PoseStamped, 'goal_pose', 1)

        # Publisher for manipulation commands
        self.manip_cmd_pub = self.create_publisher(String, 'manipulation_commands', 10)

        # Publisher for system status
        self.status_pub = self.create_publisher(String, 'system_status', 10)

        # Track the current task
        self.current_task = None
        self.task_queue = []

        self.get_logger().info('Coordinated Behavior Node initialized')

    def command_callback(self, msg):
        """Process incoming commands and coordinate behavior"""
        try:
            command_data = json.loads(msg.data)
            command_type = command_data.get('type', '')
            
            # Add command to the queue
            self.task_queue.append(command_data)
            
            # Process the next task if no task is currently active
            if not self.current_task and self.task_queue:
                self.process_next_task()
                
        except json.JSONDecodeError:
            self.get_logger().error(f'Invalid JSON in command: {msg.data}')
        except Exception as e:
            self.get_logger().error(f'Error processing command: {e}')

    def process_next_task(self):
        """Process the next task in the queue"""
        if not self.task_queue:
            return

        self.current_task = self.task_queue.pop(0)
        command_type = self.current_task.get('type', '')
        
        self.get_logger().info(f'Processing task: {command_type}')

        if command_type == 'NAVIGATION':
            self.execute_navigation()
        elif command_type == 'PICKUP':
            self.execute_pickup()
        elif command_type == 'MANIPULATION':
            self.execute_manipulation()
        else:
            self.get_logger().warn(f'Unknown command type: {command_type}')
            self.current_task = None
            if self.task_queue:
                self.process_next_task()  # Process the next task

    def execute_navigation(self):
        """Execute navigation task"""
        params = self.current_task.get('parameters', {})
        
        # Create and publish navigation goal
        nav_goal = PoseStamped()
        nav_goal.header.frame_id = 'map'
        nav_goal.header.stamp = self.get_clock().now().to_msg()
        
        nav_goal.pose.position.x = params.get('x', 0.0)
        nav_goal.pose.position.y = params.get('y', 0.0)
        nav_goal.pose.position.z = 0.0
        nav_goal.pose.orientation.w = 1.0
        
        self.nav_goal_pub.publish(nav_goal)
        
        # Publish status
        status_msg = String()
        status_msg.data = f'Navigating to ({params.get("x", 0)}, {params.get("y", 0)})'
        self.status_pub.publish(status_msg)

    def execute_pickup(self):
        """Execute pickup task - may involve navigation then manipulation"""
        # First, navigate to the object location
        # In a real implementation, this would require perception to find the object
        # For now, we'll assume it's at a known location
        
        # Publish navigation goal to go to object
        nav_goal = PoseStamped()
        nav_goal.header.frame_id = 'map'
        nav_goal.header.stamp = self.get_clock().now().to_msg()
        nav_goal.pose.position.x = 0.5  # Assume object is at 0.5, 0, 0.8
        nav_goal.pose.position.y = 0.0
        nav_goal.pose.position.z = 0.0
        nav_goal.pose.orientation.w = 1.0
        
        self.nav_goal_pub.publish(nav_goal)
        
        # After navigation completes (in a real system), we'd trigger manipulation
        # For now, we'll publish the manipulation command directly
        manip_cmd = String()
        manip_cmd.data = json.dumps({
            'type': 'PICKUP',
            'parameters': self.current_task.get('parameters', {})
        })
        
        self.manip_cmd_pub.publish(manip_cmd)
        
        # Publish status
        status_msg = String()
        object_name = self.current_task.get('parameters', {}).get('object', 'unknown')
        status_msg.data = f'Going to pick up {object_name}'
        self.status_pub.publish(status_msg)

    def execute_manipulation(self):
        """Execute manipulation task"""
        # In a real system, we'd first navigate to the destination
        # For now, we'll directly publish the manipulation command
        manip_cmd = String()
        manip_cmd.data = json.dumps({
            'type': 'MANIPULATION',
            'parameters': self.current_task.get('parameters', {})
        })
        
        self.manip_cmd_pub.publish(manip_cmd)
        
        # Publish status
        status_msg = String()
        params = self.current_task.get('parameters', {})
        object_name = params.get('object', 'unknown')
        destination = params.get('destination', 'unknown')
        status_msg.data = f'Placing {object_name} at {destination}'
        self.status_pub.publish(status_msg)

    def handle_task_completion(self):
        """Handle completion of the current task"""
        self.current_task = None
        # Process the next task in the queue if available
        if self.task_queue:
            self.process_next_task()

    def destroy_node(self):
        """Cleanup when node is destroyed"""
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CoordinatedBehaviorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## System Integration and Launch

### 1. Complete System Launch File

```python
# launch/capstone_system.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),

        # Navigation system nodes
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{
                'use_sim_time': use_sim_time,
                'yaml_filename': os.path.join(get_package_share_directory('physical_ai_examples'), 
                                             'maps', 'map.yaml')
            }]
        ),
        
        Node(
            package='nav2_localizer',
            executable='amcl',
            name='amcl',
            parameters=[
                os.path.join(get_package_share_directory('physical_ai_examples'), 
                            'config', 'amcl.yaml'),
                {'use_sim_time': use_sim_time}
            ]
        ),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[
                os.path.join(get_package_share_directory('physical_ai_examples'), 
                            'config', 'planner_server.yaml'),
                {'use_sim_time': use_sim_time}
            ]
        ),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[
                os.path.join(get_package_share_directory('physical_ai_examples'), 
                            'config', 'controller_server.yaml'),
                {'use_sim_time': use_sim_time}
            ]
        ),

        # Voice command system nodes (from previous chapter)
        Node(
            package='physical_ai_examples',
            executable='audio_capture_node',
            name='audio_capture_node',
            output='screen'
        ),
        Node(
            package='physical_ai_examples',
            executable='whisper_processing_node',
            name='whisper_processing_node',
            output='screen'
        ),
        Node(
            package='physical_ai_examples',
            executable='command_interpretation_node',
            name='command_interpretation_node',
            output='screen'
        ),

        # Navigation and manipulation nodes
        Node(
            package='physical_ai_examples',
            executable='humanoid_navigation_node',
            name='humanoid_navigation_node',
            output='screen'
        ),
        Node(
            package='physical_ai_examples',
            executable='humanoid_manipulation_node',
            name='humanoid_manipulation_node',
            output='screen'
        ),
        Node(
            package='physical_ai_examples',
            executable='coordinated_behavior_node',
            name='coordinated_behavior_node',
            output='screen'
        )
    ])
```

## Performance Optimization

### 1. Navigation Optimization

```python
class OptimizedNavigationNode(HumanoidNavigationNode):
    def __init__(self):
        super().__init__()
        
        # Cache for frequently accessed locations
        self.location_cache = {}
        
        # Timeout for navigation goals
        self.nav_timeout = 60.0  # seconds
        
        # Smoothing for planned paths
        self.path_smoothing_enabled = True

    def get_location_pose(self, location_name):
        """Optimized location retrieval with caching"""
        if location_name in self.location_cache:
            return self.location_cache[location_name]
        
        # Call parent method to get the pose
        pose = super().get_location_pose(location_name)
        if pose:
            self.location_cache[location_name] = pose
            
        return pose
```

### 2. Manipulation Optimization

```python
class OptimizedManipulationNode(HumanoidManipulationNode):
    def __init__(self):
        super().__init__()
        
        # Pre-calculated inverse kinematics solutions for common poses
        self.ik_solutions_cache = {}
        
        # Trajectory optimization flags
        self.optimize_trajectories = True
        
        # Collision checking optimization
        self.collision_check_frequency = 10  # Check every 10th calculation

    def move_arm_to_pose(self, target_pose, arm='right'):
        """Optimized arm movement with caching"""
        # Create a key for the pose
        pose_key = (target_pose.position.x, target_pose.position.y, 
                   target_pose.position.z, target_pose.orientation.w)
        
        # Check if we have a cached solution
        if pose_key in self.ik_solutions_cache:
            joints = self.ik_solutions_cache[pose_key]
            # Execute the cached joint trajectory
            return self.execute_joint_trajectory(joints, arm)
        
        # Calculate new solution if not cached
        joints = self.calculate_ik_solution(target_pose, arm)
        
        # Cache the solution
        self.ik_solutions_cache[pose_key] = joints
        
        # Execute the trajectory
        return self.execute_joint_trajectory(joints, arm)
```

## Testing and Validation

### 1. Unit Tests for Navigation

```python
import unittest
from unittest.mock import Mock, patch

class TestHumanoidNavigationNode(unittest.TestCase):
    def setUp(self):
        self.node = HumanoidNavigationNode()
        
    def test_get_location_pose_valid(self):
        """Test that a valid location returns a proper pose"""
        pose = self.node.get_location_pose('kitchen')
        
        self.assertIsNotNone(pose)
        self.assertEqual(pose.header.frame_id, 'map')
        self.assertEqual(pose.pose.position.x, 5.0)
        self.assertEqual(pose.pose.position.y, 3.0)
        
    def test_get_location_pose_invalid(self):
        """Test that an invalid location returns None"""
        pose = self.node.get_location_pose('unknown_location')
        
        self.assertIsNone(pose)
```

### 2. Integration Tests for Complete System

```bash
# Test navigation to known locations
ros2 launch physical_ai_examples capstone_system.launch.py

# Send a navigation command
ros2 topic pub /structured_commands std_msgs/String "{data: '{\"type\": \"NAVIGATION\", \"parameters\": {\"location\": \"kitchen\", \"x\": 5.0, \"y\": 3.0}}'}"

# Monitor navigation status
ros2 topic echo /goal_pose geometry_msgs/PoseStamped

# Test manipulation commands
ros2 topic pub /structured_commands std_msgs/String "{data: '{\"type\": \"PICKUP\", \"parameters\": {\"object\": \"cup\"}}'}"

# Monitor manipulation status
ros2 topic echo /manipulation_status std_msgs/String
```

## Safety Considerations

### 1. Navigation Safety

```python
def safe_navigate_to_location(self, goal_pose):
    """Safely navigate to location with safety checks"""
    # Validate goal pose is within bounds
    if not self.is_pose_valid(goal_pose):
        self.get_logger().error('Goal pose is invalid or out of bounds')
        return False
    
    # Check if path is clear (using costmap)
    if not self.is_path_clear(goal_pose):
        self.get_logger().warn('Path to goal may be blocked')
        return False
    
    # Proceed with navigation
    return self.navigate_to_location(goal_pose)

def is_pose_valid(self, pose):
    """Check if a pose is valid (within operational bounds)"""
    # Check if coordinates are within map bounds
    # Check if orientation is physically possible
    # Return True if pose is valid, False otherwise
    return True  # Simplified for example
```

### 2. Manipulation Safety

```python
def safe_execute_grasp(self, object_name):
    """Safely execute grasp with collision checking"""
    # Check if object is graspable
    if not self.is_object_graspable(object_name):
        self.get_logger().error(f'Object {object_name} is not graspable')
        return False
    
    # Check if path to object is collision-free
    if not self.is_path_collision_free('grasp_pose'):
        self.get_logger().error('Path to grasp pose is not collision-free')
        return False
    
    # Execute grasp
    return self.execute_grasp()
```

## Troubleshooting Common Issues

### 1. Navigation Failures
- Check that the map is loaded correctly
- Verify that the robot is properly localized
- Ensure the costmaps are updating correctly
- Review the Nav2 configuration parameters

### 2. Manipulation Failures
- Verify that MoveIt! is running and configured properly
- Check joint limits in the URDF
- Ensure the robot is in a valid starting state
- Validate inverse kinematics solutions

### 3. Integration Issues
- Verify message types and topic names match between nodes
- Check timing and synchronization between components
- Monitor system performance under load

## Summary

This chapter implemented the autonomous navigation and manipulation capabilities for our humanoid robot. We configured Nav2 for humanoid-specific requirements, implemented manipulation nodes for object interaction, and created a coordination layer to combine navigation and manipulation based on voice commands.

The complete system now includes:
- Voice command processing with Whisper
- Natural language interpretation
- Autonomous navigation with obstacle avoidance
- Object manipulation capabilities
- Coordinated behavior execution

## Exercises

1. Implement a recovery behavior for when navigation fails to reach a goal.
2. Add collision detection and avoidance for manipulation tasks.
3. Create a system for learning and storing new object locations.
4. Implement a more sophisticated task planning system that can handle complex multi-step commands.
5. Design a safety system that validates all actions before execution.