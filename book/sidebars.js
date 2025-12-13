// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro/index',
    {
      type: 'category',
      label: 'Module 1: ROS 2 (Robotic Nervous System)',
      items: [
        'module-1-ros2/chapter-1',
        'module-1-ros2/chapter-2',
        'module-1-ros2/chapter-3',
        'module-1-ros2/chapter-4',
        'module-1-ros2/exercises',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twin (Gazebo and Unity)',
      items: [
        'module-2-digital-twin/chapter-1',
        'module-2-digital-twin/chapter-2',
        'module-2-digital-twin/chapter-3',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: AI-Robot Brain (NVIDIA Isaac)',
      items: [
        'module-3-ai-brain/chapter-1',
        'module-3-ai-brain/chapter-2',
        'module-3-ai-brain/chapter-3',
        'module-3-ai-brain/exercises',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: [
        'module-4-vla/chapter-1',
        'module-4-vla/chapter-2',
      ],
    },
    {
      type: 'category',
      label: 'Capstone Project',
      items: [
        'capstone/chapter-1',
        'capstone/chapter-2',
        'capstone/chapter-3',
        'capstone/assessment',
        'capstone/exercises',
      ],
    },
  ],
};

module.exports = sidebars;