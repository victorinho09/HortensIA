from dataclasses import dataclass

from backend.ai.yolo.detection_zone import DetectionZone
from backend.models.websocket import AlertSeverity,DetectedObject

DEFAULT_TOP_ZONE_FACTOR = 0.25
DEFAULT_CENTER_ZONE_FACTOR = 0.60
DEFAULT_BOTTOM_ZONE_FACTOR = 1.00

# DEFAULT_OBJECT_SEMANTIC_WEIGHT = 0.55
# DEFAULT_OBJECT_PROXIMITY_WEIGHT = 0.25
# DEFAULT_OBJECT_MOTION_WEIGHT = 0.20

DEFAULT_PROXIMITY_SIZE_WEIGHT = 0.60
DEFAULT_PROXIMITY_ZONE_WEIGHT = 0.40

DEFAULT_MOTION_APPROACH_WEIGHT = 0.80
DEFAULT_MOTION_BOOLEAN_WEIGHT = 0.20

DEFAULT_APPROACH_START_RATIO = 1.20
DEFAULT_APPROACH_SATURATION_RATIO = 1.80

DEFAULT_SCENE_SMOOTHING_ALPHA = 0.35
DEFAULT_WARNING_THRESHOLD = 0.35
DEFAULT_CRITICAL_THRESHOLD = 0.70

ZONE_FACTORS: dict[DetectionZone, float] = {
    DetectionZone.TOP: DEFAULT_TOP_ZONE_FACTOR,
    DetectionZone.CENTER: DEFAULT_CENTER_ZONE_FACTOR,
    DetectionZone.BOTTOM: DEFAULT_BOTTOM_ZONE_FACTOR,
}

# Motion analysis parameters
@dataclass(frozen=True)
class SceneRiskScore:
    detections: list[DetectedObject]
    instant_risk: float
    smoothed_risk: float
    severity: AlertSeverity
    dominant_object_index: int | None
    dominant_track_id: int | None
    dominant_class_name: str | None

# Helper function to clip values between 0 and 1
def _clip(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))

def get_zone_factor(zone: DetectionZone) -> float:
    try:
        return ZONE_FACTORS[zone]
    except KeyError as exc:
        raise ValueError(f"Unsupported detection zone: {zone}") from exc

# Calculate the approach factor based on area growth and track stability
def calculate_approach_factor(
        area_growth_ratio_2s: float | None,
        is_track_stable: bool,
        start_ratio: float = DEFAULT_APPROACH_START_RATIO,
        saturation_ratio: float = DEFAULT_APPROACH_SATURATION_RATIO,
) -> float:
    if saturation_ratio <= start_ratio:
        raise ValueError("Saturation ratio must be greater than start ratio.")
    if area_growth_ratio_2s is None or not is_track_stable:
        return 0.0
    
    normalized_growth = (area_growth_ratio_2s - start_ratio) / (saturation_ratio - start_ratio)
    return _clip(normalized_growth)

# Main function to calculate motion factor for a detection
def calculate_motion_factor(detection: DetectedObject) -> float:
    if not detection.is_track_stable:
        return 0.0
    
    approach_factor = calculate_approach_factor(
        area_growth_ratio_2s=detection.area_growth_ratio_2s,
        is_track_stable=detection.is_track_stable,
    )
    boolean_component = 1.0 if detection.is_approaching else 0.0

    motion_factor = (
        DEFAULT_MOTION_APPROACH_WEIGHT * approach_factor +
        DEFAULT_MOTION_BOOLEAN_WEIGHT * boolean_component
    )
    return _clip(motion_factor)

# Calculate the proximity factor for a detection based on its size and zone
def calculate_proximity_factor(detection: DetectedObject) -> float:
    zone_factor = get_zone_factor(detection.zone)
    proximity_factor = (
        DEFAULT_PROXIMITY_SIZE_WEIGHT * detection.size_factor +
        DEFAULT_PROXIMITY_ZONE_WEIGHT * zone_factor
    )
    return _clip(proximity_factor)

# Calculate the overall risk for a single detected object by combining semantic, proximity, and motion factors
def calculate_object_risk(detection: DetectedObject) -> float:
    semantic_factor = detection.effective_risk_weight
    proximity_factor = calculate_proximity_factor(detection=detection)
    motion_factor = calculate_motion_factor(detection=detection)

    activation_factor = max(proximity_factor,motion_factor)

    return _clip(detection.confidence * semantic_factor * activation_factor)

# Combine individual object risks into an overall scene risk score using a probabilistic model that assumes independence between objects
def calculate_scene_risk(object_risks: list[float]) -> float:
    survival_probability = 1.0
    for object_risk in object_risks:
        survival_probability *= 1.0 - _clip(object_risk)
    return _clip(1.0 - survival_probability)

class SceneRiskAnalyzer:
    def __init__(
            self,
            smoothing_alpha: float = DEFAULT_SCENE_SMOOTHING_ALPHA,
            warning_threshold: float = DEFAULT_WARNING_THRESHOLD,   
            critical_threshold: float = DEFAULT_CRITICAL_THRESHOLD,
    ) -> None:
        if not 0.0 < smoothing_alpha <= 1.0:
            raise ValueError("Smoothing alpha must be in the range (0, 1].")
        if not 0.0 <= warning_threshold < critical_threshold <= 1.0:
            raise ValueError("Thresholds must satisfy 0 <= warning < critical <= 1.")
        self._smoothing_alpha = smoothing_alpha
        self._warning_threshold = warning_threshold
        self._critical_threshold = critical_threshold
        self._previous_smoothed_risk = 0.0

    def assess_detections(self, detections: list[DetectedObject]) -> SceneRiskScore:
        scored_detections: list[DetectedObject] = []
        object_risks: list[float] = []

        for detection in detections:
            object_risk = calculate_object_risk(detection=detection)
            scored_detections.append(
                detection.model_copy(update={"object_risk": object_risk})
            )
            object_risks.append(object_risk)
        
        instant_risk = calculate_scene_risk(object_risks=object_risks)
        smoothed_risk = self._smooth_risk(instant_risk=instant_risk)
        dominant_object_index = self._resolve_dominant_object_index(object_risks=object_risks)

        dominant_object = (
            scored_detections[dominant_object_index]
            if dominant_object_index is not None else None
        )
        return SceneRiskScore(
            detections=scored_detections,
            instant_risk=instant_risk,
            smoothed_risk=smoothed_risk,
            severity=self._resolve_severity(
                instant_risk=instant_risk,
                smoothed_risk=smoothed_risk,
            ),
            dominant_object_index=dominant_object_index,
            dominant_track_id=dominant_object.track_id if dominant_object is not None else None,
            dominant_class_name=dominant_object.class_name if dominant_object is not None else None,
        )
    
    def _smooth_risk(self, instant_risk: float) -> float:
        smoothed_risk = (
            self._smoothing_alpha * instant_risk +
            (1.0 - self._smoothing_alpha) * self._previous_smoothed_risk
        )
        self._previous_smoothed_risk = smoothed_risk
        return _clip(smoothed_risk)
    
    def _resolve_dominant_object_index(self, object_risks: list[float]) -> int | None:
        if not object_risks:
            return None
        return max(range(len(object_risks)), key=object_risks.__getitem__)
    
    def _resolve_severity(self, instant_risk: float, smoothed_risk: float) -> AlertSeverity:
        if instant_risk >= self._critical_threshold:
            return AlertSeverity.CRITICAL
        if smoothed_risk >= self._warning_threshold:
            return AlertSeverity.WARNING
        return AlertSeverity.INFO