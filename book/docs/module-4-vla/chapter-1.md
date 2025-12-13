# Chapter 1: Whisper Voice Commands

## Overview

OpenAI's Whisper is a state-of-the-art automatic speech recognition (ASR) system that can accurately transcribe speech to text. In this chapter, we'll explore how to integrate Whisper into our humanoid robot system to enable voice command recognition. This will allow our robots to receive and interpret natural language commands from users.

## Learning Objectives

By the end of this chapter, you will be able to:
- Set up and configure the Whisper speech recognition system
- Integrate Whisper with ROS 2 for real-time voice command processing
- Handle different Whisper models based on computational requirements
- Process and interpret transcribed commands
- Implement error handling for speech recognition failures

## Introduction to Whisper

Whisper is a transformer-based model that demonstrates a strong ability to generalize across different domains, accents, and technical language. Key features include:

- Multilingual speech recognition
- Robustness to background noise and accents
- Different model sizes for various computational constraints
- Ability to handle technical language with minimal fine-tuning

### Whisper Model Sizes
| Model | Parameters | Relative Speed | Size |
|-------|------------|----------------|------|
| tiny  | 39 M       | 32x            | 75 MB |
| base  | 74 M       | 16x            | 145 MB |
| small | 244 M      | 6x             | 465 MB |
| medium| 769 M      | 2x             | 1.5 GB |
| large | 1550 M     | 1x             | 3.0 GB |

For humanoid robots, the choice of model depends on computational resources and latency requirements.

## Installing and Setting up Whisper

### Prerequisites
```bash
pip install openai-whisper
# Or for GPU acceleration:
pip install openai-whisper[cuda]
```

### Basic Whisper Usage
```python
import whisper

# Load model
model = whisper.load_model("base")  # Choose model size

# Transcribe audio file
result = model.transcribe("audio.mp3")
print(result["text"])
```

## Integrating Whisper with ROS 2

### Voice Command Processing Node
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import AudioData
import whisper
import io
import numpy as np
import pyaudio
import wave
import threading
import time


class WhisperVoiceProcessor(Node):
    def __init__(self):
        super().__init__('whisper_voice_processor')
        
        # Initialize Whisper model (using base model for balance of speed and accuracy)
        self.get_logger().info('Loading Whisper model...')
        self.model = whisper.load_model("base")
        self.get_logger().info('Whisper model loaded successfully')
        
        # Publisher for processed commands
        self.command_pub = self.create_publisher(String, 'voice_commands', 10)
        
        # Subscriber for audio data
        self.audio_sub = self.create_subscription(
            AudioData,
            'audio_input',
            self.audio_callback,
            10
        )
        
        # Timer for continuous listening (if needed)
        self.listen_timer = self.create_timer(0.1, self.listen_callback)
        
        # Internal state
        self.audio_buffer = []
        self.is_listening = True
        self.min_audio_length = 1.0  # Minimum audio length in seconds
        
        self.get_logger().info('Whisper Voice Processor initialized')

    def audio_callback(self, msg):
        """Process incoming audio data"""
        # Convert AudioData to numpy array for Whisper
        audio_data = np.frombuffer(msg.data, dtype=np.int16)
        
        # Append to internal buffer
        self.audio_buffer.extend(audio_data)
        
        # Check if we have enough audio to process
        if self.should_process_audio():
            self.process_audio_buffer()

    def should_process_audio(self):
        """Determine if we have enough audio to process"""
        # Calculate current audio buffer length in seconds
        sample_rate = 16000  # Assuming 16kHz sample rate
        current_length = len(self.audio_buffer) / sample_rate
        return current_length >= self.min_audio_length

    def process_audio_buffer(self):
        """Process the accumulated audio buffer with Whisper"""
        if len(self.audio_buffer) == 0:
            return
            
        try:
            # Convert to float32 and normalize
            audio_array = np.array(self.audio_buffer, dtype=np.float32)
            audio_array /= 32768.0  # Normalize from int16 to float32
            
            # Process with Whisper
            result = self.model.transcribe(audio_array)
            text = result['text'].strip()
            
            if text:  # Only publish if we got meaningful text
                self.get_logger().info(f'Recognized: "{text}"')
                
                # Publish the recognized command
                cmd_msg = String()
                cmd_msg.data = text
                self.command_pub.publish(cmd_msg)
                
            # Clear buffer after processing
            self.audio_buffer = []
            
        except Exception as e:
            self.get_logger().error(f'Error processing audio with Whisper: {e}')
            # Clear buffer anyway to avoid accumulating old audio
            self.audio_buffer = []

    def listen_callback(self):
        """Periodic check for processing audio"""
        if self.should_process_audio():
            self.process_audio_buffer()

    def shutdown(self):
        """Clean shutdown of the node"""
        self.is_listening = False
        # Wait for any ongoing processes to complete
        time.sleep(0.1)


