import React, { useEffect, useMemo, useRef } from 'react';
import { Animated, Easing, Text } from 'react-native';
import { DetectedObject } from '../../hooks/useLiveSession';
import { styles } from '../styles/BoundingBox.styles';

interface BoundingBoxProps {
  detection: DetectedObject;
  frameWidth: number;
  frameHeight: number;
}

function BoundingBoxComponent({ detection, frameWidth, frameHeight }: BoundingBoxProps) {
  const { bbox, class_name, confidence, track_id } = detection;
  const label = track_id !== null ? `${class_name} #${track_id}` : class_name;

  const [x1, y1, x2, y2] = bbox;

  const metrics = useMemo(
    () => ({
      left: x1 * frameWidth,
      top: y1 * frameHeight,
      width: (x2 - x1) * frameWidth,
      height: (y2 - y1) * frameHeight,
    }),
    [frameHeight, frameWidth, x1, x2, y1, y2]
  );

  return (
    <Animated.View
      style={[
        styles.box,
        {
          left: metrics.left,
          top: metrics.top,
          width: metrics.width,
          height: metrics.height,
        },
      ]}
    >
      <Animated.View style={styles.label}>
        <Text style={styles.labelText}>
          {label} {(confidence * 100).toFixed(0)}%
        </Text>
      </Animated.View>
    </Animated.View>
  );
}

export const BoundingBox = React.memo(BoundingBoxComponent, (previousProps, nextProps) => {
  return (
    previousProps.frameWidth === nextProps.frameWidth &&
    previousProps.frameHeight === nextProps.frameHeight &&
    previousProps.detection.class_name === nextProps.detection.class_name &&
    previousProps.detection.track_id === nextProps.detection.track_id &&
    previousProps.detection.confidence === nextProps.detection.confidence &&
    previousProps.detection.bbox.every(
      (value, index) => value === nextProps.detection.bbox[index]
    )
  );
});
