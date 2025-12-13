#!/usr/bin/env python3

"""
Humanoid Manipulation System
This module provides manipulation capabilities for a humanoid robot, 
including arm control, grasp planning, and object manipulation.
"""

import math
import time
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

import numpy as np


class GraspType(Enum):
    """Types of grasps the humanoid can perform"""
    PINCH = "pinch"
    PALM = "palm"
    SUCTION = "suction"
    PINCER = "pincer"


class ManipulationStatus(Enum):
    """Status of manipulation operations"""
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    UNKNOWN = "unknown"


@dataclass
class ObjectProperties:
    """Properties of an object to be manipulated"""
    name: str
    size: Tuple[float, float, float]  # width, height, depth in meters
    weight: float  # in kilograms
    center_of_mass: Tuple[float, float, float]  # relative to object's origin
    grasp_points: List[Tuple[float, float, float]]  # potential grasp points
    material: str = "unknown"  # material type
    fragile: bool = False  # whether object is fragile


@dataclass
class Pose:
    """Represents a position and orientation in 3D space"""
    position: Tuple[float, float, float]  # x, y, z
    orientation: Tuple[float, float, float, float]  # qx, qy, qz, qw (quaternion)


@dataclass
class GraspPlan:
    """A planned grasp for manipulating an object"""
    grasp_type: GraspType
    grasp_pose: Pose
    approach_direction: Tuple[float, float, float]
    lift_direction: Tuple[float, float, float]
    object_properties: ObjectProperties
    success_probability: float = 1.0


