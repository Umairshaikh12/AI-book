#!/usr/bin/env python3

"""
Voice Command and Navigation Integration System
This module demonstrates how to integrate voice command recognition with 
navigation capabilities in a humanoid robot system.
"""

import threading
import time
import json
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

# Import components from other modules
try:
    from ..voice-commands.whisper_interface import WhisperInterface, VoiceCommand
    from ..llm-planning.llm_action_planner import LLMActionPlanner, ActionType
except ImportError:
    # If the modules aren't available, create mock classes for this example
    print("Warning: Could not import required modules. Using mock implementations.")
    
    class VoiceCommand:
        def __init__(self, text: str = "", confidence: float = 1.0, timestamp: float = 0.0):
            self.text = text
            self.confidence = confidence
            self.timestamp = timestamp
    
    class ActionType:
        NAVIGATION = "navigation"
        MANIPULATION = "manipulation"
        COMMUNICATION = "communication"
    
    class MockComponent:
        def __init__(self, *args, **kwargs):
            pass
        
        def set_recognition_callback(self, callback):
            pass
        
        def start_listening(self):
            pass
        
        def stop_listening(self):
            pass
        
        def set_action_callback(self, action_type, callback):
            pass
        
        def execute_command(self, command):
            return True
    
    WhisperInterface = MockComponent
    LLMActionPlanner = MockComponent


@dataclass
class NavigationGoal:
    """Represents a navigation goal with coordinates and orientation"""
    x: float
    y: float
    theta: float  # Orientation in radians
    frame_id: str = "map"
    description: str = ""


class VoiceNavigationIntegrator:
    """
    Integrates voice command recognition with navigation system
    """
    
    def __init__(self, whisper_model_size: str = "base", llm_provider: str = "rule_based_demo"):
        """
        Initialize the voice navigation integration system
        
        Args:
            whisper_model_size: Size of the Whisper model to use
            llm_provider: LLM provider to use for action planning
        """
        # Initialize voice recognition
        self.whisper = WhisperInterface(model_size=whisper_model_size)
        self.whisper.set_recognition_callback(self._on_voice_command)
        
        # Initialize LLM action planner
        self.planner = LLMActionPlanner(llm_provider=llm_provider)
        
        # Register navigation callback
        self.planner.set_action_callback(ActionType.NAVIGATION, self._execute_navigation)
        self.planner.set_action_callback(ActionType.COMMUNICATION, self._execute_communication)
        
        # Navigation callbacks
        self.navigation_callback: Optional[Callable[[NavigationGoal], bool]] = None
        self.communication_callback: Optional[Callable[[str], bool]] = None
        
        # System state
        self.is_active = False
        self.active_thread: Optional[threading.Thread] = None
        
        # Command queue for processing
        self.command_queue = []
        self.queue_lock = threading.Lock()
        
        print("Voice Navigation Integration System initialized")

    def set_navigation_callback(self, callback: Callable[[NavigationGoal], bool]):
        """
        Set the callback function for executing navigation goals
        
        Args:
            callback: Function to call with NavigationGoal to execute
        """
        self.navigation_callback = callback

    def set_communication_callback(self, callback: Callable[[str], bool]):
        """
        Set the callback function for executing communication actions
        
        Args:
            callback: Function to call with message string to communicate
        """
        self.communication_callback = callback

    def _on_voice_command(self, command: VoiceCommand):
        """
        Handle recognized voice commands
        
        Args:
            command: The recognized voice command
        """
        if command.confidence > 0.5:  # Only process commands with sufficient confidence
            print(f"Heard command: '{command.text}' (confidence: {command.confidence:.2f})")
            
            # Add to command queue for processing
            with self.queue_lock:
                self.command_queue.append(command)
                
            # Process all queued commands
            self._process_command_queue()
        else:
            print(f"Ignoring low-confidence command: '{command.text}' (confidence: {command.confidence:.2f})")

    def _process_command_queue(self):
        """Process all commands in the queue"""
        with self.queue_lock:
            commands_to_process = self.command_queue[:]
            self.command_queue = []
        
        for command in commands_to_process:
            self._handle_command(command)

    def _handle_command(self, command: VoiceCommand):
        """
        Handle a single voice command by planning and executing it
        
        Args:
            command: The voice command to handle
        """
        try:
            # Use the LLM planner to create an action plan
            success = self.planner.execute_command(command.text)
            if success:
                print(f"Successfully executed command: '{command.text}'")
            else:
                print(f"Failed to execute command: '{command.text}'")
                
        except Exception as e:
            print(f"Error handling command '{command.text}': {e}")

    def _execute_navigation(self, action) -> bool:
        """
        Execute navigation action
        
        Args:
            action: The navigation action to execute
            
        Returns:
            True if successful, False otherwise
        """
        if not self.navigation_callback:
            print("Warning: No navigation callback registered")
            return False
        
        try:
            params = action.parameters
            goal = NavigationGoal(
                x=params.get('x', 0.0),
                y=params.get('y', 0.0),
                theta=params.get('theta', 0.0),
                description=params.get('location', 'unknown location')
            )
            
            print(f"Executing navigation to {goal.description} at ({goal.x}, {goal.y})")
            return self.navigation_callback(goal)
            
        except Exception as e:
            print(f"Error executing navigation: {e}")
            return False

    def _execute_communication(self, action) -> bool:
        """
        Execute communication action
        
        Args:
            action: The communication action to execute
            
        Returns:
            True if successful, False otherwise
        """
        if not self.communication_callback:
            print("Warning: No communication callback registered")
            return False
        
        try:
            params = action.parameters
            message = params.get('message', '')
            
            print(f"Communicating: {message}")
            return self.communication_callback(message)
            
        except Exception as e:
            print(f"Error executing communication: {e}")
            return False

    def start_system(self):
        """Start the voice navigation integration system"""
        if self.is_active:
            print("System already active")
            return
        
        self.is_active = True
        self.whisper.start_listening()
        print("Voice Navigation Integration System started")

    def stop_system(self):
        """Stop the voice navigation integration system"""
        self.is_active = False
        self.whisper.stop_listening()
        print("Voice Navigation Integration System stopped")

    def execute_direct_command(self, command_text: str) -> bool:
        """
        Execute a command directly without voice recognition
        
        Args:
            command_text: The command text to execute
            
        Returns:
            True if successful, False otherwise
        """
        print(f"Executing direct command: '{command_text}'")
        return self.planner.execute_command(command_text)


