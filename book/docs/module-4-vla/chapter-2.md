# Chapter 2: LLM-to-ROS Action Planning

## Overview

Large Language Models (LLMs) provide powerful capabilities for understanding natural language and generating structured plans. In this chapter, we'll explore how to connect LLMs with ROS (Robot Operating System) to translate high-level natural language commands into specific robotic actions. This connection enables humanoid robots to understand complex tasks and execute them in real-world environments.

## Learning Objectives

By the end of this chapter, you will be able to:
- Connect LLMs with ROS for action planning
- Parse natural language commands into executable robot actions
- Implement safety checks and validation for LLM-generated commands
- Create a robust pipeline for converting language to robotic behavior
- Handle ambiguous or complex language commands with error recovery

## Introduction to LLM-ROS Integration

The integration of LLMs with ROS involves several key components:

1. **Command Understanding**: Interpreting natural language requests
2. **Action Decomposition**: Breaking complex tasks into simpler, executable actions
3. **ROS Command Generation**: Creating specific ROS messages and service calls
4. **Execution Monitoring**: Tracking progress and adapting to changes
5. **Error Recovery**: Handling failed or ambiguous commands

### Architecture Overview
```
Natural Language Command
         ↓
   LLM Parser & Planner
         ↓
   Action Decomposition
         ↓
   ROS Message Generator
         ↓
   ROS Action Execution
         ↓
   Feedback & Monitoring
```

## Setting up LLM Integration

### Prerequisites
```bash
pip install openai  # For OpenAI API
# OR
pip install transformers torch  # For local models like BERT, GPT
```

### Basic LLM Node Structure
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from actionlib_msgs.msg import GoalStatusArray
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import openai
import json


