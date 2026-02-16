import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

const HomeSpecificStyles = StyleSheet.create({
  container: {
    ...commonStyles.container,
    justifyContent: 'center',
  },
  content: {
    ...commonStyles.content,
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center',
  },
  title: {
    ...commonStyles.title,
    fontSize: 32,
  },
});

export const styles = {
  ...commonStyles,
  ...HomeSpecificStyles,
};
