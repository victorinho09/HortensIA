export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateRequired = (value: string, fieldName: string): string => {
  if (!value.trim()) return `${fieldName} is required`;
  return '';
};

export const validatePassword = (password: string): string => {
  const required = validateRequired(password, 'Password');
  if (required) return required;
  if (password.length < 8) return 'Minimum 8 characters';
  return '';
};

export const validatePasswordMatch = (
  password: string,
  confirmPassword: string,
): string => {
  if (!confirmPassword) return 'Please confirm password';
  if (password !== confirmPassword) return 'Passwords do not match';
  return '';
};

export const validateEmailField = (email: string): string => {
  if (!email.trim()) return 'Email is required';
  if (!validateEmail(email)) return 'Invalid email format';
  return '';
};

export const validateContactEmail = (contactEmail: string): string =>{
    if (!contactEmail.trim()) return '';
    if (!validateEmail(contactEmail)) return 'Invalid email format';
    return '';
}

export const validateCountryCode = (code: string, phone: string): string => {
  // Both empty is okay (optional fields)
  if (!code.trim() && !phone.trim()) return '';
  
  // If phone is provided, country code is required
  if (!code.trim() && phone.trim()) return 'Country code required with phone number';
  
  // If country code is provided, validate format (only if not empty)
  if (code.trim() && !/^\d{1,3}$/.test(code.trim())) return 'Invalid country code (1-3 digits)';
  
  return '';
};

export const validatePhone = (phone: string, countryCode: string): string => {
  // Both empty is okay (optional fields)
  if (!phone.trim() && !countryCode.trim()) return '';
  
  // If country code is provided, phone number is required
  if (!phone.trim() && countryCode.trim()) return 'Phone number required with country code';
  
  // If phone is provided, validate format (only if not empty)
  if (phone.trim() && !/^\d{6,15}$/.test(phone.trim())) return 'Phone number must be 6-15 digits';
  
  return '';
};

export const validateDiversityType = (diversityType: string): string => {
  return ''; // Free-form text, no validation needed
};

export const validateName = (name: string): string =>{
    return ''; //No validation required. It is optional
};