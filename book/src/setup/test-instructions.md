# ROS 2 Setup Testing Instructions

This document provides step-by-step instructions for testing your ROS 2 setup to ensure that the Physical AI & Humanoid Robotics course environment is properly configured.

## Prerequisites

Before starting these tests, ensure you have:
1. A computer with at least 8GB RAM (16GB recommended)
2. Ubuntu 22.04 LTS or equivalent Linux environment (through WSL2 on Windows or a VM)
3. ROS 2 Humble Hawksbill properly installed
4. Git installed on your system
5. Completed the workspace setup using the `ros2-workspace.py` script

## Test 1: Basic ROS 2 Installation Verification

### Objective
Verify that ROS 2 is properly installed and accessible from the command line.

### Steps
1. Open a new terminal
2. Run the following command to check ROS 2 version:
   ```bash
   ros2 --version
   ```
3. Expected result: Shows the version of ROS 2 installed (e.g., `ros2 version 0.23.0`)

### Troubleshooting
- If the command is not found, ensure ROS 2 is sourced: `source /opt/ros/humble/setup.bash`
- If you get permission errors, check that ROS 2 was installed correctly

## Test 2: Environment Variables

### Objective
Verify that required ROS 2 environment variables are set.

### Steps
1. Check the ROS distribution:
   ```bash
   echo $ROS_DISTRO
   ```
2. Expected result: Shows `humble` (or the installed distribution)

3. Check the ROS package path:
   ```bash
   echo $ROS_PACKAGE_PATH
   ```
4. Expected result: Shows paths to ROS 2 installation directories

### Troubleshooting
- If variables are not set, source ROS 2: `source /opt/ros/humble/setup.bash`

## Test 3: Basic Publisher/Subscriber Communication

### Objective
Test basic ROS 2 communication between nodes.

### Steps
1. Open a new terminal and source ROS 2:
   ```bash
   source /opt/ros/humble/setup.bash
   ```
2. Run the ROS 2 demo talker node:
   ```bash
   ros2 run demo_nodes_cpp talker
   ```

