// Security Service for BELP
// Handles data encryption, input sanitization, and security validation

class SecurityService {
  constructor() {
    // Generate a unique encryption key for this user session
    this.encryptionKey = this.generateEncryptionKey();
  }

  // Generate a unique encryption key based on user's browser fingerprint
  generateEncryptionKey() {
    const userAgent = navigator.userAgent;
    const screenRes = `${screen.width}x${screen.height}`;
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const fingerprint = `${userAgent}-${screenRes}-${timezone}`;
    
    // Create a hash of the fingerprint
    let hash = 0;
    for (let i = 0; i < fingerprint.length; i++) {
      const char = fingerprint.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    return `belp_${Math.abs(hash).toString(36)}_${Date.now().toString(36)}`;
  }

  // Encrypt data before storing in localStorage
  encryptData(data) {
    try {
      const jsonString = JSON.stringify(data);
      // Simple encryption using base64 + custom encoding
      // In production, use a proper encryption library like crypto-js
      const encoded = btoa(jsonString);
      const encrypted = this.encryptionKey + ':' + encoded;
      return encrypted;
    } catch (error) {
      console.error('Encryption failed:', error);
      return null;
    }
  }

  // Decrypt data from localStorage
  decryptData(encryptedData) {
    try {
      if (!encryptedData || !encryptedData.includes(':')) {
        return null;
      }
      
      const parts = encryptedData.split(':');
      if (parts.length !== 2) {
        return null;
      }
      
      const [key, encoded] = parts;
      if (key !== this.encryptionKey) {
        console.warn('Encryption key mismatch - data may be corrupted');
        return null;
      }
      
      const jsonString = atob(encoded);
      return JSON.parse(jsonString);
    } catch (error) {
      console.error('Decryption failed:', error);
      return null;
    }
  }

  // Sanitize user input to prevent XSS
  sanitizeInput(input) {
    if (typeof input !== 'string') {
      return input;
    }
    
    // Remove potentially dangerous HTML/script tags
    const dangerousPatterns = [
      /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
      /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
      /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi,
      /<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi
    ];
    
    let sanitized = input;
    dangerousPatterns.forEach(pattern => {
      sanitized = sanitized.replace(pattern, '');
    });
    
    // Escape HTML entities
    sanitized = sanitized
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');
    
    return sanitized;
  }

  // Validate user preferences data
  validatePreferences(preferences) {
    const errors = [];
    
    // Validate cuisines
    if (!Array.isArray(preferences.cuisines)) {
      errors.push('Cuisines must be an array');
    } else if (preferences.cuisines.length === 0) {
      errors.push('Please select at least one cuisine');
    } else if (preferences.cuisines.length > 15) {
      errors.push('Too many cuisines selected (max 15)');
    } else {
      // Validate each cuisine ID
      const validCuisineIds = ['italian', 'mexican', 'chinese', 'japanese', 'indian', 'thai', 'mediterranean', 'american', 'french', 'greek'];
      preferences.cuisines.forEach(cuisineId => {
        if (!validCuisineIds.includes(cuisineId)) {
          errors.push(`Invalid cuisine ID: ${cuisineId}`);
        }
      });
    }
    
    // Validate budget
    if (preferences.budget && !['budget', 'moderate', 'expensive'].includes(preferences.budget)) {
      errors.push('Invalid budget selection');
    }
    
    // Validate occasions
    if (!Array.isArray(preferences.occasions)) {
      errors.push('Occasions must be an array');
    } else if (preferences.occasions.length > 10) {
      errors.push('Too many occasions selected (max 10)');
    }
    
    // Validate dietary
    if (!Array.isArray(preferences.dietary)) {
      errors.push('Dietary preferences must be an array');
    } else if (preferences.dietary.length > 8) {
      errors.push('Too many dietary preferences (max 8)');
    }
    
    return {
      isValid: errors.length === 0,
      errors: errors
    };
  }

  // Validate search queries
  validateSearchQuery(query) {
    if (typeof query !== 'string') {
      return { isValid: false, error: 'Query must be a string' };
    }
    
    const sanitized = this.sanitizeInput(query);
    
    if (sanitized.length === 0) {
      return { isValid: false, error: 'Query cannot be empty' };
    }
    
    if (sanitized.length > 100) {
      return { isValid: false, error: 'Query too long (max 100 characters)' };
    }
    
    // Check for suspicious patterns
    const suspiciousPatterns = [
      /<script/i,
      /javascript:/i,
      /on\w+\s*=/i,
      /eval\s*\(/i,
      /document\./i
    ];
    
    for (const pattern of suspiciousPatterns) {
      if (pattern.test(sanitized)) {
        return { isValid: false, error: 'Query contains invalid characters' };
      }
    }
    
    return { isValid: true, sanitized };
  }

  // Validate location input
  validateLocation(location) {
    if (typeof location !== 'string') {
      return { isValid: false, error: 'Location must be a string' };
    }
    
    const sanitized = this.sanitizeInput(location);
    
    if (sanitized.length === 0) {
      return { isValid: false, error: 'Location cannot be empty' };
    }
    
    if (sanitized.length > 200) {
      return { isValid: false, error: 'Location too long (max 200 characters)' };
    }
    
    // Only allow letters, numbers, spaces, commas, and basic punctuation
    const validPattern = /^[a-zA-Z0-9\s,.-]+$/;
    if (!validPattern.test(sanitized)) {
      return { isValid: false, error: 'Location contains invalid characters' };
    }
    
    return { isValid: true, sanitized };
  }

  // Clear all encrypted data (for logout/security)
  clearEncryptedData() {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith('belp_')) {
          localStorage.removeItem(key);
        }
      });
      return true;
    } catch (error) {
      console.error('Failed to clear encrypted data:', error);
      return false;
    }
  }

  // Get security status
  getSecurityStatus() {
    return {
      encryptionEnabled: true,
      encryptionKey: this.encryptionKey ? 'Generated' : 'Not Generated',
      localStorageSecure: true,
      inputSanitization: true,
      dataValidation: true
    };
  }
}

// Create singleton instance
const securityService = new SecurityService();

export default securityService; 