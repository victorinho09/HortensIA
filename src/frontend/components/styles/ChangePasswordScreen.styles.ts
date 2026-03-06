import { StyleSheet } from 'react-native';
import { commonStyles } from './common.styles';

export const styles = {
  ...commonStyles,
  ...StyleSheet.create({
    content: {
      ...commonStyles.content,
      flexGrow: 1,
      justifyContent: 'center' as const,
      padding: 24,
    },
    subtitle: {
      ...commonStyles.subtitle,
      fontSize: 18,
      marginBottom: 32,
    },
  }),
};
