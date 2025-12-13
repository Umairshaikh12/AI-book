/**
 * Course Book Model
 * Represents the main educational resource containing six modules on Physical AI and humanoid robotics
 * Based on data-model.md specifications
 */

class CourseBook {
  constructor(title, wordCount, modules, authors, publicationDate, citations) {
    this.title = title;
    this.wordCount = wordCount;
    this.modules = modules;
    this.authors = authors;
    this.publicationDate = publicationDate;
    this.citations = citations;
    this.totalChapters = 0;
    this.estimatedCompletionTime = '';
    
    // Validate according to data-model.md
    this.validate();
  }

  validate() {
    if (this.wordCount < 20000 || this.wordCount > 30000) {
      throw new Error('Word count must be between 20,000 and 30,000');
    }
    
    if (this.modules.length !== 6) {
      throw new Error('Must have exactly 6 modules as defined in spec');
    }
    
    if (this.citations.length < 20) {
      throw new Error('Must include minimum 20 citations in APA format');
    }
  }

  addModule(module) {
    if (this.modules.length >= 6) {
      throw new Error('Course book can only have 6 modules');
    }
    this.modules.push(module);
  }

  getModuleById(moduleId) {
    return this.modules.find(module => module.moduleId === moduleId);
  }

  addCitation(citation) {
    this.citations.push(citation);
  }

  getPeerReviewedCitations() {
    return this.citations.filter(citation => citation.peerReviewed === true);
  }

  getEstimatedCompletionTime() {
    // Estimate completion time based on word count and number of modules
    const hoursPerWord = 1 / 200; // Assuming 200 words per hour reading speed
    const hoursPerCodeExample = 1; // Assuming 1 hour per code example
    const hoursPerExercise = 1.5; // Assuming 1.5 hours per exercise
    
    let totalTime = 0;
    totalTime += this.wordCount * hoursPerWord;
    
    this.modules.forEach(module => {
      if (module.chapters) {
        module.chapters.forEach(chapter => {
          if (chapter.codeExamples) totalTime += chapter.codeExamples.length * hoursPerCodeExample;
          if (chapter.exercises) totalTime += chapter.exercises.length * hoursPerExercise;
        });
      }
    });
    
    return `${Math.ceil(totalTime)} hours`;
  }
}

module.exports = CourseBook;