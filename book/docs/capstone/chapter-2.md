# Chapter 2: Voice Command Implementation

## Overview

This chapter focuses on implementing the voice command processing system for our autonomous humanoid robot. We'll integrate OpenAI's Whisper for speech recognition with our ROS-based humanoid to enable natural language interaction. The implementation will include the complete pipeline from audio capture to action execution.

## Learning Objectives

By the end of this chapter, you will be able to:
- Implement a complete voice command processing pipeline
- Integrate Whisper with ROS for real-time speech recognition
- Design a voice command interpretation system
- Implement error handling and feedback for voice interactions
- Test and validate the voice command system

## Architecture of Voice Command System

The voice command system consists of several interconnected components:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VOICE COMMAND PROCESSING PIPELINE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────┐         │
│  │  Microphone │───▶│ Whisper Speech   │───▶│ Command Interpreter │         │
│  │  Audio      │    │  Recognition     │    │  (NLP & Planning)   │         │
│  │  Capture    │    │  (Transcription) │    │                     │         │
│  └─────────────┘    └──────────────────┘    └─────────────────────┘         │
│         │                       │                        │                  │
│         ▼                       ▼                        ▼                  │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────┐         │
│  │ Audio       │    │ Transcribed      │    │ Structured Action   │         │
│  │ Preprocess- │    │ Text Buffer      │    │ Plan                │         │
│  │  ing        │    │                  │    │                     │         │
│  └─────────────┘    └──────────────────┘    └─────────────────────┘         │
│                                                                             │
│         ┌─────────────────────────────────────────────────────────┐         │
│         │                    FEEDBACK LOOP                        │         │
│         │  ┌─────────────────┐    ┌─────────────────────────────┐ │         │
│         │  │ Voice Feedback  │◀───│ Action Execution Status     │ │         │
│         │  │ (Text-to-Speech)│    │ (ROS Action Results)        │ │         │
│         │  └─────────────────┘    └─────────────────────────────┘ │         │
│         └─────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Implementation Components

### 1. Audio Capture Node

This node captures audio from the microphone and publishes it to ROS topics for further processing.

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import AudioData
import pyaudio
import numpy as np
import threading
import queue


class AudioCaptureNode(Node):
    def __init__(self):
        super().__init__('audio_capture_node')

        # Audio parameters
        self.sample_rate = 16000  # Whisper works well at 16kHz
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1

        # Publisher for audio data
        self.audio_pub = self.create_publisher(AudioData, 'audio_input', 10)

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Audio data queue
        self.audio_queue = queue.Queue()

        # Start audio capture thread
        self.capture_thread = threading.Thread(target=self.capture_audio)
        self.capture_thread.daemon = True
        self.capture_thread.start()

        self.get_logger().info('Audio Capture Node initialized')

    def capture_audio(self):
        """Capture audio from microphone in a separate thread"""
        stream = self.audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        try:
            while rclpy.ok():
                # Read audio data from stream
                data = stream.read(self.chunk_size)
                
                # Create and publish AudioData message
                audio_msg = AudioData()
                audio_msg.data = data
                self.audio_pub.publish(audio_msg)
                
        except Exception as e:
            self.get_logger().error(f'Error in audio capture: {e}')
        finally:
            stream.stop_stream()
            stream.close()

    def destroy_node(self):
        """Cleanup when node is destroyed"""
        self.audio.terminate()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = AudioCaptureNode()

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

### 2. Whisper Processing Node

This node receives audio data and processes it with Whisper to convert speech to text.

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import AudioData
from std_msgs.msg import String
import whisper
import numpy as np
import torch


