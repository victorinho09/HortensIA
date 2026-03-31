import React, { useEffect, useMemo, useRef } from 'react';
import { Animated, Easing, Text } from 'react-native';
import { DetectedObject } from '../../hooks/useLiveSession';
import { styles } from '../styles/BoundingBox.styles';

interface BoundingBoxProps {
  detection: DetectedObject;
  frameWidth: number;
  frameHeight: number;
}

const RERENDER_POSITION_DELTA = 0.02;
const RERENDER_CONFIDENCE_DELTA = 0.05;

function BoundingBoxComponent({ detection, frameWidth, frameHeight }: BoundingBoxProps) {
  const { bbox, class_name, confidence } = detection;

  // bbox is an array [x1, y1, x2, y2] normalized [0-1] in landscape orientation
  // Photo is captured in landscape (4224x2376) but preview is portrait (393x705)
  // We need to rotate 90° clockwise
  const [x1_land, y1_land, x2_land, y2_land] = bbox;

  // Rotate 90° clockwise transformation:
  // x_portrait = 1 - y_landscape, y_portrait = x_landscape
  const x1 = 1 - y2_land;
  const y1 = x1_land;
  const x2 = 1 - y1_land;
  const y2 = x2_land;

  const metrics = useMemo(
    () => ({
      left: x1 * frameWidth,
      top: y1 * frameHeight,
      width: (x2 - x1) * frameWidth,
      height: (y2 - y1) * frameHeight,
    }),
    [frameHeight, frameWidth, x1, x2, y1, y2]
  );

  const leftAnim = useRef(new Animated.Value(metrics.left)).current;
  const topAnim = useRef(new Animated.Value(metrics.top)).current;
  const widthAnim = useRef(new Animated.Value(metrics.width)).current;
  const heightAnim = useRef(new Animated.Value(metrics.height)).current;
  const opacityAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(leftAnim, {
        toValue: metrics.left,
        duration: 120,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: false,
      }),
      Animated.timing(topAnim, {
        toValue: metrics.top,
        duration: 120,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: false,
      }),
      Animated.timing(widthAnim, {
        toValue: metrics.width,
        duration: 120,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: false,
      }),
      Animated.timing(heightAnim, {
        toValue: metrics.height,
        duration: 120,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: false,
      }),
    ]).start();
  }, [
    heightAnim,
    leftAnim,
    metrics.height,
    metrics.left,
    metrics.top,
    metrics.width,
    topAnim,
    widthAnim,
  ]);

  return (
    <Animated.View
      style={[
        styles.box,
        {
          left: leftAnim,
          top: topAnim,
          width: widthAnim,
          height: heightAnim,
          opacity: opacityAnim,
        },
      ]}
    >
      <Animated.View style={styles.label}>
        <Text style={styles.labelText}>
          {class_name} {(confidence * 100).toFixed(0)}%
        </Text>
      </Animated.View>
    </Animated.View>
  );
}

export const BoundingBox = React.memo(BoundingBoxComponent, (previousProps, nextProps) => {
  if (
    previousProps.frameWidth !== nextProps.frameWidth ||
    previousProps.frameHeight !== nextProps.frameHeight ||
    previousProps.detection.class_name !== nextProps.detection.class_name
  ) {
    return false;
  }

  const hasSameConfidence =
    Math.abs(previousProps.detection.confidence - nextProps.detection.confidence) <=
    RERENDER_CONFIDENCE_DELTA;
  const hasSamePosition = previousProps.detection.bbox.every(
    (value, index) => Math.abs(value - nextProps.detection.bbox[index]) <= RERENDER_POSITION_DELTA
  );

  return hasSameConfidence && hasSamePosition;
});
