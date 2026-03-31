"""
YOLO detector

Wraps the YOLOv8s model to process a single base64-encoded JSON frame and return a list of detected objects.
The model is loaded once at instantiation (singleton) and reused across all frames.
Device is auto-detecte: MPS on Aplle Silicon, CUDA if available, else CPU.
"""

import base64
import logging
import time
from io import BytesIO

import torch
from PIL import Image
from ultralytics import YOLO

from backend.models.websocket import DetectedObject, calculate_detection_zone
from backend.ai.yolo.coco_taxonomy import calculate_detection_supercategory
from backend.ai.yolo.domestic_risk import assess_detection_risk

logger = logging.getLogger(__name__)

def _resolve_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

class YOLODetector:
    """
    Single-instance YOLO detector.
    Load once, call detect() per frame.
    """

    def __init__(self, model_name: str = "yolo26m.pt") -> None:
        self._device = _resolve_device()
        logger.info("Loading YOLO model '%s' on device '%s'", model_name,self._device)
        self._model = YOLO(model_name)
        self._model.to(self._device)
        logger.info("YOLO model loaded")
    
    def _decode_frame(self, frame_b64: str) -> Image.Image:
        try:
            raw = base64.b64decode(frame_b64)
            return Image.open(BytesIO(raw)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid frame data: {e}")

    def _parse_results(self, results, width: int, height: int) -> list[DetectedObject]:
        detections: list[DetectedObject] = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                normalized_bbox = [x1 / width, y1 / height, x2 / width, y2 / height]
                class_name = result.names[int(box.cls[0])]
                supercategory = calculate_detection_supercategory(class_name)
                risk_assessment = assess_detection_risk(class_name,supercategory)


                detections.append(DetectedObject(
                    class_name=class_name,
                    confidence=float(box.conf[0]),
                    bbox=normalized_bbox,
                    zone=calculate_detection_zone(normalized_bbox),
                    supercategory=calculate_detection_supercategory(class_name),
                    supercategory_risk_level=risk_assessment.supercategory_level,
                    supercategory_risk_weight=risk_assessment.supercategory_weight,
                    effective_risk_level=risk_assessment.effective_level,
                    effective_risk_weight=risk_assessment.effective_weight,
                    risk_source=risk_assessment.source,
                ))
        return detections               

    def detect(self, frame_b64: str) -> tuple[list[DetectedObject], float]:
        """
        Run inference on a base64-encoded JPEG frame.

        Returns:
            - List of DetectedObject (class name, confidence, bbox normalized 0-1)
            - Processing time in milliseconds
        """
        image = self._decode_frame(frame_b64)
        w, h = image.size

        start = time.perf_counter()
        results = self._model(image,device=self._device, verbose= False, conf=0.5)
        elapsed_ms = (time.perf_counter() - start) * 1000

        detections = self._parse_results(results, w, h)
        return detections,elapsed_ms
    
    