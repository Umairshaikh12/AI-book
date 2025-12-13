---
sidebar_position: 2
---

# Module 1: ROS 2 (Robotic Nervous System)

## Overview

The Robot Operating System 2 (ROS 2) is the foundation of modern robotics development. In this module, we'll explore ROS 2 as the "nervous system" of robots, learning how it enables communication between different components of a robotic system.

## Learning Objectives

By the end of this module, you will be able to:
- Explain the core concepts of ROS 2 (nodes, topics, services)
- Set up a ROS 2 development environment
- Create basic ROS 2 nodes using Python (rclpy)
- Design URDF files for humanoid robots
- Understand how ROS 2 enables distributed robotics systems

## What is ROS 2?

ROS 2 is a flexible framework for writing robotic software. It's a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robotic applications. As the "nervous system" of a robot, ROS 2 coordinates between different software components, manages hardware interfaces, and provides services such as hardware abstraction, device drivers, libraries for common functions, message-passing between processes, and package management.

Key features of ROS 2 include:
- Distributed computing: Multiple nodes can run on different machines
- Language independence: Support for multiple programming languages
- Real-time support: Capabilities for real-time systems
- Improved security: Built-in security features
- Quality of service: Configurable communication reliability

## Core Concepts: Nodes, Topics, Services

### Nodes
A node is an executable that uses ROS 2 to communicate with other nodes. Nodes are the processes that perform computation. In a distributed system, many nodes can run on different devices or machines. ROS 2 is designed to have many nodes working together to form a complete robot application.

### Topics
Topics are used for unidirectional communication between nodes. Nodes can publish messages to a topic or subscribe to messages from a topic. This creates a publish-subscribe communication pattern. Multiple nodes can publish or subscribe to the same topic, enabling flexible messaging architectures.

### Services
Services enable bidirectional communication between nodes. A service client sends a request to a service server and waits for a response. This is useful for operations that require a specific response, like requesting sensor data or commanding an action with confirmation.

## Understanding rclpy Integration

rclpy is the Python client library for ROS 2. It provides the API to interact with ROS 2 from Python code. rclpy allows you to:

- Create nodes and define their behavior
- Publish and subscribe to topics
- Create and use services
- Work with parameters
- Handle actions

rclpy follows the same concepts as other ROS 2 client libraries but provides Python-specific idioms and patterns.

## URDF for Humanoids

The Unified Robot Description Format (URDF) is an XML format for representing a robot model. URDF is used to describe the physical and visual properties of a robot, including:

- Kinematic structure (joints and links)
- Visual properties (for visualization)
- Collision properties (for collision detection)
- Inertial properties (for physics simulation)

For humanoid robots, URDF becomes particularly important as it describes the complex structure of limbs, joints, and sensors that characterize these robots.

## Summary

This module introduces the essential ROS 2 concepts that form the backbone of robotic development. We'll implement these concepts in the following chapters, creating nodes, working with topics and services, integrating rclpy, and creating URDF models for humanoid robots.

## Prerequisites

Before starting this module, ensure you have:
- A working ROS 2 Humble Hawksbill installation
- Basic Python programming knowledge
- Familiarity with Linux command line