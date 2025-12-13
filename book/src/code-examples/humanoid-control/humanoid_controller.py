#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Header
import math
import time


class HumanoidController(Node):
    def __init__(self):
        super().__init__('humanoid_controller')
        
        # Publisher for joint trajectory commands
        self.trajectory_pub = self.create_publisher(
            JointTrajectory, 
            '/joint_trajectory', 
            10
        )
        
        # Subscriber for joint states
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        # Timer for sending commands
        self.timer = self.create_timer(0.1, self.control_loop)  # 10 Hz
        
        # Initialize joint positions
        self.joint_positions = {}
        self.joint_names = [
            'left_shoulder_joint', 'left_elbow_joint', 
            'right_shoulder_joint', 'right_elbow_joint',
            'left_hip_joint', 'left_knee_joint', 'left_ankle_joint',
            'right_hip_joint', 'right_knee_joint', 'right_ankle_joint'
        ]
        
        # Initialize all joints to 0
        for name in self.joint_names:
            self.joint_positions[name] = 0.0
            
        self.get_logger().info('Humanoid controller initialized')
        
        # Initialize a simple walking pattern
        self.step_count = 0
        self.walking_pattern = [
            # Position 1: Initial stance
            {
                'left_hip_joint': 0.0, 'left_knee_joint': 0.0, 'left_ankle_joint': 0.0,
                'right_hip_joint': 0.0, 'right_knee_joint': 0.0, 'right_ankle_joint': 0.0,
                'left_shoulder_joint': 0.0, 'left_elbow_joint': 0.0,
                'right_shoulder_joint': 0.0, 'right_elbow_joint': 0.0
            },
            # Position 2: Step forward with left foot
            {
                'left_hip_joint': 0.2, 'left_knee_joint': 0.0, 'left_ankle_joint': -0.2,
                'right_hip_joint': -0.1, 'right_knee_joint': 0.0, 'right_ankle_joint': 0.1,
                'left_shoulder_joint': 0.1, 'left_elbow_joint': -0.5,
                'right_shoulder_joint': -0.1, 'right_elbow_joint': 0.5
            },
            # Position 3: Return to center
            {
                'left_hip_joint': 0.0, 'left_knee_joint': 0.0, 'left_ankle_joint': 0.0,
                'right_hip_joint': 0.0, 'right_knee_joint': 0.0, 'right_ankle_joint': 0.0,
                'left_shoulder_joint': 0.0, 'left_elbow_joint': 0.0,
                'right_shoulder_joint': 0.0, 'right_elbow_joint': 0.0
            },
            # Position 4: Step forward with right foot
            {
                'left_hip_joint': -0.1, 'left_knee_joint': 0.0, 'left_ankle_joint': 0.1,
                'right_hip_joint': 0.2, 'right_knee_joint': 0.0, 'right_ankle_joint': -0.2,
                'left_shoulder_joint': -0.1, 'left_elbow_joint': 0.5,
                'right_shoulder_joint': 0.1, 'right_elbow_joint': -0.5
            }
        ]

    def joint_state_callback(self, msg):
        """Update joint positions from received joint states"""
        for i, name in enumerate(msg.name):
            if name in self.joint_positions:
                self.joint_positions[name] = msg.position[i]

    def control_loop(self):
        """Main control loop to send joint commands"""
        # Get the current walking pattern position
        pattern_pos = self.walking_pattern[self.step_count % len(self.walking_pattern)]
        
        # Create and send trajectory command
        self.send_joint_trajectory_command(pattern_pos)
        
        # Increment step count
        self.step_count += 1

    def send_joint_trajectory_command(self, target_positions):
        """Send a joint trajectory command to move to target positions"""
        traj_msg = JointTrajectory()
        traj_msg.header = Header()
        traj_msg.header.stamp = self.get_clock().now().to_msg()
        traj_msg.header.frame_id = 'torso'
        
        # Set joint names
        traj_msg.joint_names = list(target_positions.keys())
        
        # Create trajectory point
        point = JointTrajectoryPoint()
        point.positions = list(target_positions.values())
        point.velocities = [0.0] * len(target_positions)  # Zero velocity
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 50000000  # 0.05 seconds
        
        traj_msg.points = [point]
        
        # Publish the trajectory
        self.trajectory_pub.publish(traj_msg)
        self.get_logger().info(f'Sent trajectory command: {target_positions}')


def main(args=None):
    rclpy.init(args=args)
    controller = HumanoidController()
    
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    
    controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()