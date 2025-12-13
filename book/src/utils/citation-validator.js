/**
 * Citation Validator for APA 7th Edition Format
 * Verifies citations follow proper APA 7th edition format
 */

const fs = require('fs');
const path = require('path');

class CitationValidator {
  constructor() {
    this.apaPattern = this.createApaPattern();
  }

  /**
   * Creates regex patterns for APA 7th edition citation formats
   * Supports various common APA formats:
   * - Single author: Author, A. A. (Year). Title. Publisher.
   * - Multiple authors: Author, A. A., & Author, B. B. (Year). Title. Publisher.
   * - With DOI: Author, A. A. (Year). Title. https://doi.org/xx.xxx/yyyy
   * - With URL: Author, A. A. (Year). Title. Publisher/URL
   */
  createApaPattern() {
    // Simplified pattern for basic APA format validation
    const basicPattern = /^([A-Z][a-z]+,\s[A-Z]\.\s?([A-Z]\.)*\s?(&\s[A-Z][a-z]+,\s[A-Z]\.\s?([A-Z]\.)*)*|[A-Z][a-z]+,\s[A-Z]\.\s?([A-Z]\.)*\s?et\sal\.*)\s\((\d{4}|n\.d\.)\)\.\s(.+?)\.\s(.+?\.)?(\shttps:\/\/doi\.org\/\d+\/[a-zA-Z0-9_.-]+|\s.+\.[a-z]{2,3}\/[a-zA-Z0-9_.-\/]+)?$/;
    return basicPattern;
  }

  /**
   * Validates a single citation string against APA format
   * @param {string} citation - The citation string to validate
   * @returns {object} Validation result with isValid flag and error message
   */
  validateCitation(citation) {
    if (!citation || typeof citation !== 'string') {
      return {
        isValid: false,
        error: 'Citation must be a non-empty string'
      };
    }

    // Check if it roughly matches APA format
    const matchesPattern = this.apaPattern.test(citation.trim());
    
    // Additional checks
    const checks = {
      hasAuthor: /([A-Z][a-z]+,\s[A-Z]\.)/.test(citation),
      hasYear: /\((\d{4}|n\.d\.)\)/.test(citation),
      hasTitle: /([A-Za-z].+?)\.\s/.test(citation),
      endsWithPeriod: citation.trim().endsWith('.') || citation.trim().endsWith('.)')
    };

    const allChecksPassed = Object.values(checks).every(check => check);

    if (matchesPattern && allChecksPassed) {
      return {
        isValid: true,
        error: null,
        checks: checks
      };
    } else {
      const errors = [];
      
      if (!checks.hasAuthor) errors.push('Missing author in APA format (Lastname, A.A.)');
      if (!checks.hasYear) errors.push('Missing year in format (YYYY) or (n.d.)');
      if (!checks.hasTitle) errors.push('Missing or incorrectly formatted title');
      if (!checks.endsWithPeriod) errors.push('Citation does not end with a period');
      
      return {
        isValid: false,
        error: `Citation does not match APA 7th edition format. Issues: ${errors.join(', ')}`,
        checks: checks
      };
    }
  }

  /**
   * Validates all citations in a BibTeX file
   * @param {string} bibFilePath - Path to the .bib file
   * @returns {object} Validation results for all citations
   */
  validateBibFile(bibFilePath) {
    if (!fs.existsSync(bibFilePath)) {
      throw new Error(`BibTeX file does not exist: ${bibFilePath}`);
    }

    const content = fs.readFileSync(bibFilePath, 'utf8');
    const entries = this.parseBibTeX(content);
    
    const results = {
      total: entries.length,
      valid: 0,
      invalid: 0,
      entries: []
    };

    for (const entry of entries) {
      const citationText = this.formatAsApa(entry);
      const validation = this.validateCitation(citationText);
      
      results.entries.push({
        id: entry.id,
        original: entry.raw,
        formatted: citationText,
        validation: validation
      });
      
      if (validation.isValid) {
        results.valid++;
      } else {
        results.invalid++;
      }
    }

    return results;
  }

  /**
   * Parses BibTeX content into structured entries
   * @param {string} content - The BibTeX content to parse
   * @returns {array} Array of parsed BibTeX entries
   */
  parseBibTeX(content) {
    // Simple BibTeX parser
    const entries = [];
    const entryPattern = /@(\w+)\{([^,]+),\s*([^}]+)\}/gs;
    let match;

    while ((match = entryPattern.exec(content)) !== null) {
      const type = match[1];
      const id = match[2].trim();
      const fieldsText = match[3];

      // Parse fields
      const fieldPattern = /(\w+)\s*=\s*\{([^}]*)\}/g;
      const fields = {};
      let fieldMatch;

