/**
 * Template for New Chapters
 * Based on data-model.md Chapter entity attributes
 */

const ChapterTemplate = {
  create: function(chapterId, title, content, learningObjectives, codeExamples, diagrams, exercises, prerequisites) {
    return {
      chapterId: chapterId,
      title: title,
      content: content || '',
      learningObjectives: learningObjectives || [],
      codeExamples: codeExamples || [],
      diagrams: diagrams || [],
      exercises: exercises || [],
      prerequisites: prerequisites || [],
      validate: this.validate
    };
  },

  validate: function(chapter) {
    const errors = [];

    // Validate chapterId format
    if (!chapter.chapterId || typeof chapter.chapterId !== 'string') {
      errors.push('chapterId is required and must be a string');
    } else {
      // Check if chapterId follows format "{moduleNumber}.{chapterNumber}-{topic}"
      const idPattern = /^\d+\.\d+-[a-zA-Z0-9-]+$/;
      if (!idPattern.test(chapter.chapterId)) {
        errors.push('chapterId must follow format "{moduleNumber}.{chapterNumber}-{topic}"');
      }
    }

    // Validate title
    if (!chapter.title || typeof chapter.title !== 'string') {
      errors.push('title is required and must be a string');
    }

    // Validate content is valid Markdown
    if (chapter.content && typeof chapter.content !== 'string') {
      errors.push('content must be a string in Markdown format');
    }

    // Validate learning objectives
    if (!Array.isArray(chapter.learningObjectives) || chapter.learningObjectives.length === 0) {
      errors.push('learningObjectives must be a non-empty array');
    }

    // Validate code examples
    if (chapter.codeExamples && !Array.isArray(chapter.codeExamples)) {
      errors.push('codeExamples must be an array');
    }

    // Validate diagrams
    if (chapter.diagrams && !Array.isArray(chapter.diagrams)) {
      errors.push('diagrams must be an array');
    }

    // Validate exercises
    if (chapter.exercises && !Array.isArray(chapter.exercises)) {
      errors.push('exercises must be an array');
    }

    // Validate prerequisites
    if (chapter.prerequisites && !Array.isArray(chapter.prerequisites)) {
      errors.push('prerequisites must be an array');
    }

    return {
      isValid: errors.length === 0,
      errors: errors
    };
  },

  addLearningObjective: function(chapter, objective) {
    if (!chapter.learningObjectives) {
      chapter.learningObjectives = [];
    }
    if (!chapter.learningObjectives.includes(objective)) {
      chapter.learningObjectives.push(objective);
    }
  },

  addCodeExample: function(chapter, codeExample) {
    if (!chapter.codeExamples) {
      chapter.codeExamples = [];
    }
    chapter.codeExamples.push(codeExample);
  },

  addExercise: function(chapter, exercise) {
    if (!chapter.exercises) {
      chapter.exercises = [];
    }
    chapter.exercises.push(exercise);
  }
};

module.exports = ChapterTemplate;