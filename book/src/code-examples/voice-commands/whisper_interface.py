#!/usr/bin/env python3

"""
Whisper Voice Recognition Interface
This module provides an interface to OpenAI's Whisper model for voice recognition
in the Physical AI & Humanoid Robotics system.
"""

import os
import sys
import torch
import whisper
import numpy as np
import pyaudio
import queue
import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable, Any


@dataclass
class VoiceCommand:
    """Represents a recognized voice command"""
    text: str
    confidence: float
    timestamp: float
    raw_audio: Optional[np.ndarray] = None


class WhisperInterface:
    """
    Interface to OpenAI's Whisper model for real-time voice recognition
    """
    
    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        """
        Initialize the Whisper interface
        
        Args:
            model_size: Size of the Whisper model ('tiny', 'base', 'small', 'medium', 'large')
            device: Device to run the model on ('cpu', 'cuda', or None for auto)
        """
        self.model_size = model_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load the Whisper model
        self.get_logger_info(f"Loading Whisper model '{model_size}' on {self.device}...")
        try:
            self.model = whisper.load_model(model_size, device=self.device)
            self.get_logger_info("Whisper model loaded successfully")
        except Exception as e:
            self.get_logger_error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}") from e

        # Audio parameters
        self.sample_rate = 16000  # Whisper works best at 16kHz
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Audio processing queue
        self.audio_queue = queue.Queue()
        
        # Recognition settings
        self.recognition_callback: Optional[Callable[[VoiceCommand], None]] = None
        self.is_listening = False
        self.capture_thread: Optional[threading.Thread] = None
        
        # Buffer for accumulating audio for recognition
        self.audio_buffer = np.array([], dtype=np.float32)
        self.buffer_duration = 3.0  # Process audio every 3 seconds
        self.silence_threshold = 0.01  # Threshold for silence detection
        
        self.get_logger_info(f"Whisper Interface initialized on {self.device}")

    def get_logger_info(self, message: str):
        """Print info message - in a real implementation this would use ROS logging"""
        print(f"[INFO] {message}")

    def get_logger_error(self, message: str):
        """Print error message - in a real implementation this would use ROS logging"""
        print(f"[ERROR] {message}")

    def set_recognition_callback(self, callback: Callable[[VoiceCommand], None]):
        """
        Set the callback function to be called when a voice command is recognized
        
        Args:
            callback: Function to call with recognized VoiceCommand
        """
        self.recognition_callback = callback

    def start_listening(self):
        """Start capturing and processing audio"""
        if self.is_listening:
            self.get_logger_info("Already listening")
            return

        self.is_listening = True
        
        # Start audio capture thread
        self.capture_thread = threading.Thread(target=self._capture_audio, daemon=True)
        self.capture_thread.start()
        
        # Start audio processing thread
        processing_thread = threading.Thread(target=self._process_audio, daemon=True)
        processing_thread.start()
        
        self.get_logger_info("Started listening for voice commands")

    def stop_listening(self):
        """Stop capturing and processing audio"""
        self.is_listening = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        
        self.get_logger_info("Stopped listening for voice commands")

    def _capture_audio(self):
        """Capture audio from the microphone in a separate thread"""
        try:
            stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            while self.is_listening:
                # Read audio data from stream
                data = stream.read(self.chunk_size)
                
                # Convert to numpy array and normalize
                audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Put audio chunk in queue for processing
                self.audio_queue.put(audio_chunk)
                
        except Exception as e:
            self.get_logger_error(f"Error in audio capture: {e}")
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()

    def _process_audio(self):
        """Process accumulated audio and perform recognition"""
        while self.is_listening:
            try:
                # Accumulate audio from the queue
                while not self.audio_queue.empty():
                    chunk = self.audio_queue.get_nowait()
                    self.audio_buffer = np.concatenate([self.audio_buffer, chunk])
                
                # Check if we have enough audio to process
                required_samples = int(self.sample_rate * self.buffer_duration)
                if len(self.audio_buffer) >= required_samples:
                    # Process the accumulated audio
                    self._recognize_audio(self.audio_buffer)
                    # Clear the buffer after processing
                    self.audio_buffer = np.array([], dtype=np.float32)
                else:
                    # Wait a bit before checking again
                    time.sleep(0.1)
                    
            except queue.Empty:
                # Queue was empty, continue loop
                time.sleep(0.1)
            except Exception as e:
                self.get_logger_error(f"Error in audio processing: {e}")

    def _recognize_audio(self, audio_data: np.ndarray):
        """Recognize speech in the provided audio data using Whisper"""
        try:
            # Ensure audio is the right format for Whisper
            if len(audio_data) < 16000 * 0.1:  # Less than 0.1 seconds, probably just noise
                return

            # Check for silence before processing
            if np.max(np.abs(audio_data)) < self.silence_threshold:
                return  # Skip silent audio

            # Process with Whisper
            result = self.model.transcribe(audio_data, fp16=False)
            text = result['text'].strip()

            if text and len(text) > 2:  # Only process meaningful text
                # Calculate a simple confidence estimate
                confidence = self._estimate_confidence(text, result)
                
                # Create and return the voice command
                command = VoiceCommand(
                    text=text,
                    confidence=confidence,
                    timestamp=time.time(),
                    raw_audio=audio_data.copy()
                )
                
                self.get_logger_info(f"Recognized: '{text}' (confidence: {confidence:.2f})")
                
                # Call the recognition callback if set
                if self.recognition_callback:
                    try:
                        self.recognition_callback(command)
                    except Exception as e:
                        self.get_logger_error(f"Error in recognition callback: {e}")
                        
        except Exception as e:
            self.get_logger_error(f"Error in Whisper recognition: {e}")

    def _estimate_confidence(self, text: str, result: dict) -> float:
        """Estimate confidence in the recognition result"""
        # Simple heuristic for confidence estimation
        # In a real implementation, you might use more sophisticated methods
        
        # Length-based check
        if len(text.strip()) < 3:
            return 0.3
        
        # Check for common indicators of low confidence
        words = text.split()
        if any(len(word) == 1 and word.lower() not in ['a', 'i'] for word in words):
            return 0.4  # Likely contains unrecognized fragments
        
        # Check for repeated characters (often indicates recognition error)
        import re
        repeated_chars = re.findall(r'(.)\1{2,}', text.lower())
        if len(repeated_chars) > 1:  # Multiple instances of 3+ repeated characters
            return 0.3
        
        # Otherwise, return medium confidence
        # In a real implementation, Whisper could provide more sophisticated confidence metrics
        return 0.7

    def recognize_from_file(self, audio_file_path: str) -> VoiceCommand:
        """Recognize speech from an audio file"""
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            result = self.model.transcribe(audio_file_path)
            text = result['text'].strip()
            
            if text:
                confidence = self._estimate_confidence(text, result)
                
                command = VoiceCommand(
                    text=text,
                    confidence=confidence,
                    timestamp=time.time()
                )
                
                self.get_logger_info(f"Recognized from file: '{text}' (confidence: {confidence:.2f})")
                return command
            else:
                raise ValueError("No speech detected in audio file")
                
        except Exception as e:
            self.get_logger_error(f"Error recognizing from file: {e}")
            raise

    def __del__(self):
        """Cleanup when the interface is destroyed"""
        if hasattr(self, 'audio'):
            self.audio.terminate()


# Example usage
if __name__ == "__main__":
    def on_recognized_command(command: VoiceCommand):
        """Example callback function"""
        print(f"Heard command: '{command.text}' with confidence {command.confidence:.2f}")
        
        # Example: Process specific commands
        text_lower = command.text.lower()
        if "hello" in text_lower:
            print("Robot acknowledges greeting")
        elif "move" in text_lower or "go to" in text_lower:
            print("Processing navigation command")
        elif "pick up" in text_lower or "grab" in text_lower:
            print("Processing manipulation command")

    # Initialize the Whisper interface
    try:
        whisper_interface = WhisperInterface(model_size="base")
        whisper_interface.set_recognition_callback(on_recognized_command)
        
        print("Whisper interface ready. Starting to listen...")
        print("Say something for the robot to recognize. Press Ctrl+C to stop.")
        
        whisper_interface.start_listening()
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
            whisper_interface.stop_listening()
            
    except Exception as e:
        print(f"Error initializing Whisper interface: {e}")
        sys.exit(1)