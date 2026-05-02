import React, { useEffect, useMemo, useRef } from 'react';
import { Animated, Easing, Text } from 'react-native';
import { DetectedObject } from '../../hooks/useLiveSession';
import { styles } from '../styles/BoundingBox.styles';
import { translateObjectClassName } from '../../utils/objectClassTranslations';


interface BoundingBoxProps {
  detection: DetectedObject;
  frameWidth: number;
  frameHeight: number;
}

function BoundingBoxComponent({ detection, frameWidth, frameHeight }: BoundingBoxProps) {
  const { bbox, class_name,track_id, object_risk } = detection;
  const label = translateObjectClassName(class_name) ?? class_name;
  const riskColors = getRiskColors(object_risk);

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
          borderColor: riskColors.borderColor,
        },
      ]}
    >
      <Animated.View style={[styles.label, { backgroundColor: riskColors.labelBackgroundColor }]}>
        <Text style={[styles.labelText, {color: riskColors.labelTextColor}]}>
          {label}
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
    previousProps.detection.object_risk === nextProps.detection.object_risk &&
    previousProps.detection.confidence === nextProps.detection.confidence &&
    previousProps.detection.bbox.every(
      (value, index) => value === nextProps.detection.bbox[index]
    )
  );
});

function getRiskColors(objectRisk: number | null) {
  if (objectRisk === null) {
    return {
      borderColor: '#94a3b8',
      labelBackgroundColor: 'rgba(148, 163, 184, 0.85)',
      labelTextColor: '#0f172a',
    };
  }

  if (objectRisk >= 0.70) {
    return {
      borderColor: '#ef4444',
      labelBackgroundColor: 'rgba(239, 68, 68, 0.88)',
      labelTextColor: '#ffffff',
    };
  }

  if (objectRisk >= 0.35) {
    return {
      borderColor: '#f59e0b',
      labelBackgroundColor: 'rgba(245, 158, 11, 0.88)',
      labelTextColor: '#111827',
    };
  }

  return {
    borderColor: '#22c55e',
    labelBackgroundColor: 'rgba(34, 197, 94, 0.88)',
    labelTextColor: '#052e16',
  };
}