class LLMActionPlanner(Node):
    def __init__(self):
        super().__init__('llm_action_planner')
        
        # Initialize OpenAI client (in real implementation, use proper API key handling)
        # openai.api_key = "your-api-key-here"
        
        # Publishers and subscribers
        self.command_sub = self.create_subscription(
            String,
            'interpreted_commands',
            self.command_callback,
            10
        )
        
        self.status_pub = self.create_publisher(String, 'action_status', 10)
        self.goal_pub = self.create_publisher(Pose, 'goal_pose', 10)
        
        # Action client for navigation (example)
        # self.nav_client = ActionClient(self, MoveBaseAction, 'move_base')
        
        # Robot capabilities and map of locations
        self.robot_capabilities = {
            'navigation': True,
            'manipulation': True,
            'object_recognition': True
        }
        
        self.location_map = {
            'kitchen': {'x': 5.0, 'y': 3.0, 'theta': 0.0},
            'living_room': {'x': 0.0, 'y': 0.0, 'theta': 0.0},
            'bedroom': {'x': -3.0, 'y': 4.0, 'theta': 0.0},
            'office': {'x': -2.0, 'y': -2.0, 'theta': 0.0}
        }
        
        self.get_logger().info('LLM Action Planner initialized')

    def command_callback(self, msg):
        """Process incoming command messages"""
        command = msg.data
        
        self.get_logger().info(f'Received command: {command}')
        
        # Process command through LLM
        action_plan = self.plan_action(command)
        
        if action_plan:
            self.execute_plan(action_plan)
        else:
            self.get_logger().error(f'Could not generate plan for command: {command}')

    def plan_action(self, command):
        """Generate action plan using LLM"""
        try:
            # This is a simplified example. In practice, you would use
            # proper LLM calls with structured prompts
            plan = self.generate_structured_plan(command)
            return plan
        except Exception as e:
            self.get_logger().error(f'Error in LLM planning: {e}')
            return None

    def generate_structured_plan(self, command):
        """Generate structured plan from natural language command"""
        # For this example, we'll create a simple rule-based planner
        # In a real implementation, this would call an LLM API
        
        # Convert command to a structured plan
        if command.startswith('NAVIGATE:'):
            location = command.split(':', 1)[1]
            return self.create_navigation_plan(location)
        elif command.startswith('PICK_UP:'):
            object_name = command.split(':', 1)[1]
            return self.create_pickup_plan(object_name)
        elif command.startswith('PLACE:'):
            parts = command.split(':')
            object_name = parts[1]
            destination = parts[3]  # PLACE:object:AT:destination
            return self.create_placement_plan(object_name, destination)
        
        # If no specific pattern matched, we might use an actual LLM
        return self.call_llm_for_planning(command)

    def call_llm_for_planning(self, command):
        """Call actual LLM for complex planning"""
        # Example using OpenAI API
        prompt = f"""
        You are a robot action planner. Convert the following natural language command 
        into a sequence of robot actions. Return the response as JSON with the following structure:
        
        {{
            "actions": [
                {{
                    "type": "navigation|pickup|place|wait|custom",
                    "parameters": {{"location": "string", "object": "string", ...}}
                }}
            ]
        }}
        
        Command: {command}
        """
        
        try:
            # For demonstration, returning a mock response
            # In real implementation: response = openai.ChatCompletion.create(...)
            
            # Mock response for demonstration
            if 'go to' in command:
                location = command.split('go to')[-1].strip()
                return {
                    "actions": [
                        {
                            "type": "navigation",
                            "parameters": {"location": location}
                        }
                    ]
                }
            elif 'pick up' in command:
                obj = command.split('pick up')[-1].strip()
                return {
                    "actions": [
                        {
                            "type": "navigation",
                            "parameters": {"location": "object_location"}
                        },
                        {
                            "type": "pickup",
                            "parameters": {"object": obj}
                        }
                    ]
                }
            else:
                return {"actions": []}
                
        except Exception as e:
            self.get_logger().error(f'Error calling LLM: {e}')
            return {"actions": []}

    def create_navigation_plan(self, location):
        """Create a navigation plan for a given location"""
        if location in self.location_map:
            return {
                "actions": [
                    {
                        "type": "navigation",
                        "parameters": {
                            "x": self.location_map[location]['x'],
                            "y": self.location_map[location]['y'],
                            "theta": self.location_map[location]['theta']
                        }
                    }
                ]
            }
        else:
            self.get_logger().warn(f'Unknown location: {location}')
            return {"actions": []}

    def create_pickup_plan(self, object_name):
        """Create a pickup plan for a given object"""
        # In a real implementation, this would involve object detection
        # to find the actual location of the object
        return {
            "actions": [
                {
                    "type": "navigation",
                    "parameters": {"location": "object_location"}
                },
                {
                    "type": "pickup",
                    "parameters": {"object": object_name}
                }
            ]
        }

    def create_placement_plan(self, object_name, destination):
        """Create a placement plan"""
        return {
            "actions": [
                {
                    "type": "navigation",
                    "parameters": {"location": destination}
                },
                {
                    "type": "place",
                    "parameters": {"object": object_name}
                }
            ]
        }

    def execute_plan(self, plan):
        """Execute the generated action plan"""
        for action in plan.get('actions', []):
            action_type = action['type']
            parameters = action['parameters']
            
            self.get_logger().info(f'Executing {action_type} with parameters: {parameters}')
            
            if action_type == 'navigation':
                self.execute_navigation(parameters)
            elif action_type == 'pickup':
                self.execute_pickup(parameters)
            elif action_type == 'place':
                self.execute_placement(parameters)
            elif action_type == 'wait':
                self.execute_wait(parameters)
            else:
                self.get_logger().warn(f'Unknown action type: {action_type}')

    def execute_navigation(self, params):
        """Execute navigation action"""
        # Create and publish goal pose
        goal_pose = Pose()
        if 'location' in params and params['location'] in self.location_map:
            loc = self.location_map[params['location']]
            goal_pose.position.x = loc['x']
            goal_pose.position.y = loc['y']
            # Simple orientation setting (face forward)
            goal_pose.orientation.z = 0.0
            goal_pose.orientation.w = 1.0
        elif 'x' in params and 'y' in params:
            goal_pose.position.x = params['x']
            goal_pose.position.y = params['y']
            goal_pose.orientation.w = 1.0
        else:
            self.get_logger().error('Invalid navigation parameters')
            return
        
        self.goal_pub.publish(goal_pose)
        
        # Publish status
        status_msg = String()
        status_msg.data = f'Navigating to {params}'
        self.status_pub.publish(status_msg)

    def execute_pickup(self, params):
        """Execute pickup action"""
        # In a real implementation, this would call manipulation services
        obj_name = params.get('object', 'unknown')
        
        status_msg = String()
        status_msg.data = f'Attempting to pickup {obj_name}'
        self.status_pub.publish(status_msg)
        
        # Placeholder for actual pickup logic
        self.get_logger().info(f'Pickup action for {obj_name} not yet implemented')

    def execute_placement(self, params):
        """Execute placement action"""
        # In a real implementation, this would call manipulation services
        obj_name = params.get('object', 'unknown')
        
        status_msg = String()
        status_msg.data = f'Attempting to place {obj_name}'
        self.status_pub.publish(status_msg)
        
        # Placeholder for actual placement logic
        self.get_logger().info(f'Placement action for {obj_name} not yet implemented')

    def execute_wait(self, params):
        """Execute wait action"""
        duration = params.get('duration', 1.0)  # Default 1 second wait
        
        status_msg = String()
        status_msg.data = f'Waiting for {duration} seconds'
        self.status_pub.publish(status_msg)
        
        # In a real implementation, use a timer instead of blocking sleep
        import time
        time.sleep(duration)