3. In another terminal, source ROS 2 and run the listener node:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 run demo_nodes_py listener
   ```

4. Expected result: The listener terminal should show messages being received from the talker

### Troubleshooting
- If nodes can't communicate, check that both terminals have ROS environment sourced
- Ensure no firewall is blocking ROS 2 communication

## Test 4: Workspace Build and Source

### Objective
Verify that your workspace was built correctly and can be sourced.

### Steps
1. Navigate to the workspace directory (typically `~/physical_ai_ws`):
   ```bash
   cd ~/physical_ai_ws
   ```

2. Source the workspace:
   ```bash
   source install/setup.bash
   ```

3. Check that the workspace is in the package path:
   ```bash
   echo $ROS_PACKAGE_PATH
   ```
4. Expected result: The workspace path should appear at the beginning of the list

5. List packages in the workspace:
   ```bash
   ros2 pkg list | grep physical_ai
   ```
6. Expected result: Shows the package created during workspace setup

## Test 5: Python Package Functionality

### Objective
Test that ROS 2 Python packages can be executed.

### Steps
1. In the workspace directory, verify Python setup:
   ```bash
   python3 -c "import rclpy; print('rclpy imported successfully')"
   ```
2. Expected result: "rclpy imported successfully"

3. Check if you can create a minimal ROS 2 Python node:
   ```bash
   python3 -c "
   import rclpy
   rclpy.init()
   node = rclpy.create_node('test_node')
   print('ROS 2 Python node created successfully')
   node.destroy_node()
   rclpy.shutdown()
   "
   ```
4. Expected result: "ROS 2 Python node created successfully"

## Test 6: Gazebo Integration (If Installed)

### Objective
Verify Gazebo simulation environment is working with ROS 2.

### Steps
1. Open a new terminal and source ROS 2:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. Launch Gazebo with ROS 2 integration:
   ```bash
   gz sim
   ```
3. Expected result: Gazebo simulation environment starts without errors

4. In another terminal, check available Gazebo services:
   ```bash
   gz service --list
   ```
5. Expected result: List of available Gazebo services appears

### Troubleshooting
- If Gazebo fails to start, ensure it's properly installed: `sudo apt install gz-garden`
- Check graphics drivers are properly configured for simulation

## Test 7: Course-Specific Package Verification

### Objective
Verify that the course-specific packages are properly built and accessible.

### Steps
1. Navigate to your workspace:
   ```bash
   cd ~/physical_ai_ws
   ```

2. Source both ROS 2 and your workspace:
   ```bash
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ```

3. Try to run a basic command to check if your custom packages work:
   ```bash
   ros2 pkg list
   ```
4. Expected result: Your workspace packages appear in the list

5. Test that the workspace setup script works:
   ```bash
   # Navigate to your workspace
   cd ~/physical_ai_ws
   # Try the generated setup script (if created)
   ./setup_workspace.sh
   ```

## Test 8: Code Example Execution

### Objective
Verify that basic code examples from the course can be executed.

### Steps
1. Navigate to your workspace and source the environment:
   ```bash
   cd ~/physical_ai_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ```

2. Create a minimal publisher example to test functionality:
   ```bash
   # Create a test directory
   mkdir -p test_examples
   cd test_examples
   
   # Create a simple Python publisher
   cat > simple_publisher.py << 'EOF'
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SimplePublisher(Node):
    def __init__(self):
        super().__init__('simple_publisher')
        self.publisher_ = self.create_publisher(String, 'test_topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    simple_publisher = SimplePublisher()
    rclpy.spin(simple_publisher)
    simple_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
EOF
   
   # Make it executable
   chmod +x simple_publisher.py
   
   # Run with Python (in the background)
   python3 simple_publisher.py &
   PUBLISHER_PID=$!
   
   # Check if it's working by listening for messages
   timeout 5 ros2 topic echo /test_topic std_msgs/msg/String
   
   # Clean up
   kill $PUBLISHER_PID 2>/dev/null || true
   cd .. && rm -rf test_examples
   ```

3. Expected result: The publisher should run and you should see messages published to `/test_topic`

## Final Verification

### Objective
Run all tests to ensure the complete setup is working.

### Steps
1. Create a simple script that runs all basic verifications:
   ```bash
   #!/bin/bash
   
   echo "=== ROS 2 Setup Verification ==="
   
   # Test 1: Check ROS 2 installation
   echo -n "1. Checking ROS 2 installation... "
   if command -v ros2 &> /dev/null; then
       echo "✓"
       echo "   ROS 2 version: $(ros2 --version)"
   else
       echo "✗"
   fi
   
   # Test 2: Check environment
   echo -n "2. Checking ROS environment variables... "
   if [ -n "$ROS_DISTRO" ]; then
       echo "✓"
       echo "   ROS_DISTRO: $ROS_DISTRO"
   else
       echo "✗"
   fi
   
   # Test 3: Check workspace
   echo -n "3. Checking workspace setup... "
   if [ -f "$HOME/physical_ai_ws/install/setup.bash" ]; then
       echo "✓"
   else
       echo "✗"
   fi
   
   # Test 4: Check Python
   echo -n "4. Checking Python ROS packages... "
   if python3 -c "import rclpy" &> /dev/null; then
       echo "✓"
   else
       echo "✗"
   fi
   
   echo "=== Verification Complete ==="
   ```

2. Save this script and run it to get a quick overview of your setup status.

## Troubleshooting Common Issues

### 1. Command Not Found
- Ensure you've sourced ROS 2: `source /opt/ros/humble/setup.bash`
- Check if ROS 2 is properly installed: `ls /opt/ros/humble/bin/`

### 2. Permission Errors
- Ensure you're not running as root unnecessarily
- Check file permissions: `ls -la /path/to/issue`

### 3. Network/Communication Issues
- Check if ROS_DOMAIN_ID is set consistently across terminals
- Ensure no firewall is blocking ROS 2 communication

### 4. Python Import Errors
- Ensure python3-rosdep is installed: `sudo apt install python3-rosdep2`
- Check if packages are built: `colcon build` in workspace directory

## Next Steps

After successfully completing all tests:

1. Proceed to Module 1 content in the course documentation
2. Try running the example code provided in the course materials
3. Set up your development environment as recommended in the course
4. Join the course community for support and discussions

Your ROS 2 setup is now fully tested and ready for the Physical AI & Humanoid Robotics course!