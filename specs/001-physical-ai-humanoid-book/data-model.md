# Data Model: Physical AI & Humanoid Robotics Course Book

**Feature**: Physical AI & Humanoid Robotics Course Book
**Date**: 2025-12-11

## Key Entities

### 1. Course Book
- **Description**: The main educational resource containing six modules on Physical AI and humanoid robotics
- **Attributes**:
  - title: string
  - wordCount: integer (20,000-30,000)
  - modules: Module[]
  - authors: Author[]
  - publicationDate: date
  - citations: Citation[]
  - totalChapters: integer
  - estimatedCompletionTime: string
- **Validation**:
  - wordCount must be between 20,000 and 30,000
  - must have exactly 6 modules as defined in spec
  - must include minimum 20 citations in APA format

### 2. Module
- **Description**: A major section of the course book containing related content
- **Attributes**:
  - moduleId: string (e.g., "module-1-ros2")
  - title: string
  - chapters: Chapter[]
  - learningObjectives: string[]
  - prerequisites: string[]
  - estimatedDuration: string
- **Validation**:
  - moduleId must follow format "module-{number}-{topic}"
  - must have at least one chapter
  - title must match one of the six specified modules in the spec

### 3. Chapter
- **Description**: A subsection within a module containing specific learning content
- **Attributes**:
  - chapterId: string (e.g., "ch1-intro-ros2")
  - title: string
  - content: string (Markdown format)
  - learningObjectives: string[]
  - codeExamples: CodeExample[]
  - diagrams: Diagram[]
  - exercises: Exercise[]
  - prerequisites: string[]
- **Validation**:
  - chapterId must follow format "{moduleNumber}.{chapterNumber}-{topic}"
  - content must be in valid Markdown format
  - must have at least one learning objective

### 4. CodeExample
- **Description**: A code snippet included in the course material
- **Attributes**:
  - exampleId: string
  - title: string
  - language: string (e.g., "python", "bash", "xml")
  - code: string
  - explanation: string
  - tested: boolean
  - testResults: TestResult
- **Validation**:
  - code must be syntactically valid for the specified language
  - must have been tested and verified to work in the target environment
  - language must be one of the supported languages

### 5. Diagram
- **Description**: A visual representation used to explain concepts
- **Attributes**:
  - diagramId: string
  - title: string
  - type: string (e.g., "architecture", "flowchart", "sequence")
  - description: string
  - fileReference: string
  - caption: string
- **Validation**:
  - fileReference must point to an existing diagram file
  - type must be one of the valid diagram types

### 6. Citation
- **Description**: A reference to an external source used in the course
- **Attributes**:
  - citationId: string
  - title: string
  - authors: string[]
  - publication: string
  - year: integer
  - url: string (optional)
  - doi: string (optional)
  - apaFormat: string
  - peerReviewed: boolean
- **Validation**:
  - must follow APA 7th edition format
  - peerReviewed must be true for at least 50% of citations
  - all required fields must be present

### 7. Exercise
- **Description**: A practical task for students to complete
- **Attributes**:
  - exerciseId: string
  - title: string
  - description: string
  - difficulty: string ("beginner", "intermediate", "advanced")
  - estimatedTime: string
  - requiredSkills: string[]
  - solution: string (optional)
- **Validation**:
  - difficulty must be one of the allowed values
  - estimatedTime must be in valid format (e.g., "30 minutes")

### 8. Author
- **Description**: An author of the course book
- **Attributes**:
  - authorId: string
  - name: string
  - affiliation: string
  - expertise: string[]
  - bio: string
- **Validation**:
  - name must be non-empty
  - expertise must include robotics or AI-related fields

### 9. SimulationEnvironment
- **Description**: A simulated environment for testing humanoid robots
- **Attributes**:
  - envId: string
  - name: string
  - type: string ("gazebo", "isaac", "unity")
  - humanoidModel: string
  - physicsEngine: string
  - sensors: Sensor[]
  - scenarios: Scenario[]
- **Validation**:
  - type must be one of the supported simulation types
  - must be reproducible across different student setups

### 10. Sensor
- **Description**: A simulated sensor on the humanoid robot
- **Attributes**:
  - sensorId: string
  - name: string
  - type: string ("lidar", "imu", "camera", "depth_camera")
  - specifications: object
  - frameId: string
- **Validation**:
  - type must be one of the supported sensor types
  - specifications must match the requirements for the sensor type

### 11. Scenario
- **Description**: A specific test scenario within a simulation environment
- **Attributes**:
  - scenarioId: string
  - title: string
  - description: string
  - goal: string
  - initialConditions: object
  - successCriteria: string[]
- **Validation**:
  - must have defined success criteria that can be objectively measured
  - initial conditions must be properly specified