# Example usage with mock navigation system
class MockNavigationSystem:
    """Mock navigation system for demonstration"""
    
    def __init__(self):
        self.current_position = (0.0, 0.0)
        self.is_moving = False

    def navigate_to(self, goal: NavigationGoal) -> bool:
        """Mock navigation function"""
        if self.is_moving:
            print("Already moving, cannot start new navigation")
            return False

        print(f"Starting navigation to ({goal.x}, {goal.y}) in frame {goal.frame_id}")
        self.is_moving = True
        
        # Simulate navigation time
        distance = ((goal.x - self.current_position[0])**2 + 
                   (goal.y - self.current_position[1])**2)**0.5
        estimated_time = distance / 0.5  # Assuming 0.5 m/s speed
        
        print(f"Estimated time to goal: {estimated_time:.1f} seconds")
        
        # Update position
        self.current_position = (goal.x, goal.y)
        
        # Simulate movement
        time.sleep(min(estimated_time, 2.0))  # Cap simulation time
        
        print(f"Arrived at ({goal.x}, {goal.y})")
        self.is_moving = False
        return True

    def communicate(self, message: str) -> bool:
        """Mock communication function"""
        print(f"Robot says: {message}")
        return True


def main():
    """Example usage of the voice navigation integration system"""
    # Create mock navigation system
    nav_system = MockNavigationSystem()
    
    # Initialize the integration system
    try:
        integrator = VoiceNavigationIntegrator(whisper_model_size="base")
        
        # Register callbacks
        integrator.set_navigation_callback(nav_system.navigate_to)
        integrator.set_communication_callback(nav_system.communicate)
        
        print("Voice Navigation Integration System ready")
        print("Commands to try:")
        print("  - 'Go to the kitchen'")
        print("  - 'Move to the living room'")
        print("  - 'Hello robot'")
        print("\nType 'start' to begin voice recognition or 'quit' to exit:")
        
        while True:
            user_input = input("> ").strip().lower()
            
            if user_input == 'start':
                print("Starting voice recognition...")
                integrator.start_system()
                print("Voice recognition started. Speak to the robot!")
                print("Press Enter to stop voice recognition...")
                input()
                integrator.stop_system()
                
            elif user_input == 'direct':
                # Execute a direct command
                cmd = input("Enter command: ")
                if cmd:
                    integrator.execute_direct_command(cmd)
                    
            elif user_input.startswith('direct:'):
                # Execute a direct command from input
                cmd = user_input[7:].strip()  # Remove 'direct:' prefix
                if cmd:
                    integrator.execute_direct_command(cmd)
                    
            elif user_input == 'quit' or user_input == 'exit':
                print("Exiting...")
                break
                
            elif user_input == 'help':
                print("Commands:")
                print("  start  - Start voice recognition")
                print("  direct - Enter a direct command")
                print("  direct:<command> - Execute a command directly")
                print("  quit   - Exit the system")
                print("  help   - Show this help")
            else:
                print("Unknown command. Type 'help' for available commands.")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error running integration system: {e}")


