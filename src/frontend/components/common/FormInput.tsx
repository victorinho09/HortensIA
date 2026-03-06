import React, { forwardRef } from 'react';
import { StyleProp, ViewStyle } from 'react-native';
import { TextInput, HelperText } from 'react-native-paper';

interface FormInputProps {
  // Core
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  onBlur?: () => void;

  // Validation
  touched?: boolean;
  errorMessage?: string;
  showInlineError?: boolean; // default true — set false when error is rendered externally

  // Accessibility (required — prevents forgetting)
  accessibilityLabel: string;
  accessibilityHint: string;

  // Left icon
  icon?: string;

  // Secure text (password fields)
  secureTextEntry?: boolean;
  showSecureToggle?: boolean;
  isSecureVisible?: boolean;
  onToggleSecure?: () => void;

  // Keyboard behavior
  keyboardType?: React.ComponentProps<typeof TextInput>['keyboardType'];
  autoCapitalize?: React.ComponentProps<typeof TextInput>['autoCapitalize'];
  autoComplete?: React.ComponentProps<typeof TextInput>['autoComplete'];
  textContentType?: React.ComponentProps<typeof TextInput>['textContentType'];
  returnKeyType?: React.ComponentProps<typeof TextInput>['returnKeyType'];
  submitBehavior?: 'submit' | 'blurAndSubmit' | 'newline';
  onSubmitEditing?: () => void;

  // Other
  placeholder?: string;
  disabled?: boolean;
  style?: StyleProp<ViewStyle>;
}

const FormInput = forwardRef<any, FormInputProps>(
  (
    {
      label,
      value,
      onChangeText,
      onBlur,
      touched,
      errorMessage,
      showInlineError = true,
      accessibilityLabel,
      accessibilityHint,
      icon,
      secureTextEntry,
      showSecureToggle,
      isSecureVisible,
      onToggleSecure,
      keyboardType,
      autoCapitalize,
      autoComplete,
      textContentType,
      returnKeyType,
      submitBehavior,
      onSubmitEditing,
      placeholder,
      disabled,
      style,
    },
    ref
  ) => {
    const hasError = !!(touched && errorMessage);

    return (
      <>
        <TextInput
          ref={ref}
          label={label}
          value={value}
          onChangeText={onChangeText}
          onBlur={onBlur}
          mode="outlined"
          placeholder={placeholder}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
          autoComplete={autoComplete}
          textContentType={textContentType}
          secureTextEntry={secureTextEntry}
          returnKeyType={returnKeyType}
          submitBehavior={submitBehavior}
          onSubmitEditing={onSubmitEditing}
          disabled={disabled}
          error={hasError}
          left={icon ? <TextInput.Icon icon={icon} /> : undefined}
          right={
            showSecureToggle ? (
              <TextInput.Icon
                icon={isSecureVisible ? 'eye-off' : 'eye'}
                onPress={onToggleSecure}
                accessibilityLabel={isSecureVisible ? 'Hide password' : 'Show password'}
                accessibilityHint="Toggle password visibility"
                accessibilityRole="button"
              />
            ) : undefined
          }
          style={style}
          accessibilityLabel={accessibilityLabel}
          accessibilityHint={accessibilityHint}
          accessibilityRole="text"
        />
        {showInlineError && hasError && (
          <HelperText
            type="error"
            visible={hasError}
            accessible={true}
            accessibilityLabel={`${accessibilityLabel} error`}
            accessibilityLiveRegion="polite"
          >
            {errorMessage}
          </HelperText>
        )}
      </>
    );
  }
);

FormInput.displayName = 'FormInput';

export default FormInput;