class HumanoidManipulationSystem:
    """
    A system for controlling the manipulation capabilities of a humanoid robot
    """
    
    def __init__(self):
        """Initialize the manipulation system"""
        self.left_arm_pose = Pose((0.0, 0.2, 1.2), (0.0, 0.0, 0.0, 1.0))  # Initial pose
        self.right_arm_pose = Pose((0.0, -0.2, 1.2), (0.0, 0.0, 0.0, 1.0))  # Initial pose
        self.gripper_state = {"left": 0.0, "right": 0.0}  # 0.0 = open, 1.0 = closed
        self.is_moving = False
        
        # Known object database
        self.object_database = self._initialize_object_database()
        
        print("Humanoid Manipulation System initialized")

    def _initialize_object_database(self) -> Dict[str, ObjectProperties]:
        """Initialize the database of known objects"""
        return {
            "red_cup": ObjectProperties(
                name="red_cup",
                size=(0.08, 0.1, 0.08),
                weight=0.2,
                center_of_mass=(0.0, 0.0, 0.05),
                grasp_points=[(0.0, 0.0, 0.08)],
                material="plastic",
                fragile=True
            ),
            "wooden_box": ObjectProperties(
                name="wooden_box",
                size=(0.15, 0.15, 0.15),
                weight=0.5,
                center_of_mass=(0.0, 0.0, 0.075),
                grasp_points=[(0.0, 0.0, 0.15), (0.075, 0.075, 0.075)],
                material="wood",
                fragile=False
            ),
            "book": ObjectProperties(
                name="book",
                size=(0.2, 0.02, 0.15),
                weight=0.4,
                center_of_mass=(0.0, 0.0, 0.01),
                grasp_points=[(-0.1, 0.0, 0.02), (0.0, 0.0, 0.02)],
                material="paper",
                fragile=True
            ),
            "ball": ObjectProperties(
                name="ball",
                size=(0.14, 0.14, 0.14),  # diameter
                weight=0.3,
                center_of_mass=(0.0, 0.0, 0.0),
                grasp_points=[(0.0, 0.0, 0.07)],
                material="rubber",
                fragile=False
            )
        }

    def detect_object(self, object_name: str) -> Optional[ObjectProperties]:
        """
        Simulate object detection and return properties if found
        
        Args:
            object_name: Name of the object to detect
            
        Returns:
            ObjectProperties if found, None otherwise
        """
        print(f"Detecting object: {object_name}")
        
        # In a real implementation, this would use perception systems
        # For simulation, we'll look up the object in our database
        if object_name in self.object_database:
            obj = self.object_database[object_name]
            print(f"Found object: {obj.name}")
            return obj
        else:
            print(f"Object not found: {object_name}")
            return None

    def plan_grasp(self, object_props: ObjectProperties, 
                   target_pose: Pose, arm: str = "right") -> Optional[GraspPlan]:
        """
        Plan a grasp for manipulating the given object
        
        Args:
            object_props: Properties of the object to grasp
            target_pose: Target pose for the manipulation
            arm: Which arm to use ('left' or 'right')
            
        Returns:
            GraspPlan if successful, None otherwise
        """
        print(f"Planning grasp for {object_props.name} using {arm} arm")
        
        # Determine grasp type based on object properties
        grasp_type = self._select_grasp_type(object_props)
        
        # Calculate grasp pose based on object properties and target
        grasp_pose = self._calculate_grasp_pose(object_props, target_pose)
        
        if grasp_pose is None:
            print("Could not calculate a valid grasp pose")
            return None
        
        # Determine approach and lift directions
        approach_dir = self._calculate_approach_direction(grasp_pose, target_pose)
        lift_dir = (0.0, 0.0, 0.1)  # Lift upward by default
        
        # Calculate success probability based on factors
        success_prob = self._calculate_success_probability(object_props, grasp_type)
        
        grasp_plan = GraspPlan(
            grasp_type=grasp_type,
            grasp_pose=grasp_pose,
            approach_direction=approach_dir,
            lift_direction=lift_dir,
            object_properties=object_props,
            success_probability=success_prob
        )
        
        print(f"Grasp plan created: {grasp_type.value} at {grasp_pose.position}")
        return grasp_plan

    def _select_grasp_type(self, obj_props: ObjectProperties) -> GraspType:
        """Select appropriate grasp type based on object properties"""
        size = max(obj_props.size[:2])  # Use max of width/height for 2D size
        
        if size < 0.05:  # Small objects
            return GraspType.PINCH
        elif obj_props.size[1] < 0.05:  # Thin objects like books
            return GraspType.PALM
        elif size < 0.15:  # Medium objects
            return GraspType.PINCER
        else:  # Large objects
            return GraspType.PALM

    def _calculate_grasp_pose(self, obj_props: ObjectProperties, 
                             target_pose: Pose) -> Optional[Pose]:
        """Calculate the optimal grasp pose for the object"""
        # For simplicity, we'll use the first grasp point
        # In a real implementation, this would use inverse kinematics
        if not obj_props.grasp_points:
            return None
            
        grasp_point = obj_props.grasp_points[0]
        
        # Calculate grasp position relative to object's position
        grasp_pos = (
            target_pose.position[0] + grasp_point[0],
            target_pose.position[1] + grasp_point[1],
            target_pose.position[2] + grasp_point[2]
        )
        
        # For simplicity, use the same orientation as the target
        grasp_orientation = target_pose.orientation
        
        return Pose(position=grasp_pos, orientation=grasp_orientation)

    def _calculate_approach_direction(self, grasp_pose: Pose, 
                                    target_pose: Pose) -> Tuple[float, float, float]:
        """Calculate the approach direction for grasping"""
        # Approach from above by default
        return (0.0, 0.0, -1.0)

    def _calculate_success_probability(self, obj_props: ObjectProperties, 
                                     grasp_type: GraspType) -> float:
        """Calculate the success probability of the grasp"""
        # Base probability
        prob = 0.9
        
        # Reduce probability for fragile objects
        if obj_props.fragile:
            prob *= 0.8
            
        # Reduce probability for heavy objects
        if obj_props.weight > 0.5:
            prob *= 0.7
            
        return max(0.1, prob)  # Minimum 10% success probability

    def execute_grasp_plan(self, grasp_plan: GraspPlan, arm: str = "right") -> ManipulationStatus:
        """
        Execute a pre-planned grasp
        
        Args:
            grasp_plan: The grasp plan to execute
            arm: Which arm to use ('left' or 'right')
            
        Returns:
            ManipulationStatus indicating the result
        """
        if self.is_moving:
            print("Manipulator is already in motion, cannot execute new plan")
            return ManipulationStatus.FAILED
            
        print(f"Executing {grasp_plan.grasp_type.value} grasp with {arm} arm")
        
        # Check success probability
        if grasp_plan.success_probability < 0.3:
            print(f"Grasp plan has low success probability ({grasp_plan.success_probability:.2f}), aborting")
            return ManipulationStatus.FAILED
            
        self.is_moving = True
        
        try:
            # Move to approach position
            approach_pos = (
                grasp_plan.grasp_pose.position[0] + grasp_plan.approach_direction[0] * 0.1,
                grasp_plan.grasp_pose.position[1] + grasp_plan.approach_direction[1] * 0.1,
                grasp_plan.grasp_pose.position[2] + grasp_plan.approach_direction[2] * 0.1
            )
            
            print(f"Moving to approach position: {approach_pos}")
            self._move_arm_to_position(approach_pos, arm)
            time.sleep(1)  # Simulate movement time
            
            # Move to grasp position
            print(f"Moving to grasp position: {grasp_plan.grasp_pose.position}")
            self._move_arm_to_position(grasp_plan.grasp_pose.position, arm)
            time.sleep(0.5)  # Simulate movement time
            
            # Close gripper
            print(f"Closing gripper on {grasp_plan.object_properties.name}")
            self._close_gripper(arm, grasp_plan.object_properties.weight)
            time.sleep(0.5)  # Simulate gripper action
            
            # Lift object
            lift_pos = (
                grasp_plan.grasp_pose.position[0] + grasp_plan.lift_direction[0] * 0.1,
                grasp_plan.grasp_pose.position[1] + grasp_plan.lift_direction[1] * 0.1,
                grasp_plan.grasp_pose.position[2] + grasp_plan.lift_direction[2] * 0.1
            )
            
            print(f"Lifting object to: {lift_pos}")
            self._move_arm_to_position(lift_pos, arm)
            time.sleep(0.5)  # Simulate lifting
            
            print("Grasp executed successfully")
            return ManipulationStatus.SUCCESS
            
        except Exception as e:
            print(f"Error during grasp execution: {e}")
            return ManipulationStatus.FAILED
        finally:
            self.is_moving = False

    def _move_arm_to_position(self, position: Tuple[float, float, float], arm: str):
        """Simulate moving an arm to a position"""
        # In a real implementation, this would solve inverse kinematics
        # and send commands to the robot's joints
        
        # Update the internal pose tracking
        if arm == "left":
            self.left_arm_pose = Pose(position, self.left_arm_pose.orientation)
        elif arm == "right":
            self.right_arm_pose = Pose(position, self.right_arm_pose.orientation)
        else:
            raise ValueError(f"Invalid arm: {arm}")

    def _close_gripper(self, arm: str, object_weight: float):
        """Simulate closing the gripper"""
        # Check if object is too heavy
        max_weight = 2.0  # Maximum weight the gripper can handle
        if object_weight > max_weight:
            print(f"Object too heavy to grasp ({object_weight}kg > {max_weight}kg)")
            raise Exception("Object too heavy")
        
        # Close the gripper
        self.gripper_state[arm] = 1.0  # Fully closed
        print(f"{arm} gripper closed")

    def _open_gripper(self, arm: str):
        """Simulate opening the gripper"""
        self.gripper_state[arm] = 0.0  # Fully open
        print(f"{arm} gripper opened")

    def place_object(self, target_pose: Pose, arm: str = "right") -> ManipulationStatus:
        """
        Place the currently held object at the target pose
        
        Args:
            target_pose: Where to place the object
            arm: Which arm is holding the object
            
        Returns:
            ManipulationStatus indicating the result
        """
        if self.gripper_state[arm] == 0.0:
            print(f"No object detected in {arm} gripper")
            return ManipulationStatus.FAILED
            
        if self.is_moving:
            print("Manipulator is already in motion, cannot place object")
            return ManipulationStatus.FAILED
        
        print(f"Placing object at {target_pose.position}")
        
        self.is_moving = True
        try:
            # Move to target position
            print(f"Moving to placement position: {target_pose.position}")
            self._move_arm_to_position(target_pose.position, arm)
            time.sleep(0.5)  # Simulate movement time
            
            # Open gripper to release object
            print(f"Opening gripper to release object")
            self._open_gripper(arm)
            time.sleep(0.3)  # Simulate gripper action
            
            # Move away from the placed object
            move_away_pos = (
                target_pose.position[0],
                target_pose.position[1],
                target_pose.position[2] + 0.05  # Move up slightly
            )
            print(f"Moving away from object: {move_away_pos}")
            self._move_arm_to_position(move_away_pos, arm)
            time.sleep(0.3)  # Simulate movement time
            
            print("Object placed successfully")
            return ManipulationStatus.SUCCESS
            
        except Exception as e:
            print(f"Error during placement: {e}")
            return ManipulationStatus.FAILED
        finally:
            self.is_moving = False

    def execute_manipulation_task(self, object_name: str, target_pose: Pose, 
                                arm: str = "right") -> ManipulationStatus:
        """
        Execute a complete manipulation task: pick up and place an object
        
        Args:
            object_name: Name of the object to manipulate
            target_pose: Where to place the object
            arm: Which arm to use
            
        Returns:
            ManipulationStatus indicating the result
        """
        print(f"Starting manipulation task: move {object_name} to {target_pose.position}")
        
        # Detect the object
        obj_props = self.detect_object(object_name)
        if obj_props is None:
            print(f"Failed to detect object: {object_name}")
            return ManipulationStatus.FAILED
        
        # Plan the grasp
        # For this simulation, we'll use a default position for the object
        obj_pose = Pose(
            position=(0.5, 0.0, 0.7),  # Default object position 
            orientation=(0.0, 0.0, 0.0, 1.0)
        )
        grasp_plan = self.plan_grasp(obj_props, obj_pose, arm)
        
        if grasp_plan is None:
            print("Failed to plan grasp")
            return ManipulationStatus.FAILED
        
        # Execute the grasp
        grasp_status = self.execute_grasp_plan(grasp_plan, arm)
        if grasp_status != ManipulationStatus.SUCCESS:
            print("Failed to execute grasp")
            return grasp_status
        
        # Place the object
        place_status = self.place_object(target_pose, arm)
        
        if place_status == ManipulationStatus.SUCCESS:
            print(f"Successfully moved {object_name} to target location")
            return ManipulationStatus.SUCCESS
        else:
            print(f"Failed to place {object_name}")
            # Try to drop the object safely
            self._open_gripper(arm)
            return ManipulationStatus.FAILED


