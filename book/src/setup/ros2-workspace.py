#!/usr/bin/env python3

"""
ROS 2 Workspace Setup Script
This script automates the process of setting up a ROS 2 workspace for the Physical AI & Humanoid Robotics course.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_ros2_installation():
    """
    Check if ROS 2 is properly installed and sourced
    """
    try:
        result = subprocess.run(['ros2', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ ROS 2 is installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ROS 2 is not installed or not in PATH")
        print("Please install ROS 2 Humble Hawksbill before continuing.")
        return False


def create_workspace(workspace_name="physical_ai_ws"):
    """
    Create a new ROS 2 workspace directory structure
    """
    workspace_path = Path.home() / workspace_name
    
    if workspace_path.exists():
        print(f"⚠️  Workspace {workspace_path} already exists. Skipping creation.")
        return workspace_path
    
    try:
        workspace_path.mkdir(parents=True, exist_ok=True)
        src_path = workspace_path / 'src'
        src_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created ROS 2 workspace: {workspace_path}")
        print(f"✓ Created source directory: {src_path}")
        return workspace_path
    except Exception as e:
        print(f"✗ Failed to create workspace: {e}")
        return None


def build_workspace(workspace_path):
    """
    Build the ROS 2 workspace using colcon
    """
    try:
        # Change to workspace directory
        original_dir = os.getcwd()
        os.chdir(workspace_path)
        
        # Build the workspace
        print("📦 Building workspace with colcon...")
        result = subprocess.run(['colcon', 'build'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Workspace built successfully")
        else:
            print(f"✗ Build failed: {result.stderr}")
            return False
            
        # Source the workspace
        setup_path = workspace_path / 'install' / 'setup.bash'
        if setup_path.exists():
            print(f"✓ Workspace built at: {setup_path}")
        else:
            print("✗ Install setup.bash not found - build may have failed")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Error during build: {e}")
        return False
    finally:
        # Return to original directory
        os.chdir(original_dir)


def create_package(workspace_path, package_name="physical_ai_examples"):
    """
    Create a new ROS 2 package within the workspace
    """
    try:
        src_path = workspace_path / 'src'
        package_path = src_path / package_name
        
        if package_path.exists():
            print(f"⚠️  Package {package_name} already exists. Skipping creation.")
            return package_path
        
        # Create the package using ros2 pkg create
        print(f"📦 Creating ROS 2 package: {package_name}")
        result = subprocess.run([
            'ros2', 'pkg', 'create', 
            '--build-type', 'ament_python', 
            package_name
        ], cwd=src_path, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Created package: {package_name}")
            return package_path
        else:
            print(f"✗ Failed to create package: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ Error creating package: {e}")
        return None


def setup_dependencies():
    """
    Install common dependencies needed for humanoid robotics
    """
    dependencies = [
        'ros-humble-ros-base',
        'ros-humble-ros-core',
        'ros-humble-gazebo-ros-pkgs',
        'ros-humble-navigation2',
        'ros-humble-nav2-bringup',
        'ros-humble-xacro',
        'ros-humble-joint-state-publisher',
        'ros-humble-robot-state-publisher'
    ]
    
    print("📋 Installing common ROS 2 dependencies...")
    print("Note: This may require sudo access and will install system packages.")
    
    # We'll just print the apt commands that should be run
    print("\nTo install ROS 2 dependencies, run:")
    print("sudo apt update")
    print(f"sudo apt install {' '.join(dependencies)}")
    
    return True


def verify_setup():
    """
    Perform basic checks to verify the ROS 2 setup is working
    """
    print("\n🔍 Verifying ROS 2 setup...")
    
    # Check if ROS_DISTRO is set
    ros_distro = os.environ.get('ROS_DISTRO')
    if ros_distro:
        print(f"✓ ROS_DISTRO is set to: {ros_distro}")
    else:
        print("⚠️  ROS_DISTRO environment variable is not set")
    
    # Try to run a simple ROS 2 command
    try:
        result = subprocess.run(['ros2', 'topic', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ ROS 2 topic list command executed successfully")
        else:
            print("⚠️  ROS 2 topic list command failed")
    except subprocess.TimeoutExpired:
        print("⚠️  ROS 2 topic list command timed out - this is normal if no ROS nodes are running")
    except Exception as e:
        print(f"⚠️  Error verifying ROS 2 setup: {e}")
    
    return True


def create_workspace_config(workspace_path):
    """
    Create configuration files for the workspace
    """
    # Create a README file for the workspace
    readme_content = f"""# Physical AI & Humanoid Robotics Workspace

This workspace contains packages for the Physical AI & Humanoid Robotics course.

## Getting Started

1. Source the workspace:
   ```bash
   cd {workspace_path}
   source install/setup.bash
   ```

2. Run examples:
   ```bash
   ros2 run <package_name> <executable_name>
   ```

## Packages

This workspace includes packages for:
- Humanoid robot control
- Gazebo simulation
- ROS 2 tutorials
- Course examples
"""
    
    readme_path = workspace_path / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"✓ Created workspace README: {readme_path}")
    
    # Create a setup script
    setup_script = f"""#!/bin/bash
# Setup script for Physical AI & Humanoid Robotics workspace

# Navigate to workspace
cd {workspace_path}

# Source ROS 2 if not already sourced
if [ -z "$ROS_DISTRO" ]; then
    source /opt/ros/humble/setup.bash
    echo "Sourced ROS 2 Humble"
fi

# Source the workspace
if [ -f install/setup.bash ]; then
    source install/setup.bash
    echo "Sourced workspace"
else
    echo "Workspace not built yet. Run 'colcon build' first."
fi

echo "Workspace environment is ready!"
echo "ROS_DISTRO: $ROS_DISTRO"
echo "ROS_PACKAGE_PATH: $ROS_PACKAGE_PATH"
"""
    
    setup_path = workspace_path / 'setup_workspace.sh'
    with open(setup_path, 'w') as f:
        f.write(setup_script)
    
    # Make it executable
    os.chmod(setup_path, 0o755)
    print(f"✓ Created setup script: {setup_path}")
    
    return True


def main():
    """
    Main function to orchestrate the ROS 2 workspace setup
    """
    print("🤖 Setting up ROS 2 workspace for Physical AI & Humanoid Robotics course")
    print("="*70)
    
    # Check if ROS 2 is installed
    if not check_ros2_installation():
        print("\n❌ Setup failed: ROS 2 is not installed or not in PATH")
        print("Please install ROS 2 Humble Hawksbill and ensure it's in your PATH before running this script.")
        sys.exit(1)
    
    # Create workspace
    workspace_path = create_workspace()
    if not workspace_path:
        print("\n❌ Setup failed: Could not create workspace")
        sys.exit(1)
    
    # Create a default package
    package_path = create_package(workspace_path)
    if not package_path:
        print("\n⚠️  Warning: Could not create default package, but continuing setup")
    
    # Create workspace configuration
    create_workspace_config(workspace_path)
    
    # Build workspace
    if not build_workspace(workspace_path):
        print("\n❌ Setup failed: Could not build workspace")
        sys.exit(1)
    
    # Verify setup
    verify_setup()
    
    # Provide next steps
    print("\n" + "="*70)
    print("✅ ROS 2 workspace setup complete!")
    print(f"📁 Workspace location: {workspace_path}")
    print("\n📋 Next steps:")
    print(f"1. Navigate to workspace: cd {workspace_path}")
    print(f"2. Source the workspace: source install/setup.bash")
    print("3. Start developing your ROS 2 packages")
    print("\n📖 For more information, refer to the course materials in the book/docs/ directory")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())