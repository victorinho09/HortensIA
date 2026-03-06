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

  // Status bar (top)
  statusBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.55)',
    paddingHorizontal: 16,
    paddingVertical: 10,
    gap: 8,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  statusText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 14,
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
  startButton: {
    minWidth: 140,
    borderRadius: 30,
  },
  stopButton: {
    minWidth: 140,
    borderRadius: 30,
    borderColor: '#ef4444',
    backgroundColor: 'rgba(239,68,68,0.2)',
  },

  // Permissions screen
  permissionsContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  permissionsTitle: {
    color: '#fff',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 12,
  },
  permissionsSubtitle: {
    color: '#ccc',
    textAlign: 'center',
    marginBottom: 32,
  },
  permissionStatusRow: {
    flexDirection: 'row',
    gap: 24,
    marginBottom: 32,
  },
  permissionItem: {
    fontSize: 16,
    fontWeight: '600',
  },
  permissionsButton: {
    minWidth: 200,
    borderRadius: 8,
  },
});
