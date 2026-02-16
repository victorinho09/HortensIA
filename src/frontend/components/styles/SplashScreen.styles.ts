import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

const SplashSpecificStyles = StyleSheet.create({
  container: {
    ...commonStyles.container,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  text: {
    marginTop: 16,
  },
});

export const styles = {
  ...commonStyles,
  ...SplashSpecificStyles,
};