class WhisperProcessingNode(Node):
    def __init__(self):
        super().__init__('whisper_processing_node')

        # Initialize Whisper model (using base model for balance of speed and accuracy)
        self.get_logger().info('Loading Whisper model...')
        try:
            self.model = whisper.load_model("base")
            self.get_logger().info('Whisper model loaded successfully')
        except Exception as e:
            self.get_logger().error(f'Failed to load Whisper model: {e}')
            self.model = None

        # Publisher for transcribed text
        self.text_pub = self.create_publisher(String, 'transcribed_text', 10)

        # Subscriber for audio data
        self.audio_sub = self.create_subscription(
            AudioData,
            'audio_input',
            self.audio_callback,
            10
        )

        # Audio buffer to accumulate audio for better transcription
        self.audio_buffer = []
        self.buffer_max_size = 16000 * 5  # 5 seconds at 16kHz

        # Flag to control processing
        self.processing_enabled = True

        self.get_logger().info('Whisper Processing Node initialized')

    def audio_callback(self, msg):
        """Process incoming audio data with Whisper"""
        if not self.model or not self.processing_enabled:
            return

        try:
            # Convert AudioData to numpy array
            audio_data = np.frombuffer(msg.data, dtype=np.int16).astype(np.float32)
            audio_data = audio_data / 32768.0  # Normalize from int16 to float32

            # Add to buffer
            self.audio_buffer.extend(audio_data)

            # Check if buffer is full enough for processing
            if len(self.audio_buffer) >= self.buffer_max_size:
                self.process_audio_buffer()
        except Exception as e:
            self.get_logger().error(f'Error processing audio: {e}')

    def process_audio_buffer(self):
        """Process the accumulated audio buffer with Whisper"""
        if len(self.audio_buffer) == 0:
            return

        try:
            # Convert buffer to numpy array
            audio_array = np.array(self.audio_buffer)
            
            # Process with Whisper
            result = self.model.transcribe(audio_array)
            text = result['text'].strip()

            if text and len(text) > 2:  # Only publish meaningful text
                self.get_logger().info(f'Recognized: "{text}"')

                # Publish the recognized text
                text_msg = String()
                text_msg.data = text
                self.text_pub.publish(text_msg)

            # Clear buffer after processing
            self.audio_buffer = []

        except Exception as e:
            self.get_logger().error(f'Error in Whisper transcription: {e}')
            self.audio_buffer = []  # Clear buffer to avoid accumulating old data

    def destroy_node(self):
        """Cleanup when node is destroyed"""
        if hasattr(self, 'audio_buffer'):
            self.audio_buffer = []
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WhisperProcessingNode()

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

### 3. Command Interpretation Node

This node interprets the transcribed text and converts it into structured commands.

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from move_base_msgs.msg import MoveBaseGoal
import re
import json


