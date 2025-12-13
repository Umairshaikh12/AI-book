/**
 * Validation Tools for Code Examples
 * Validates code examples in the Physical AI & Humanoid Robotics Course Book
 */

const fs = require('fs');
const path = require('path');

class CodeExampleValidator {
  constructor() {
    this.supportedLanguages = ['python', 'bash', 'xml', 'yaml', 'json', 'c++', 'c', 'javascript', 'typescript'];
  }

  validateCodeExample(example) {
    const errors = [];

    // Validate required fields
    if (!example.exampleId) errors.push('exampleId is required');
    if (!example.title) errors.push('title is required');
    if (!example.language) errors.push('language is required');
    if (example.code === undefined || example.code === null) errors.push('code is required');

    // Validate language
    if (!this.supportedLanguages.includes(example.language)) {
      errors.push(`language must be one of: ${this.supportedLanguages.join(', ')}`);
    }

    // Validate code syntax based on language
    if (example.language === 'python') {
      const pythonErrors = this.validatePythonCode(example.code);
      errors.push(...pythonErrors);
    } else if (example.language === 'bash') {
      const bashErrors = this.validateBashCode(example.code);
      errors.push(...bashErrors);
    }
    // Additional language validations can be added here

    // Check if code has been tested
    if (example.tested === undefined) {
      errors.push('tested status is required');
    }

    return {
      isValid: errors.length === 0,
      errors: errors
    };
  }

  validatePythonCode(code) {
    const errors = [];
    
    // Check for basic Python syntax issues
    try {
      // This is a basic validation - a real implementation might use a Python parser
      if (code.includes('import') && !code.trim().startsWith('import')) {
        // Check if import statements are at the beginning
        const lines = code.split('\n');
        let foundNonImport = false;
        for (const line of lines) {
          if (line.trim() && !line.trim().startsWith('#') && !line.trim().startsWith('import') && !line.trim().startsWith('from')) {
            foundNonImport = true;
          } else if (foundNonImport && line.trim().startsWith('import')) {
            errors.push('Import statements should be at the beginning of the file');
            break;
          }
        }
      }
    } catch (e) {
      errors.push(`Python syntax validation error: ${e.message}`);
    }

    return errors;
  }

  validateBashCode(code) {
    const errors = [];
    
    // Basic bash validation
    if (code.includes('<<EOF') && !code.includes('EOF')) {
      errors.push('Bash heredoc syntax error: EOF delimiter missing');
    }
    
    // Check for common mistakes like using = instead of == in conditionals
    if (code.includes('[ ') && code.includes(' = ') && !code.includes(' == ')) {
      errors.push('Use == instead of = in bash conditionals');
    }

    return errors;
  }

  validateCodeFile(filePath) {
    if (!fs.existsSync(filePath)) {
      return { isValid: false, errors: [`File does not exist: ${filePath}`] };
    }

    const code = fs.readFileSync(filePath, 'utf8');
    const ext = path.extname(filePath).toLowerCase();

    let language;
    switch (ext) {
      case '.py':
        language = 'python';
        break;
      case '.sh':
        language = 'bash';
        break;
      case '.xml':
        language = 'xml';
        break;
      case '.yaml':
      case '.yml':
        language = 'yaml';
        break;
      case '.json':
        language = 'json';
        break;
      case '.js':
        language = 'javascript';
        break;
      case '.ts':
        language = 'typescript';
        break;
      case '.cpp':
      case '.cxx':
      case '.cc':
        language = 'c++';
        break;
      case '.c':
        language = 'c';
        break;
      default:
        return { isValid: false, errors: [`Unsupported file extension: ${ext}`] };
    }

    // Create a temporary example object for validation
    const example = {
      exampleId: 'temp',
      title: 'temp',
      language: language,
      code: code
    };

    return this.validateCodeExample(example);
  }

  static isValidPython(code) {
    // Simple check for basic Python syntax
    try {
      // This is a simplified validation
      const lines = code.split('\n');
      let indentLevel = 0;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line || line.startsWith('#')) continue;
        
        // Check for basic syntax elements
        if (line.endsWith(':')) {
          // Increase expected indentation for control structures
          indentLevel++;
        }
      }
      return true;
    } catch (e) {
      return false;
    }
  }
}

module.exports = CodeExampleValidator;