def main(args=None):
    rclpy.init(args=args)
    planner = LLMActionPlanner()
    
    try:
        rclpy.spin(planner)
    except KeyboardInterrupt:
        pass
    finally:
        planner.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Advanced Planning with LLMs

### Context-Aware Planning
```python
class ContextAwarePlanner(Node):
    def __init__(self):
        super().__init__('context_aware_planner')
        
        # Maintain context about the environment and ongoing tasks
        self.current_context = {
            'robot_position': {'x': 0.0, 'y': 0.0},
            'detected_objects': [],
            'current_task': None,
            'task_history': []
        }
        
        # Subscribe to relevant topics for context updates
        self.position_sub = self.create_subscription(
            Pose,
            'robot_pose',
            self.position_callback,
            10
        )
        
        self.objects_sub = self.create_subscription(
            String,
            'detected_objects',
            self.objects_callback,
            10
        )

    def position_callback(self, msg):
        """Update robot position context"""
        self.current_context['robot_position'] = {
            'x': msg.position.x,
            'y': msg.position.y
        }

    def objects_callback(self, msg):
        """Update detected objects context"""
        import json
        try:
            objects = json.loads(msg.data)
            self.current_context['detected_objects'] = objects
        except json.JSONDecodeError:
            self.get_logger().warn('Invalid detected objects message')

    def generate_contextual_plan(self, command):
        """Generate plan with environmental context"""
        context_description = self.format_context_for_llm()
        
        prompt = f"""
        Context: {context_description}
        
        Command: {command}
        
        Generate a detailed action plan considering the current environment.
        Respond in JSON format with structured actions.
        """
        
        # Call LLM with context
        return self.call_llm(prompt)
```

### Handling Ambiguity
```python
def handle_ambiguous_command(self, command):
    """Handle commands that may need clarification"""
    # Check if command is ambiguous
    if self.is_ambiguous(command):
        # Generate possible interpretations
        interpretations = self.generate_interpretations(command)
        
        # If we can disambiguate based on context
        disambiguated = self.disambiguate_with_context(interpretations)
        
        if disambiguated:
            return self.generate_plan_for_interpretation(disambiguated)
        else:
            # Request clarification from user
            clarification_request = self.generate_clarification_request(interpretations)
            self.request_clarification(clarification_request)
            return None
    
    # If not ambiguous, proceed normally
    return self.generate_structured_plan(command)

def is_ambiguous(self, command):
    """Check if command is ambiguous"""
    # Example ambiguous phrases
    ambiguous_indicators = [
        'it', 'there', 'that', 'the one', 'over there'
    ]
    
    command_lower = command.lower()
    return any(indicator in command_lower for indicator in ambiguous_indicators)

def generate_interpretations(self, command):
    """Generate possible interpretations of an ambiguous command"""
    # In a real implementation, this would use the LLM to generate interpretations
    # based on context and possible meanings
    
    # For example, if command is "Go there", possible interpretations might be:
    # - Go to the detected kitchen
    # - Go to the detected living room
    # - Go to the last mentioned location
    
    return []  # Placeholder
```