# ROS node implementation (would be used in a real ROS environment)
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import PoseStamped
    from std_msgs.msg import String
    from ..setup.ros2_workspace import create_package  # Import ROS functionality
    
    class VoiceNavigationROSNode(Node):
        """
        ROS Node implementation of the voice navigation integration
        """
        
        def __init__(self):
            super().__init__('voice_navigation_integrator')
            
            # Initialize the integration system
            self.integrator = VoiceNavigationIntegrator()
            
            # Create publishers and subscribers
            self.nav_goal_pub = self.create_publisher(PoseStamped, 'goal_pose', 10)
            self.tts_pub = self.create_publisher(String, 'tts_input', 10)  # Text-to-speech
            
            # Register ROS callbacks
            self.integrator.set_navigation_callback(self._ros_navigation_callback)
            self.integrator.set_communication_callback(self._ros_communication_callback)
            
            # Start the system
            self.integrator.start_system()
            
            self.get_logger().info('Voice Navigation ROS Node initialized')

        def _ros_navigation_callback(self, goal) -> bool:
            """ROS callback for navigation goals"""
            try:
                # Create and publish navigation goal
                pose_msg = PoseStamped()
                pose_msg.header.frame_id = goal.frame_id
                pose_msg.header.stamp = self.get_clock().now().to_msg()
                pose_msg.pose.position.x = goal.x
                pose_msg.pose.position.y = goal.y
                pose_msg.pose.position.z = 0.0
                
                # Convert theta to quaternion (simplified)
                import math
                pose_msg.pose.orientation.z = math.sin(goal.theta / 2.0)
                pose_msg.pose.orientation.w = math.cos(goal.theta / 2.0)
                
                self.nav_goal_pub.publish(pose_msg)
                self.get_logger().info(f'Published navigation goal to ({goal.x}, {goal.y})')
                return True
                
            except Exception as e:
                self.get_logger().error(f'Error in ROS navigation callback: {e}')
                return False

        def _ros_communication_callback(self, message: str) -> bool:
            """ROS callback for communication"""
            try:
                # Publish message for text-to-speech
                msg = String()
                msg.data = message
                self.tts_pub.publish(msg)
                self.get_logger().info(f'Published TTS message: {message}')
                return True
                
            except Exception as e:
                self.get_logger().error(f'Error in ROS communication callback: {e}')
                return False

        def destroy_node(self):
            """Cleanup when node is destroyed"""
            self.integrator.stop_system()
            super().destroy_node()

    def run_ros_node():
        """Run the ROS node version"""
        rclpy.init()
        node = VoiceNavigationROSNode()
        
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
    print("Voice Navigation Integration System")
    print("==================================")
    print("Choose mode:")
    print("1. Standalone demo")
    print("2. ROS node (if ROS is available)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        run_ros_node()
    else:
        main()