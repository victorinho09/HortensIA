import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
    width: '100%',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'space-between',
  },

  // Status bar (top-left corner)
  statusBar: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: 16,
    paddingVertical: 10,
    gap: 8,
  },
  statusDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
  },
  statusText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 18,
  },
  errorText: {
    color: '#ef4444',
    fontSize: 12,
    flex: 1,
  },

  // Live indicators (top-right)
  indicators: {
    position: 'absolute',
    top: 52,
    right: 12,
    gap: 6,
    alignItems: 'flex-end',
  },
  indicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 14,
    gap: 5,
  },
  indicatorText: {
    color: '#fff',
    fontSize: 12,
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ef4444',
  },

  // Controls (bottom)
  controls: {
    paddingBottom: 40,
    alignItems: 'center',
  },
  captureButtonContainer: {
    width: 84,
    height: 84,
    borderRadius: 42,
    borderWidth: 4,
    borderColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButtonInner: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#fff',
  },
  captureButtonInnerActive: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#ef4444',
  },
});