## Safety and Validation

### Safety Checks for LLM-Generated Commands
```python
class SafeLLMPlanner(Node):
    def __init__(self):
        super().__init__('safe_llm_planner')
        
        # Define safety constraints
        self.safety_constraints = {
            'forbidden_locations': ['restricted_area', 'danger_zone'],
            'valid_objects': ['cup', 'book', 'ball', 'box'],  # Define what robot can manipulate
            'max_navigation_distance': 20.0,  # Max distance robot can navigate
            'valid_actions': ['navigation', 'pickup', 'place', 'wait']
        }

    def validate_plan(self, plan):
        """Validate that the plan is safe and feasible"""
        for action in plan.get('actions', []):
            if not self.is_action_safe(action):
                self.get_logger().error(f'Safe action validation failed: {action}')
                return False
        
        return True

    def is_action_safe(self, action):
        """Check if individual action is safe"""
        action_type = action['type']
        params = action['parameters']
        
        # Check if action type is valid
        if action_type not in self.safety_constraints['valid_actions']:
            return False
        
        # Check location safety for navigation
        if action_type == 'navigation':
            location = params.get('location')
            if location in self.safety_constraints['forbidden_locations']:
                return False
            
            # Check distance if coordinates provided
            if 'x' in params and 'y' in params:
                current_pos = self.current_context['robot_position']
                distance = ((params['x'] - current_pos['x'])**2 + 
                           (params['y'] - current_pos['y'])**2)**0.5
                if distance > self.safety_constraints['max_navigation_distance']:
                    return False
        
        # Check object safety for manipulation
        elif action_type in ['pickup', 'place']:
            obj_name = params.get('object', '').lower()
            if obj_name not in self.safety_constraints['valid_objects']:
                return False
        
        return True
```

## Error Recovery and Adaptation

### Handling Plan Failures
```python
class AdaptivePlanner(LLMActionPlanner):
    def __init__(self):
        super().__init__()
        
        # Subscribe to feedback from action execution
        self.feedback_sub = self.create_subscription(
            String,
            'action_feedback',
            self.feedback_callback,
            10
        )
        
        self.current_plan = None
        self.current_action_index = 0

    def feedback_callback(self, msg):
        """Handle feedback from action execution"""
        feedback = msg.data
        
        if feedback.startswith('SUCCESS:'):
            self.handle_action_success()
        elif feedback.startswith('FAILURE:'):
            self.handle_action_failure(feedback)
        elif feedback.startswith('PROGRESS:'):
            self.handle_action_progress(feedback)

    def handle_action_failure(self, feedback):
        """Handle when an action fails"""
        self.get_logger().warn(f'Action failed: {feedback}')
        
        # Determine appropriate recovery strategy
        if self.current_plan and self.current_action_index < len(self.current_plan.get('actions', [])):
            failed_action = self.current_plan['actions'][self.current_action_index]
            
            # Try alternative approach
            recovery_plan = self.generate_recovery_plan(failed_action, feedback)
            
            if recovery_plan:
                self.execute_plan(recovery_plan)
            else:
                # If no recovery possible, abandon current plan
                self.get_logger().error('No recovery possible, abandoning plan')
                self.current_plan = None

    def generate_recovery_plan(self, failed_action, failure_cause):
        """Generate a plan to recover from failed action"""
        # Based on the type of failure and action, generate recovery
        action_type = failed_action['type']
        
        if action_type == 'navigation':
            # Try alternative route or approach
            return self.generate_alternative_navigation(failed_action)
        elif action_type == 'pickup':
            # Try different grasp approach or look for alternative object
            return self.generate_alternative_pickup(failed_action)
        else:
            # For other actions, consider retry or alternative
            return self.generate_retry_plan(failed_action)

    def generate_alternative_navigation(self, failed_action):
        """Generate alternative navigation plan"""
        # This would implement path planning algorithms
        # to find alternative routes around obstacles
        return {
            "actions": [
                {
                    "type": "navigation",
                    "parameters": failed_action['parameters']  # Same destination but different route
                }
            ]
        }
```

