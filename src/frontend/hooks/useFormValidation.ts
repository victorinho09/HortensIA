import { useState } from 'react';

export const useFormValidation = <T extends Record<string, string>>(
  initialValues: T,
  validatorsFn: (data: T) => Record<keyof T, (value: string) => string>
) => {
  const [formData, setFormData] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<keyof T, string>>({} as Record<keyof T, string>);
  const [touched, setTouched] = useState<Record<keyof T, boolean>>({} as Record<keyof T, boolean>);

  const validators = validatorsFn(formData);

  const handleBlur = (field: keyof T) => () => {
    setTouched(prev => ({ ...prev, [field]: true }));
    const value = formData[field];
    if (value.trim() === '') {
      setErrors(prev => ({ ...prev, [field]: '' }));
      return;
    }
    setErrors(prev => ({ ...prev, [field]: validators[field](value) }));
  };

  const handleChange = (field: keyof T) => (value: string) => {
    setFormData(prev => ({ ...prev, [field]: value as any }));
    if (!touched[field]) return;

    if (value.trim() === '') {
      setErrors(prev => ({ ...prev, [field]: '' }));
      return;
    }
    setErrors(prev => ({ ...prev, [field]: validators[field](value) }));
  };

  const validateForm = () => {
    const newErrors = {} as Record<keyof T, string>;
    for (const field in formData) {
      newErrors[field] = validators[field](formData[field]);
    }
    setErrors(newErrors);
    return Object.values(newErrors).every(error => error === '');
  };

  const setAllTouched = () => {
    const allTouched = {} as Record<keyof T, boolean>;
    for (const field in formData) {
      allTouched[field] = true;
    }
    setTouched(allTouched);
  };

  return { 
    formData, 
    errors, 
    touched, 
    handleBlur, 
    handleChange, 
    validateForm,
    setAllTouched
  };
};