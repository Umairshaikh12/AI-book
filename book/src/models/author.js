/**
 * Author Model
 * Represents an author of the course book
 * Based on data-model.md specifications
 */

class Author {
  constructor(authorId, name, affiliation, expertise, bio) {
    this.authorId = authorId;
    this.name = name;
    this.affiliation = affiliation;
    this.expertise = expertise;
    this.bio = bio;

    // Validate according to data-model.md
    this.validate();
  }

  validate() {
    if (!this.authorId || typeof this.authorId !== 'string') {
      throw new Error('authorId is required and must be a string');
    }

    if (!this.name || typeof this.name !== 'string' || this.name.trim() === '') {
      throw new Error('name is required and must be a non-empty string');
    }

    if (!Array.isArray(this.expertise) || this.expertise.length === 0) {
      throw new Error('expertise must be a non-empty array');
    }

    // Check if expertise includes robotics or AI-related fields
    const validExpertise = ['robotics', 'artificial intelligence', 'AI', 'machine learning', 
                           'computer science', 'engineering', 'physical AI', 'humanoid robotics'];
    const hasValidExpertise = this.expertise.some(expertise => 
      validExpertise.some(valid => expertise.toLowerCase().includes(valid.toLowerCase()))
    );

    if (!hasValidExpertise) {
      throw new Error('Expertise must include robotics or AI-related fields');
    }
  }

  addExpertise(newExpertise) {
    if (!this.expertise.includes(newExpertise)) {
      this.expertise.push(newExpertise);
    }
  }

  updateBio(newBio) {
    this.bio = newBio;
  }

  getExpertiseSummary() {
    return this.expertise.join(', ');
  }
}

module.exports = Author;