class CommandInterpretationNode(Node):
    def __init__(self):
        super().__init__('command_interpretation_node')

        # Subscriber for transcribed text
        self.text_sub = self.create_subscription(
            String,
            'transcribed_text',
            self.text_callback,
            10
        )

        # Publishers for different types of commands
        self.nav_pub = self.create_publisher(MoveBaseGoal, 'move_base/goal', 10)
        self.action_pub = self.create_publisher(String, 'structured_commands', 10)
        self.feedback_pub = self.create_publisher(String, 'voice_feedback', 10)

        # Define command patterns
        self.command_patterns = {
            'navigation': [
                r'go to the (.+)',
                r'move to the (.+)',
                r'go to (.+)',
                r'walk to (.+)',
                r'travel to (.+)',
                r'move toward (.+)'
            ],
            'object_interaction': [
                r'pick up the (.+)',
                r'grab the (.+)',
                r'take the (.+)',
                r'get the (.+)',
                r'pick up (.+)',
                r'bring me the (.+)'
            ],
            'manipulation': [
                r'put (.+) in the (.+)',
                r'place (.+) on the (.+)',
                r'move (.+) to the (.+)',
                r'take (.+) and put it in the (.+)'
            ]
        }

        # Predefined locations in the environment
        self.locations = {
            'kitchen': {'x': 5.0, 'y': 3.0, 'theta': 0.0},
            'living room': {'x': 0.0, 'y': 0.0, 'theta': 0.0},
            'bedroom': {'x': -3.0, 'y': 4.0, 'theta': 0.0},
            'office': {'x': -2.0, 'y': -2.0, 'theta': 0.0},
            'table': {'x': 1.0, 'y': 2.0, 'theta': 0.0},
            'couch': {'x': 0.5, 'y': -1.0, 'theta': 0.0}
        }

        # Predefined objects in the environment
        self.objects = {
            'cup', 'book', 'ball', 'box', 'bottle', 'phone'
        }

        self.get_logger().info('Command Interpretation Node initialized')

    def text_callback(self, msg):
        """Process incoming transcribed text"""
        text = msg.data.lower().strip()

        self.get_logger().info(f'Processing command: "{text}"')

        # Provide feedback that command is received
        feedback_msg = String()
        feedback_msg.data = f'Processing command: {text}'
        self.feedback_pub.publish(feedback_msg)

        # Interpret the command
        interpretation_result = self.interpret_command(text)

        if interpretation_result:
            command_type, params = interpretation_result
            self.get_logger().info(f'Interpreted command: {command_type} with params {params}')

            # Publish structured command
            cmd_msg = String()
            cmd_msg.data = json.dumps({
                'type': command_type,
                'parameters': params
            })
            self.action_pub.publish(cmd_msg)

            # If it's a navigation command, publish goal pose
            if command_type == 'NAVIGATION':
                self.publish_navigation_goal(params)

            # Provide feedback about interpretation
            feedback_msg.data = f'Understood command: {text}'
            self.feedback_pub.publish(feedback_msg)
        else:
            self.get_logger().warn(f'Could not interpret command: "{text}"')
            feedback_msg.data = f'Sorry, I did not understand: {text}'
            self.feedback_pub.publish(feedback_msg)

    def interpret_command(self, text):
        """Interpret natural language command into structured action"""
        # Check navigation commands
        for pattern in self.command_patterns['navigation']:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                if location in self.locations:
                    return 'NAVIGATION', {'location': location, **self.locations[location]}
                else:
                    # Try to find the closest match or return location name as-is
                    return 'NAVIGATION', {'location': location}

        # Check object interaction commands
        for pattern in self.command_patterns['object_interaction']:
            match = re.search(pattern, text)
            if match:
                object_name = match.group(1).strip()
                if object_name in self.objects or 'any' in object_name:
                    return 'PICKUP', {'object': object_name}
                else:
                    # For unknown objects, we might use perception to find it
                    return 'PICKUP', {'object': object_name}

        # Check manipulation commands
        for pattern in self.command_patterns['manipulation']:
            match = re.search(pattern, text)
            if match:
                object_name = match.group(1).strip()
                destination = match.group(2).strip()
                return 'MANIPULATION', {'object': object_name, 'destination': destination}

        # If no specific pattern matches, return None
        return None

    def publish_navigation_goal(self, params):
        """Publish navigation goal for MoveBase"""
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = self.get_clock().now().to_msg()
        
        goal.target_pose.pose.position.x = params.get('x', 0.0)
        goal.target_pose.pose.position.y = params.get('y', 0.0)
        
        # Simple orientation setting (facing forward)
        goal.target_pose.pose.orientation.z = 0.0
        goal.target_pose.pose.orientation.w = 1.0

        self.nav_pub.publish(goal)


def main(args=None):
    rclpy.init(args=args)
    node = CommandInterpretationNode()

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

## Voice Command Pipeline Integration

The complete voice command pipeline is orchestrated by launching all nodes together:

```xml
<!-- launch/voice_command_system.launch.py -->
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
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
        )
    ])
```

## Performance Optimization

### 1. Whisper Model Selection
For real-time applications, consider using smaller Whisper models:
- `tiny` or `base` models for resource-constrained robots
- `distil-whisper` models for faster processing
- Quantized models for reduced memory usage

### 2. Audio Preprocessing
```python
def preprocess_audio(self, audio_data):
    """Apply noise reduction and preprocessing"""
    # Apply noise reduction (example using simple spectral gating)
    # In practice, use libraries like noisereduce
    processed_audio = audio_data  # Placeholder for actual processing
    
    # Voice activity detection to reduce unnecessary processing
    if self.detect_speech(processed_audio):
        return processed_audio
    else:
        return None  # No speech detected, return None to skip processing
```

