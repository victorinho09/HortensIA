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

from backend.ai.yolo.scene_risk import SceneRiskAnalyzer
from backend.models.websocket import DetectedObject, SceneRiskAssessment
from backend.ai.yolo.coco_taxonomy import calculate_detection_supercategory
from backend.ai.yolo.domestic_risk import assess_detection_risk
from backend.ai.yolo.object_size import assess_detection_size
from backend.ai.yolo.detection_zone import calculate_detection_zone
from backend.ai.yolo.track_motion import TrackMotionAnalyzer

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

    def __init__(self, model_name: str = "yolo26s.pt",tracker_config: str = "bytetrack.yaml",) -> None:
        self._device = _resolve_device()
        self._tracker_config = tracker_config
        self._track_motion_analyzer = TrackMotionAnalyzer()
        self._scene_risk_analyzer = SceneRiskAnalyzer()
        logger.info("Loading YOLO model '%s' on device '%s'", model_name,self._device)
        self._model = YOLO(model_name)
        self._model.to(self._device)
        logger.info("YOLO model loaded")

    def _track_frame(self, image: Image.Image):
        return self._model.track(
            source=image,
            device=self._device,
            verbose = False,
            conf = 0.1,
            persist=True,
            imgsz=960,
            tracker = self._tracker_config,
        )
    
    def _decode_frame(self, frame_b64: str) -> Image.Image:
        try:
            raw = base64.b64decode(frame_b64)
            return Image.open(BytesIO(raw)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid frame data: {e}")

    def _parse_results(self, results, width: int, height: int,frame_timestamp_ms: float) -> list[DetectedObject]:
        detections: list[DetectedObject] = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                normalized_bbox = [x1 / width, y1 / height, x2 / width, y2 / height]
                class_name = result.names[int(box.cls[0])]
                supercategory = calculate_detection_supercategory(class_name)
                risk_assessment = assess_detection_risk(class_name,supercategory)
                size_assessment = assess_detection_size(normalized_bbox)

                track_id = None
                if getattr(result.boxes, "is_track",False) and box.id is not None:
                    track_id = int(box.id.item())

                motion_assessment = self._track_motion_analyzer.assess_detection_track(
                    track_id=track_id,
                    class_name=class_name,
                    bbox=normalized_bbox,
                    frame_height=height,
                    frame_width=width,
                    timestamp_ms=frame_timestamp_ms,
                )


                detections.append(DetectedObject(
                    class_name=class_name,
                    confidence=float(box.conf[0]),
                    bbox=normalized_bbox,
                    track_id=track_id,
                    zone=calculate_detection_zone(normalized_bbox),
                    supercategory=supercategory,
                    supercategory_risk_level=risk_assessment.supercategory_level,
                    supercategory_risk_weight=risk_assessment.supercategory_weight,
                    effective_risk_level=risk_assessment.effective_level,
                    effective_risk_weight=risk_assessment.effective_weight,
                    risk_source=risk_assessment.source,
                    size_ratio=size_assessment.size_ratio,
                    size_category=size_assessment.category,
                    size_factor=size_assessment.factor,
                    velocity_x_px_s=motion_assessment.velocity_x_px_s,
                    velocity_y_px_s=motion_assessment.velocity_y_px_s,
                    speed_px_s=motion_assessment.speed_px_s,
                    area_growth_ratio_2s=motion_assessment.area_growth_ratio_2s,
                    is_approaching=motion_assessment.is_approaching,
                    track_age_ms=motion_assessment.track_age_ms,
                    is_track_stable=motion_assessment.is_track_stable,
                ))
        return detections               

    def detect(self, frame_b64: str, frame_timestamp_ms: float | None = None) -> tuple[list[DetectedObject], float, SceneRiskAssessment]:
        """
        Run inference on a base64-encoded JPEG frame.
        """
        image = self._decode_frame(frame_b64)
        w, h = image.size
        resolved_frame_timestamp_ms = frame_timestamp_ms if frame_timestamp_ms is not None else time.time() *1000

        start = time.perf_counter()
        results = self._track_frame(image=image)
        elapsed_ms = (time.perf_counter() - start) * 1000

        detections = self._parse_results(results, w, h,resolved_frame_timestamp_ms)
        scene_risk_score = self._scene_risk_analyzer.assess_detections(detections)

        scene_risk = SceneRiskAssessment(
            instant = scene_risk_score.instant_risk,
            smoothed = scene_risk_score.smoothed_risk,
            severity = scene_risk_score.severity,
            dominant_object_index = scene_risk_score.dominant_object_index,
            dominant_track_id = scene_risk_score.dominant_track_id,
            dominant_class_name = scene_risk_score.dominant_class_name,
        )
        return scene_risk_score.detections,elapsed_ms,scene_risk
    
    