# Example usage and testing
def main():
    """Example usage of the manipulation system"""
    # Initialize the manipulation system
    manipulator = HumanoidManipulationSystem()
    
    # Define a target position to place an object
    target_pose = Pose(
        position=(0.8, -0.5, 0.8),
        orientation=(0.0, 0.0, 0.0, 1.0)
    )
    
    print("Humanoid Manipulation System Demo")
    print("===============================")
    
    # Test picking up and placing different objects
    test_objects = ["red_cup", "book", "ball"]
    
    for obj_name in test_objects:
        print(f"\n--- Manipulation Task: {obj_name} ---")
        
        status = manipulator.execute_manipulation_task(obj_name, target_pose)
        print(f"Task result: {status.value}")
        
        # Small delay between tasks
        time.sleep(1)
    
    # Test error handling with a heavy object
    print(f"\n--- Testing with Unknown/Heavy Object ---")
    # Create a temporary heavy object in the database
    manipulator.object_database["heavy_box"] = ObjectProperties(
        name="heavy_box",
        size=(0.3, 0.3, 0.3),
        weight=5.0,  # Too heavy
        center_of_mass=(0.0, 0.0, 0.15),
        grasp_points=[(0.0, 0.0, 0.3)],
        material="steel",
        fragile=False
    )
    
    status = manipulator.execute_manipulation_task("heavy_box", target_pose)
    print(f"Task result: {status.value}")