      while ((fieldMatch = fieldPattern.exec(fieldsText)) !== null) {
        const fieldName = fieldMatch[1].toLowerCase();
        const fieldValue = fieldMatch[2].trim();
        fields[fieldName] = fieldValue;
      }

      entries.push({
        type: type,
        id: id,
        fields: fields,
        raw: match[0]
      });
    }

    return entries;
  }

  /**
   * Formats a BibTeX entry as APA citation string
   * @param {object} entry - The BibTeX entry to format
   * @returns {string} APA formatted citation
   */
  formatAsApa(entry) {
    const fields = entry.fields;
    let citation = '';

    // Format author(s)
    if (fields.author) {
      citation += this.formatAuthors(fields.author) + ' ';
    }

    // Add year
    if (fields.year) {
      citation += `(${fields.year}). `;
    } else {
      citation += '(n.d.). ';
    }

    // Add title
    if (fields.title) {
      citation += `${fields.title}. `;
    }

    // Add journal/publisher info based on entry type
    if (entry.type.toLowerCase() === 'article' && fields.journal) {
      citation += `${fields.journal}. `;
    } else if (fields.publisher) {
      citation += `${fields.publisher}. `;
    }

    // Add URL or DOI if available
    if (fields.doi) {
      citation += `https://doi.org/${fields.doi}`;
    } else if (fields.url) {
      citation += fields.url;
    }

    return citation;
  }

  /**
   * Formats author list in APA style
   * @param {string} authorString - Raw author string from BibTeX
   * @returns {string} Formatted author list in APA style
   */
  formatAuthors(authorString) {
    // Handle different author format notations
    const authors = authorString.split(' and ');
    if (authors.length === 0) return '';

    const formattedAuthors = authors.map(author => {
      // Format "Lastname, Firstname" to "Lastname, F."
      author = author.trim();
      const commaIndex = author.indexOf(',');
      if (commaIndex > 0) {
        const lastName = author.substring(0, commaIndex).trim();
        const firstNames = author.substring(commaIndex + 1).trim();
        
        // Handle multiple first names or initials
        const nameParts = firstNames.split(/\s+/).filter(part => part.length > 0);
        const initials = nameParts.map(name => {
          return name.charAt(0).toUpperCase() + '.';
        }).join(' ');
        
        return `${lastName}, ${initials}`;
      } else {
        // If no comma, assume "Firstname Lastname" format
        const parts = author.split(/\s+/);
        if (parts.length >= 2) {
          const lastName = parts[parts.length - 1];
          const firstNames = parts.slice(0, -1);
          const initials = firstNames.map(name => {
            return name.charAt(0).toUpperCase() + '.';
          }).join(' ');
          return `${lastName}, ${initials}`;
        }
        return author; // Return as-is if not properly formatted
      }
    });

    if (formattedAuthors.length === 1) {
      return formattedAuthors[0];
    } else if (formattedAuthors.length === 2) {
      return `${formattedAuthors[0]} & ${formattedAuthors[1]}`;
    } else {
      // For 3 or more authors, use "First, A. A., Second, B. B., & Third, C. C." format
      const lastAuthor = formattedAuthors.pop();
      return `${formattedAuthors.join(', ')}, & ${lastAuthor}`;
    }
  }

  /**
   * Performs comprehensive validation of citations
   * @param {string} citationDirPath - Path to the citations directory
   * @returns {object} Comprehensive validation results
   */
  validateCitations(citationDirPath) {
    const referencesPath = path.join(citationDirPath, 'references.bib');
    if (!fs.existsSync(referencesPath)) {
      throw new Error(`references.bib not found in ${citationDirPath}`);
    }

    const validationResults = this.validateBibFile(referencesPath);
    
    // Additional checks for the assignment requirements
    const peerReviewedCount = validationResults.entries
      .filter(entry => entry.original.toLowerCase().includes('peer') || 
                     entry.original.toLowerCase().includes('journal') ||
                     entry.original.toLowerCase().includes('conference') ||
                     entry.original.toLowerCase().includes('trans'))
      .length;
    
    return {
      ...validationResults,
      peerReviewedCount: peerReviewedCount,
      peerReviewedPercentage: validationResults.total > 0 ? (peerReviewedCount / validationResults.total) * 100 : 0,
      meetsMinRequirement: validationResults.total >= 20, // Minimum 20 references requirement
      meetsPeerReviewRequirement: validationResults.total > 0 ? (peerReviewedCount / validationResults.total) >= 0.5 : true // 50% peer reviewed
    };
  }
}

module.exports = CitationValidator;