### 3. Confidence Thresholding
```python
def transcribe_with_confidence(self, audio_array):
    """Transcribe audio and return with confidence estimate"""
    result = self.model.transcribe(audio_array)
    
    # Simple confidence heuristic (in practice, use more sophisticated methods)
    text = result['text']
    confidence = self.estimate_confidence(text)
    
    if confidence > 0.5:  # Threshold for accepting transcription
        return text
    else:
        return None  # Confidence too low, reject transcription
```

## Error Handling and Robustness

### 1. Network-Related Errors
```python
def call_whisper_with_retry(self, audio_data, max_retries=3):
    """Call Whisper with retry logic for network errors"""
    for attempt in range(max_retries):
        try:
            result = self.model.transcribe(audio_data)
            return result
        except Exception as e:
            self.get_logger().warn(f'Whisper call failed (attempt {attempt + 1}): {e}')
            if attempt == max_retries - 1:
                # Last attempt failed, return None or default response
                return None
            time.sleep(0.5)  # Wait before retrying
```

### 2. Audio Quality Issues
```python
def validate_audio_quality(self, audio_data):
    """Validate audio quality before processing"""
    # Check for minimum volume level
    max_amplitude = np.max(np.abs(audio_data))
    if max_amplitude < 0.01:  # Very quiet, likely just noise
        return False
    
    # Check for reasonable duration
    duration = len(audio_data) / self.sample_rate
    if duration < 0.5:  # Less than 0.5 seconds, might be noise
        return False
    
    return True
```

## Testing the Voice Command System

### 1. Unit Tests
```python
import unittest
from unittest.mock import Mock, patch

class TestCommandInterpretationNode(unittest.TestCase):
    def setUp(self):
        self.node = CommandInterpretationNode()
        
    def test_navigation_command(self):
        """Test that navigation commands are correctly interpreted"""
        text = "go to the kitchen"
        result = self.node.interpret_command(text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'NAVIGATION')
        self.assertEqual(result[1]['location'], 'kitchen')
        
    def test_unknown_command(self):
        """Test that unknown commands return None"""
        text = "dance like a robot"
        result = self.node.interpret_command(text)
        
        self.assertIsNone(result)
```

### 2. Integration Tests
```bash
# Test the full pipeline with recorded audio
ros2 launch physical_ai_examples voice_command_system.launch.py &

# Send test audio data
# (In practice, this would be done programmatically)
# Check that the system responds appropriately to various commands
# Verify that feedback is provided for both successful and unsuccessful commands
```

## Security Considerations

### 1. API Key Management
When using cloud-based LLMs for command interpretation:
- Store API keys securely, not in code
- Use environment variables or ROS parameters for configuration
- Implement rate limiting to prevent abuse

### 2. Input Validation
- Validate all user commands for safety before execution
- Implement command timeouts to prevent system lockup
- Include safety checks before executing actions

## Troubleshooting Common Issues

### 1. High Latency
- Use smaller Whisper models for faster processing
- Optimize audio buffer sizes
- Consider edge processing instead of cloud APIs

### 2. Low Recognition Accuracy
- Ensure good audio quality (minimize background noise)
- Use directional microphones when possible
- Fine-tune Whisper for specific vocabulary if needed

### 3. Memory Issues
- Monitor memory usage, especially with larger models
- Consider using models with reduced precision
- Implement proper cleanup of old audio data

## Summary

This chapter covered the implementation of the voice command processing system for our autonomous humanoid robot. We implemented a complete pipeline from audio capture to command interpretation, with considerations for performance, robustness, and integration with the rest of the robot system.

The next chapter will focus on implementing the navigation and manipulation capabilities that will execute the commands interpreted in this chapter.

## Exercises

1. Implement a voice activity detection system to reduce unnecessary processing.
2. Add confidence scoring to the Whisper transcription and filter low-confidence results.
3. Implement a custom vocabulary for better recognition of specific robot commands.
4. Create a testing framework that evaluates voice command accuracy with various audio conditions.
5. Design and implement a fallback mechanism when the voice recognition system fails.