# ROS node implementation (would be used in a real ROS environment)
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Pose as GeometryPose
    from geometry_msgs.msg import Point, Quaternion
    from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
    from control_msgs.msg import JointTrajectoryController
    
    class ManipulationROSNode(Node):
        """
        ROS Node implementation of the manipulation system
        """
        
        def __init__(self):
            super().__init__('humanoid_manipulation_node')
            
            # Initialize the manipulation system
            self.manipulator = HumanoidManipulationSystem()
            
            # Create publishers and subscribers
            self.joint_traj_pub = self.create_publisher(
                JointTrajectory, 
                '/manipulation_controller/joint_trajectory', 
                10
            )
            
            self.get_logger().info('Humanoid Manipulation ROS Node initialized')

        def execute_manipulation_task_ros(self, object_name: str, target_pose_msg: GeometryPose):
            """Execute manipulation task using ROS Pose message"""
            # Convert ROS Pose to our internal representation
            position = (target_pose_msg.position.x, 
                       target_pose_msg.position.y, 
                       target_pose_msg.position.z)
            orientation = (target_pose_msg.orientation.x,
                          target_pose_msg.orientation.y,
                          target_pose_msg.orientation.z,
                          target_pose_msg.orientation.w)
            
            target = Pose(position=position, orientation=orientation)
            
            # Execute the manipulation task
            return self.manipulator.execute_manipulation_task(object_name, target)
            
        def destroy_node(self):
            """Cleanup when node is destroyed"""
            super().destroy_node()

    def run_ros_node():
        """Run the ROS node version"""
        rclpy.init()
        node = ManipulationROSNode()
        
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()
            
except ImportError:
    # If ROS is not available, define a placeholder
    def run_ros_node():
        print("ROS not available, skipping ROS node example")


if __name__ == "__main__":
    print("Humanoid Manipulation System")
    print("=============================")
    print("Choose mode:")
    print("1. Standalone demo")
    print("2. ROS node (if ROS is available)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        run_ros_node()
    else:
        main()