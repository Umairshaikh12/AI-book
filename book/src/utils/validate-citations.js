#!/usr/bin/env node

/**
 * Script to run automated quality checks for APA citations
 * Validates all citations in the references.bib file against APA 7th edition format
 */

const CitationValidator = require('./utils/citation-validator');
const path = require('path');

function runCitationValidation() {
  try {
    const citationDir = path.join(__dirname, '..', 'citations');
    const validator = new CitationValidator();
    const results = validator.validateCitations(citationDir);

    console.log('=== APA Citation Validation Results ===\n');
    console.log(`Total citations found: ${results.total}`);
    console.log(`Valid citations: ${results.valid}`);
    console.log(`Invalid citations: ${results.invalid}`);
    console.log(`Peer-reviewed citations: ${results.peerReviewedCount} (${results.peerReviewedPercentage.toFixed(1)}%)`);
    console.log(`Meets minimum 20 citations requirement: ${results.meetsMinRequirement ? 'YES' : 'NO'}`);
    console.log(`Meets 50% peer-reviewed requirement: ${results.meetsPeerReviewRequirement ? 'YES' : 'NO'}\n`);

    if (results.invalid > 0) {
      console.log('=== Invalid Citations ===');
      results.entries
        .filter(entry => !entry.validation.isValid)
        .forEach(entry => {
          console.log(`\nID: ${entry.id}`);
          console.log(`Original: ${entry.original.substring(0, 100)}...`);
          console.log(`Error: ${entry.validation.error}`);
        });
    }

    // Check overall requirements
    const allRequirementsMet = 
      results.meetsMinRequirement && 
      results.meetsPeerReviewRequirement && 
      results.invalid === 0;

    console.log('\n=== Overall Status ===');
    if (allRequirementsMet) {
      console.log('✓ All citation requirements have been met!');
      console.log('  - Minimum 20 citations: ✓');
      console.log('  - At least 50% peer-reviewed: ✓');
      console.log('  - All citations in APA format: ✓');
      process.exit(0);
    } else {
      console.log('✗ Some citation requirements are not met:');
      if (!results.meetsMinRequirement) console.log('  - Need at least 20 citations');
      if (!results.meetsPeerReviewRequirement) console.log('  - Need at least 50% peer-reviewed citations');
      if (results.invalid > 0) console.log('  - Some citations are not in proper APA format');
      process.exit(1);
    }
  } catch (error) {
    console.error('Error during citation validation:', error.message);
    process.exit(1);
  }
}

// Run the validation if this script is executed directly
if (require.main === module) {
  runCitationValidation();
}

module.exports = { runCitationValidation };