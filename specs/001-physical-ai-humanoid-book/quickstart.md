# Quickstart Guide: Physical AI & Humanoid Robotics Course Book

**Feature**: Physical AI & Humanoid Robotics Course Book
**Date**: 2025-12-11

## Getting Started with the Course

This guide will help you set up your environment to follow along with the Physical AI & Humanoid Robotics course book.

### Prerequisites

Before starting the course, ensure you have:

1. A computer with at least 8GB RAM (16GB recommended)
2. Ubuntu 22.04 LTS or equivalent Linux environment (through WSL2 on Windows or a VM)
3. Basic understanding of Python programming
4. Familiarity with command-line tools
5. Git installed on your system

### Environment Setup

1. **Install ROS 2 Humble Hawksbill**:
   ```bash
   # Add ROS 2 repository
   sudo apt update && sudo apt install -y curl gnupg lsb-release
   curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
   
   # Add the repository to your sources list
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
   
   # Install ROS 2 packages
   sudo apt update
   sudo apt install -y ros-humble-desktop ros-humble-ros-base
   sudo apt install -y python3-rosdep2 python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
   ```

2. **Initialize rosdep**:
   ```bash
   sudo rosdep init
   rosdep update
   ```

3. **Install Gazebo Garden**:
   ```bash
   # Install prerequisites
   sudo apt-get update
   sudo apt-get install lsb-release wget gnupg
   
   # Add Gazebo repository
   sudo wget -qO - https://packages.osrfoundation.org/gazebo.gpg | sudo gpg --dearmor -o /usr/share/keyrings/gazebo-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo.list > /dev/null
   
   # Install Gazebo
   sudo apt-get update
   sudo apt-get install gz-garden
   ```

4. **Install NVIDIA Isaac Sim** (if you have an NVIDIA GPU):
   - Visit https://developer.nvidia.com/isaac-sim and download the latest version
   - Follow the installation instructions for your platform
   - Ensure you have CUDA-compatible GPU and drivers installed

5. **Set up your ROS 2 workspace**:
   ```bash
   # Create workspace
   mkdir -p ~/physical_ai_ws/src
   cd ~/physical_ai_ws
   
   # Source ROS 2
   source /opt/ros/humble/setup.bash
   
   # Build workspace
   colcon build
   source install/setup.bash
   ```

### First Steps in the Course

1. **Read Part I: Introduction to Physical AI**
   - Understand the concept of embodied intelligence
   - Learn the relationship between digital brain and physical body
   - Explore real-world examples of physical AI applications

2. **Module 1: ROS 2 (Robotic Nervous System)**
   - Follow the tutorials on nodes, topics, and services
   - Practice with the rclpy integration
   - Create your first URDF for a humanoid robot

3. **Module 2: Digital Twin (Gazebo)**
   - Set up your first simulation environment
   - Learn about physics simulation parameters
   - Work with simulated sensors (LiDAR, IMU, depth cameras)

4. **Module 3: AI-Robot Brain (NVIDIA Isaac)**
   - Generate synthetic data using Isaac Sim
   - Implement Isaac ROS perception components
   - Configure Nav2 for humanoid navigation

5. **Module 4: Vision-Language-Action (VLA)**
   - Integrate Whisper for voice commands
   - Create an LLM-to-ROS action planning system

6. **Capstone Project**
   - Combine all modules into an autonomous humanoid
   - Implement voice command response
   - Add navigation, detection, and manipulation capabilities

### Verification Steps

To verify your setup is working correctly:

1. **Test ROS 2**:
   ```bash
   # Open a new terminal and source ROS 2
   source /opt/ros/humble/setup.bash
   
   # Run a simple test
   ros2 run demo_nodes_cpp talker
   ```
   
   In another terminal:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 run demo_nodes_py listener
   ```

2. **Test Gazebo**:
   ```bash
   gz sim
   ```

3. **Verify workspace setup**:
   ```bash
   cd ~/physical_ai_ws
   source install/setup.bash
   echo $ROS_PACKAGE_PATH
   ```

### Common Issues and Troubleshooting

1. **Package installation fails**: Ensure your package lists are updated (`sudo apt update`)
2. **Permission errors**: Ensure you're following all instructions correctly, including proper sourcing of setup files
3. **Simulation performance**: Ensure your system meets the minimum requirements, especially for GPU-intensive simulation tasks
4. **Python conflicts**: Always use `python3` and `pip3` to ensure compatibility with ROS 2

### Next Steps

After completing the setup:

1. Navigate to the course documentation hosted at: [GITHUB_PAGES_URL] (to be created during development)
2. Review the first chapter of Part I in the course material
3. Set up your development environment according to the detailed instructions in Module 1