## Performance Optimization

### Caching and Pre-planning
```python
class OptimizedLLMPlanner(LLMActionPlanner):
    def __init__(self):
        super().__init__()
        
        # Cache for common command patterns
        self.plan_cache = {}
        self.max_cache_size = 100
        
        # Pre-computed maps for common locations
        self.precomputed_paths = {}
        
    def plan_action(self, command):
        """Plan action with caching"""
        # Check cache first
        if command in self.plan_cache:
            self.get_logger().info('Retrieved plan from cache')
            return self.plan_cache[command]
        
        # Generate new plan
        plan = self.generate_structured_plan(command)
        
        # Cache the plan if it's not too large
        if len(self.plan_cache) < self.max_cache_size and plan:
            self.plan_cache[command] = plan
            
        return plan
```

## Testing and Validation

### Unit Tests for LLM Integration
```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from std_msgs.msg import String


class TestLLMActionPlanner(unittest.TestCase):
    def setUp(self):
        # Create a mock node for testing
        self.node = LLMActionPlanner()
        # Mock the OpenAI API call
        self.node.call_llm = Mock()

    def test_navigation_command(self):
        """Test that navigation commands are processed correctly"""
        command = "NAVIGATE:kitchen"
        
        # Mock the planning result
        expected_plan = {
            "actions": [
                {
                    "type": "navigation",
                    "parameters": {"location": "kitchen"}
                }
            ]
        }
        self.node.call_llm.return_value = expected_plan
        
        # Call the plan_action method
        result = self.node.plan_action(command)
        
        # Verify the result
        self.assertEqual(result, expected_plan)
        self.node.call_llm.assert_called_once()

    def test_invalid_command(self):
        """Test handling of invalid commands"""
        command = "INVALID_COMMAND:unknown_action"
        
        # Mock to return no actions
        self.node.call_llm.return_value = {"actions": []}
        
        # Call the plan_action method
        result = self.node.plan_action(command)
        
        # Verify we get a plan with no actions
        self.assertEqual(result["actions"], [])


if __name__ == '__main__':
    # Initialize ROS context for testing
    rclpy.init()
    unittest.main()
    rclpy.shutdown()
```

## Real-World Considerations

### Handling Network Failures
```python
import time
from functools import wraps


def retry_on_failure(max_attempts=3, delay=1.0):
    """Decorator to retry LLM calls on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:  # Last attempt
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


class RobustLLMPlanner(LLMActionPlanner):
    @retry_on_failure(max_attempts=3, delay=2.0)
    def call_llm(self, prompt):
        """Call LLM with retry logic"""
        # Actual LLM call here
        # response = openai.ChatCompletion.create(...)
        pass
```

## Troubleshooting Common Issues

### 1. LLM API Issues
- Ensure API keys are correctly configured
- Check rate limits and billing
- Implement proper error handling and retry logic

### 2. Plan Generation Issues
- Verify prompts are well-structured
- Check that LLM responses are properly parsed
- Implement validation for generated plans

### 3. Execution Issues
- Monitor action execution feedback
- Implement proper state tracking
- Handle concurrent action execution

## Summary

LLM-to-ROS action planning enables humanoid robots to understand and execute complex natural language commands. By connecting LLMs with ROS, we can create robots that interpret human instructions and translate them into specific robotic behaviors. This chapter covered the implementation of a complete pipeline from language understanding to action execution, including safety considerations and error recovery.

## Exercises

1. Implement a safety checker that validates LLM-generated plans before execution.
2. Create an adaptive planner that learns from action failures to improve future plans.
3. Develop a context-aware system that considers environmental information when generating plans.
4. Implement a multi-step planning system that breaks complex tasks into manageable subtasks.
5. Design a system for handling ambiguous commands with user clarification requests.