def main(args=None):
    rclpy.init(args=args)
    voice_processor = WhisperVoiceProcessor()
    
    try:
        rclpy.spin(voice_processor)
    except KeyboardInterrupt:
        voice_processor.get_logger().info('Shutting down Whisper Voice Processor...')
        voice_processor.shutdown()
    finally:
        voice_processor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Real-time Audio Capture Integration

For real-time applications, we often need to capture audio directly from a microphone:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import whisper
import pyaudio
import numpy as np
import threading
import queue


class RealtimeWhisperNode(Node):
    def __init__(self):
        super().__init__('realtime_whisper_node')
        
        # Initialize Whisper model
        self.get_logger().info('Loading Whisper model...')
        self.model = whisper.load_model("base")
        self.get_logger().info('Whisper model loaded successfully')
        
        # Publisher for recognized commands
        self.command_pub = self.create_publisher(String, 'recognized_commands', 10)
        
        # Audio parameters
        self.sample_rate = 16000
        self.chunk_size = 1024  # Number of audio frames per buffer
        self.audio_queue = queue.Queue()
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Start audio capture thread
        self.capture_thread = threading.Thread(target=self.capture_audio)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_audio_stream)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        self.get_logger().info('Realtime Whisper Node initialized')

    def capture_audio(self):
        """Capture audio from microphone in a separate thread"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        try:
            while rclpy.ok():
                # Read audio data from stream
                data = stream.read(self.chunk_size)
                # Convert to numpy array
                audio_array = np.frombuffer(data, dtype=np.int16)
                # Add to queue for processing
                self.audio_queue.put(audio_array)
        except Exception as e:
            self.get_logger().error(f'Error in audio capture: {e}')
        finally:
            stream.stop_stream()
            stream.close()

    def process_audio_stream(self):
        """Process audio stream and run Whisper"""
        accumulated_audio = np.array([], dtype=np.float32)
        silence_threshold = 0.01  # Threshold for silence detection
        max_buffer_length = self.sample_rate * 5  # 5 seconds max buffer
        
        while rclpy.ok():
            try:
                # Get audio chunk from queue
                if not self.audio_queue.empty():
                    chunk = self.audio_queue.get()
                    # Convert to float and normalize
                    chunk = chunk.astype(np.float32) / 32768.0
                    # Add to accumulated audio
                    accumulated_audio = np.concatenate([accumulated_audio, chunk])
                    
                    # Check if we have enough non-silent audio to process
                    if len(accumulated_audio) > self.sample_rate * 0.5:  # At least 0.5 seconds
                        # Check for speech activity (simplified)
                        if np.max(np.abs(accumulated_audio)) > silence_threshold:
                            # Check if buffer isn't too long
                            if len(accumulated_audio) < max_buffer_length:
                                continue  # Accumulate more
                            else:
                                # Process the accumulated audio
                                self.transcribe_audio(accumulated_audio)
                                # Reset for next segment
                                accumulated_audio = np.array([], dtype=np.float32)
                        else:
                            # Likely silence - process what we have if it's substantial
                            if len(accumulated_audio) > self.sample_rate * 1.0:  # At least 1 second
                                self.transcribe_audio(accumulated_audio)
                            # Reset for next segment
                            accumulated_audio = np.array([], dtype=np.float32)
                else:
                    # Small delay to prevent busy waiting
                    time.sleep(0.01)
                    
            except Exception as e:
                self.get_logger().error(f'Error in audio processing: {e}')
                accumulated_audio = np.array([], dtype=np.float32)

    def transcribe_audio(self, audio_data):
        """Transcribe audio using Whisper"""
        try:
            # Process with Whisper in a separate thread to avoid blocking
            # For simplicity, we'll call it directly here
            result = self.model.transcribe(audio_data)
            
            if result and result['text'].strip():
                # Log and publish the recognized text
                recognized_text = result['text'].strip()
                self.get_logger().info(f'Recognized: "{recognized_text}"')
                
                # Publish the command
                cmd_msg = String()
                cmd_msg.data = recognized_text
                self.command_pub.publish(cmd_msg)
                
        except Exception as e:
            self.get_logger().error(f'Error in Whisper transcription: {e}')

    def destroy_node(self):
        """Cleanup when node is destroyed"""
        self.audio.terminate()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = RealtimeWhisperNode()
    
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

## Command Interpretation and Validation

Once we receive transcribed text, we need to interpret and validate commands:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose
import re


class VoiceCommandInterpreter(Node):
    def __init__(self):
        super().__init__('voice_command_interpreter')
        
        # Subscriber for recognized text
        self.text_sub = self.create_subscription(
            String,
            'recognized_commands',
            self.text_callback,
            10
        )
        
        # Publisher for interpreted commands
        self.command_pub = self.create_publisher(String, 'interpreted_commands', 10)
        self.goal_pub = self.create_publisher(Pose, 'goal_pose', 10)
        
        # Define command patterns
        self.command_patterns = {
            'navigation': [
                r'go to the (.+)',
                r'move to the (.+)',
                r'go to (.+)',
                r'walk to (.+)'
            ],
            'object_interaction': [
                r'pick up the (.+)',
                r'grab the (.+)',
                r'take the (.+)',
                r'get the (.+)'
            ],
            'manipulation': [
                r'put (.+) in the (.+)',
                r'place (.+) on the (.+)',
                r'move (.+) to the (.+)'
            ]
        }
        
        self.location_keywords = {
            'kitchen': self.get_kitchen_pose(),
            'living room': self.get_living_room_pose(),
            'bedroom': self.get_bedroom_pose(),
            'office': self.get_office_pose(),
            'table': self.get_table_pose(),
            'couch': self.get_couch_pose()
        }
        
        self.get_logger().info('Voice Command Interpreter initialized')

    def text_callback(self, msg):
        """Process incoming text commands"""
        text = msg.data.lower()
        
        # Interpret the command
        interpreted = self.interpret_command(text)
        
        if interpreted:
            self.get_logger().info(f'Interpreted command: {interpreted}')
            
            # Publish interpreted command
            cmd_msg = String()
            cmd_msg.data = interpreted
            self.command_pub.publish(cmd_msg)
            
            # If it's a navigation command, also publish the goal
            if interpreted.startswith('NAVIGATE:'):
                location = interpreted.split(':', 1)[1]
                if location in self.location_keywords:
                    goal_pose = self.location_keywords[location]
                    self.goal_pub.publish(goal_pose)
        else:
            self.get_logger().warn(f'Could not interpret command: "{text}"')

    def interpret_command(self, text):
        """Interpret natural language command"""
        # Check navigation commands
        for pattern in self.command_patterns['navigation']:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                return f'NAVIGATE:{location}'
        
        # Check object interaction commands
        for pattern in self.command_patterns['object_interaction']:
            match = re.search(pattern, text)
            if match:
                object_name = match.group(1).strip()
                return f'PICK_UP:{object_name}'
        
        # Check manipulation commands
        for pattern in self.command_patterns['manipulation']:
            match = re.search(pattern, text)
            if match:
                object_name = match.group(1).strip()
                destination = match.group(2).strip()
                return f'PLACE:{object_name}:AT:{destination}'
        
        # If no pattern matches, return None
        return None

    # Placeholder methods for location poses - in a real implementation,
    # these would return actual Pose messages with coordinates
    def get_kitchen_pose(self):
        from geometry_msgs.msg import Pose
        pose = Pose()
        pose.position.x = 5.0
        pose.position.y = 3.0
        pose.position.z = 0.0
        pose.orientation.w = 1.0
        return pose

    def get_living_room_pose(self):
        from geometry_msgs.msg import Pose
        pose = Pose()
        pose.position.x = 0.0
        pose.position.y = 0.0
        pose.position.z = 0.0
        pose.orientation.w = 1.0
        return pose

    def get_bedroom_pose(self):
        from geometry_msgs.msg import Pose
        pose = Pose()
        pose.position.x = -3.0
        pose.position.y = 4.0
        pose.position.z = 0.0
        pose.orientation.w = 1.0
        return pose

    def get_office_pose(self):
        from geometry_msgs.msg import Pose
        pose = Pose()
        pose.position.x = -2.0
        pose.position.y = -2.0
        pose.position.z = 0.0
        pose.orientation.w = 1.0
        return pose

    def get_table_pose(self):
        from geometry_msgs.msg import Pose
        pose = Pose()
        pose.position.x = 1.0
        pose.position.y = 2.0
        pose.position.z = 0.0
        pose.orientation.w = 1.0
        return pose

    def get_couch_pose(self):
        from geometry_msgs.msg import Pose
        pose = Pose()
        pose.position.x = 0.5
        pose.position.y = -1.0
        pose.position.z = 0.0
        pose.orientation.w = 1.0
        return pose


def main(args=None):
    rclpy.init(args=args)
    interpreter = VoiceCommandInterpreter()
    
    try:
        rclpy.spin(interpreter)
    except KeyboardInterrupt:
        pass
    finally:
        interpreter.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Error Handling and Robustness

### Confidence Scoring and Validation
```python
def transcribe_with_confidence(self, audio_data):
    """Transcribe audio and estimate confidence"""
    # Whisper doesn't directly provide confidence scores
    # We can implement our own heuristic based on various factors
    
    result = self.model.transcribe(audio_data)
    text = result['text']
    
    # Simple confidence heuristic based on text characteristics
    # In a real implementation, you might use more sophisticated methods
    confidence = self.estimate_confidence(text, result)
    
    return text, confidence

def estimate_confidence(self, text, result):
    """Estimate confidence in the transcription"""
    # Check for common indicators of low confidence
    if not text.strip():
        return 0.0
    
    # Check for repeated characters (often indicates recognition error)
    import re
    repeated_chars = re.findall(r'(.)\1{2,}', text.lower())
    if len(repeated_chars) > 2:  # Too many repeated characters
        return 0.3
    
    # Simple length-based heuristic
    words = text.split()
    if len(words) < 2 or len(words) > 20:  # Too short or too long
        return 0.5
    
    # Otherwise, return medium confidence
    return 0.7
```

## Performance Optimization

For humanoid robots, it's important to optimize Whisper usage:

### 1. Model Selection
- Use smaller models (tiny, base) for real-time applications
- Consider using Distil-Whisper for faster processing
- For deployment, optimize models using ONNX or TensorRT

### 2. Audio Preprocessing
- Apply noise reduction before Whisper processing
- Use voice activity detection to only process actual speech
- Optimize audio format and sample rate

### 3. Batch Processing
- Process audio in chunks rather than continuously
- Use threading for non-blocking audio capture

## Testing and Validation

### Unit Testing
```python
import unittest
from unittest.mock import Mock, patch

class TestWhisperIntegration(unittest.TestCase):
    def setUp(self):
        # Mock the Whisper model to avoid actual model loading in tests
        self.node = WhisperVoiceProcessor()
        self.node.model = Mock()

    def test_audio_processing(self):
        # Test that audio gets processed correctly
        audio_data = np.random.randn(16000)  # 1 second of random audio
        self.node.model.transcribe.return_value = {"text": "test command"}
        
        # Process the audio
        self.node.audio_buffer = audio_data.tolist()
        self.node.process_audio_buffer()
        
        # Check that model was called
        self.node.model.transcribe.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

## Troubleshooting Common Issues

### 1. Audio Capture Issues
- Ensure microphone is properly configured
- Check audio format compatibility (16kHz recommended)
- Verify audio permissions for the application

### 2. Performance Issues
- Monitor CPU usage - Whisper can be computationally intensive
- Consider using GPU acceleration if available
- Use appropriate model size for your hardware

### 3. Recognition Accuracy
- Ensure good audio quality (minimal background noise)
- Consider fine-tuning Whisper for domain-specific vocabulary
- Implement voice activity detection to avoid processing silence

## Summary

In this chapter, we've covered the integration of OpenAI's Whisper with our humanoid robot system for voice command recognition. We've implemented real-time audio processing, command interpretation, and error handling. The next chapter will cover how to translate these voice commands into robotic actions using LLMs.

## Exercises

1. Implement a Whisper node that can distinguish between different speakers.
2. Add confidence scoring to your voice command recognition system.
3. Integrate voice activity detection to reduce unnecessary processing.
4. Create a system that can handle multiple consecutive voice commands.
5. Implement a voice command system that works with custom vocabulary specific to your robot's environment.