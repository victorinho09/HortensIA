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
  if (!code && !phone) return ''; // Both empty is okay
  if (!code && phone) return 'Country code required with phone number';
  if (!/^\d{1,3}$/.test(code)) return 'Invalid country code';
  return '';
};

export const validatePhone = (phone: string, countryCode: string): string => {
  if (!phone && !countryCode) return ''; // Both empty is okay
  if (!phone && countryCode) return 'Phone number required with country code';
  if (!/^\d{6,15}$/.test(phone)) return 'Invalid phone number';
  return '';
};

export const validateDiversityType = (diversityType: string): string => {
  return ''; // Free-form text, no validation needed
};

export const validateName = (name: string): string =>{
    return ''; //No validation required. It is optional
};