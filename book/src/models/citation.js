/**
 * Citation Model
 * Represents a reference to an external source used in the course
 * Based on data-model.md specifications
 */

class Citation {
  constructor(citationId, title, authors, publication, year, url, doi, apaFormat, peerReviewed) {
    this.citationId = citationId;
    this.title = title;
    this.authors = authors;
    this.publication = publication;
    this.year = year;
    this.url = url;
    this.doi = doi;
    this.apaFormat = apaFormat;
    this.peerReviewed = peerReviewed;

    // Validate according to data-model.md
    this.validate();
  }

  validate() {
    if (!this.citationId || typeof this.citationId !== 'string') {
      throw new Error('citationId is required and must be a string');
    }

    if (!this.title || typeof this.title !== 'string') {
      throw new Error('title is required and must be a string');
    }

    if (!Array.isArray(this.authors) || this.authors.length === 0) {
      throw new Error('authors must be a non-empty array');
    }

    if (!this.publication || typeof this.publication !== 'string') {
      throw new Error('publication is required and must be a string');
    }

    if (!this.year || typeof this.year !== 'number' || this.year < 1900 || this.year > new Date().getFullYear() + 1) {
      throw new Error('year is required and must be a valid number between 1900 and next year');
    }

    if (!this.apaFormat || typeof this.apaFormat !== 'string') {
      throw new Error('apaFormat is required and must be a string');
    }

    if (typeof this.peerReviewed !== 'boolean') {
      throw new Error('peerReviewed must be a boolean value');
    }
  }

  static formatAsAPA(citation) {
    // Format the citation according to APA 7th edition standards
    let authorsStr = citation.authors.join(', ');
    if (citation.authors.length > 1) {
      authorsStr = authorsStr.replace(/, ([^,]*)$/, ', &$1'); // Replace last comma with &
    }
    
    const year = citation.year;
    const title = citation.title;
    const publication = citation.publication;
    const doi = citation.doi ? `doi:${citation.doi}` : citation.url;
    
    return `${authorsStr} (${year}). ${title}. ${publication}. ${doi}`;
  }

  static validateAPAFormat(apaString) {
    // Basic validation of APA format
    const requiredElements = ['(', ')', '. ', ', '];
    return requiredElements.every(element => apaString.includes(element));
  }
}

module.exports = Citation;