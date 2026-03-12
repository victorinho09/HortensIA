import React from 'react';
import { View, Text } from 'react-native';
import { DetectedObject } from '../../hooks/useLiveSession';
import { styles } from '../styles/BoundingBox.styles'; // AÑADIR ESTA LÍNEA

interface BoundingBoxProps {
  detection: DetectedObject;
  frameWidth: number;
  frameHeight: number;
}

export function BoundingBox({ detection, frameWidth, frameHeight }: BoundingBoxProps) {
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

  // Convert normalized coordinates to pixel coordinates
  const left = x1 * frameWidth;
  const top = y1 * frameHeight;
  const width = (x2 - x1) * frameWidth;
  const height = (y2 - y1) * frameHeight;

  // Debug log
  console.log(`[BoundingBox] ${class_name}:`, {
    bbox_landscape: bbox,
    bbox_portrait: [x1, y1, x2, y2],
    frameWidth,
    frameHeight,
    computed: {
      left: left.toFixed(1),
      top: top.toFixed(1),
      width: width.toFixed(1),
      height: height.toFixed(1),
    },
  });

  return (
    <View
      style={[
        styles.box,
        {
          left,
          top,
          width,
          height,
        },
      ]}
    >
      <View style={styles.label}>
        <Text style={styles.labelText}>
          {class_name} {(confidence * 100).toFixed(0)}%
        </Text>
      </View>
    </View>
  );
}
