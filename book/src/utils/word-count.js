/**
 * Word Count Tracking Tool
 * Ensures content meets the 20,000-30,000 word requirement
 */

class WordCountTracker {
  constructor() {
    this.wordCount = 0;
    this.targetMin = 20000;
    this.targetMax = 30000;
  }

  countWords(text) {
    if (!text || typeof text !== 'string') {
      return 0;
    }
    
    // Remove extra whitespace and count words
    return text.trim()
      .split(/\s+/)
      .filter(word => word.length > 0).length;
  }

  addText(text) {
    const words = this.countWords(text);
    this.wordCount += words;
    return this.wordCount;
  }

  addMultipleTexts(texts) {
    let totalAdded = 0;
    for (const text of texts) {
      totalAdded += this.countWords(text);
    }
    this.wordCount += totalAdded;
    return this.wordCount;
  }

  getWordCount() {
    return this.wordCount;
  }

  getRemainingWords() {
    return this.targetMax - this.wordCount;
  }

  isWithinRange() {
    return this.wordCount >= this.targetMin && this.wordCount <= this.targetMax;
  }

  isUnderMinimum() {
    return this.wordCount < this.targetMin;
  }

  isOverMaximum() {
    return this.wordCount > this.targetMax;
  }

  getPercentageComplete() {
    // Calculate percentage based on the target range
    if (this.wordCount <= this.targetMin) {
      return 0;
    } else if (this.wordCount >= this.targetMax) {
      return 100;
    } else {
      // Calculate percentage between min and max
      return Math.min(100, Math.max(0, 
        ((this.wordCount - this.targetMin) / (this.targetMax - this.targetMin)) * 100
      ));
    }
  }

  getWordsNeeded() {
    if (this.wordCount < this.targetMin) {
      return this.targetMin - this.wordCount;
    }
    return 0;
  }

  getStatus() {
    if (this.isWithinRange()) {
      return 'GREEN - Within required range';
    } else if (this.isUnderMinimum()) {
      return `RED - ${this.getWordsNeeded()} words needed to reach minimum`;
    } else if (this.isOverMaximum()) {
      return `RED - ${this.wordCount - this.targetMax} words over maximum`;
    }
    return 'UNKNOWN';
  }

  static countWordsInMarkdown(markdownContent) {
    // Remove markdown syntax before counting
    if (!markdownContent || typeof markdownContent !== 'string') {
      return 0;
    }
    
    // Remove markdown elements but keep the text content
    const plainText = markdownContent
      // Remove headers
      .replace(/^#+\s+/gm, '')
      // Remove emphasis
      .replace(/[*_]{1,3}([^*_]+)[*_]{1,3}/g, '$1')
      // Remove inline code
      .replace(/`([^`]+)`/g, '$1')
      // Remove code blocks
      .replace(/```[\s\S]*?```/g, '')
      // Remove links but keep the link text
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      // Remove images but keep the alt text
      .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1')
      // Remove blockquotes
      .replace(/^>\s+/gm, '')
      // Remove horizontal rules
      .replace(/^\s*[-*_]{3,}\s*$/gm, '')
      // Remove list markers
      .replace(/^\s*[\-*+]\s+/gm, '')
      .replace(/^\s*\d+\.\s+/gm, '');
    
    return this.countWords(plainText);
  }
}

module.exports = WordCountTracker;