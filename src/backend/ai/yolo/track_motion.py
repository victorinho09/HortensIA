from collections import deque
from dataclasses import dataclass

DEFAULT_APPROACH_WINDOW_MS = 2000
DEFAULT_APPROACH_GROWTH_THRESHOLD = 1.20
DEFAULT_TRACK_STABLE_MS = 3000
DEFAULT_TRACK_RETENTION_MS = 5000

@dataclass(frozen=True)
class TrackObservation:
    timestamp_ms: float
    center_x_px: float
    center_y_px: float
    area_px: float

@dataclass(frozen=True)
class TrackMotionAssessment: 
    velocity_x_px_s: float | None
    velocity_y_px_s: float | None
    speed_px_s: float | None
    area_growth_ratio_2s: float | None
    is_approaching: bool
    track_age_ms: float
    is_track_stable: bool

class _TrackState:
    def __init__(self,class_name: str) -> None:
        self.class_name = class_name
        self.observations: deque[TrackObservation] = deque()
        self.first_seen_at_ms: float | None = None
        self.last_seen_at_ms: float | None = None

class TrackMotionAnalyzer:
    def __init__(
            self,
            approach_window_ms: int = DEFAULT_APPROACH_WINDOW_MS,
            approach_growth_threshold: float = DEFAULT_APPROACH_GROWTH_THRESHOLD,
            stable_track_ms: int = DEFAULT_TRACK_STABLE_MS,
            track_retention_ms:int = DEFAULT_TRACK_RETENTION_MS,
    ) -> None:
        self._approach_window_ms = approach_window_ms
        self._approach_growth_threshold = approach_growth_threshold
        self._stable_track_ms = stable_track_ms
        self._track_retention_ms = track_retention_ms
        self._tracks: dict[int, _TrackState] = {}

    def assess_detection_track(
            self,
            track_id: int |None,
            class_name: str,
            bbox: list[float],
            frame_width: int,
            frame_height: int,
            timestamp_ms: float,
    ) -> TrackMotionAssessment:
        if track_id is None:
            return TrackMotionAssessment(
                velocity_x_px_s=None,
                velocity_y_px_s=None,
                speed_px_s=None,
                area_growth_ratio_2s=None,
                is_approaching=False,
                track_age_ms=0.0,
                is_track_stable=False,
            )
        self._evict_stale_tracks(current_timestamp_ms=timestamp_ms)

        track_state = self._tracks.get(track_id)
        if track_state is None or track_state.class_name != class_name:
            track_state = _TrackState(class_name=class_name)
            self._tracks[track_id] = track_state
        
        current_observation = self._build_observation(
            bbox=bbox,
            frame_height = frame_height,
            frame_width = frame_width,
            timestamp_ms = timestamp_ms,
        )

        previous_observation = track_state.observations[-1] if track_state.observations else None
        if track_state.first_seen_at_ms is None:
            track_state.first_seen_at_ms = timestamp_ms
        
        track_state.last_seen_at_ms = timestamp_ms
        track_state.observations.append(current_observation)
        self._trim_history(track_state=track_state,current_timestamp_ms=timestamp_ms)

        velocity_x_px_s, velocity_y_px_s, speed_px_s = self._calculate_velocity(
            previous_observation=previous_observation,
            current_observation=current_observation,
        )

        area_growth_ratio_2s = self._calculate_area_growth_ratio(
            track_state=track_state,
            current_timestamp_ms=timestamp_ms,
        )

        track_age_ms = timestamp_ms - track_state.first_seen_at_ms

        is_approaching = area_growth_ratio_2s is not None and area_growth_ratio_2s >= self._approach_growth_threshold
        is_track_stable = track_age_ms >= self._stable_track_ms

        return TrackMotionAssessment(
            velocity_x_px_s=velocity_x_px_s,
            velocity_y_px_s=velocity_y_px_s,
            speed_px_s=speed_px_s,
            area_growth_ratio_2s=area_growth_ratio_2s,
            is_approaching=is_approaching,
            track_age_ms=track_age_ms,
            is_track_stable=is_track_stable,
        )
    
    def _build_observation(
        self,
        bbox: list[float],
        frame_width: int,
        frame_height: int,
        timestamp_ms: float,
    ) -> TrackObservation:
        x1, y1, x2, y2 = bbox
        center_x_px = ((x1 + x2) / 2.0) * frame_width
        center_y_px = ((y1 + y2) / 2.0) * frame_height
        area_px = max(0.0, (x2 - x1) * frame_width) * max(0.0, (y2 - y1) * frame_height)
        return TrackObservation(
            timestamp_ms=timestamp_ms,
            center_x_px=center_x_px,
            center_y_px=center_y_px,
            area_px=area_px,
        )
    
    def _trim_history(self, track_state: _TrackState, current_timestamp_ms: float) -> None:
        history_cutoff_ms = current_timestamp_ms - max(self._track_retention_ms, self._approach_window_ms)
        while len(track_state.observations) > 1 and track_state.observations[0].timestamp_ms < history_cutoff_ms:
            track_state.observations.popleft()

    def _evict_stale_tracks(self,current_timestamp_ms: float) -> None:
        stale_track_ids = [
            track_id
            for track_id, track_state in self._tracks.items()
            if track_state.last_seen_at_ms is not None
            and current_timestamp_ms - track_state.last_seen_at_ms > self._track_retention_ms
        ]
        for track_id in stale_track_ids:
            del self._tracks[track_id]
    
    def _calculate_velocity(
        self,
        previous_observation: TrackObservation | None,
        current_observation: TrackObservation,
    ) -> tuple[float | None, float | None, float | None]:
        if previous_observation is None:
            return None, None, None

        delta_t_ms = current_observation.timestamp_ms - previous_observation.timestamp_ms
        if delta_t_ms <= 0:
            return None, None, None

        delta_t_s = delta_t_ms / 1000.0
        velocity_x_px_s = (current_observation.center_x_px - previous_observation.center_x_px) / delta_t_s
        velocity_y_px_s = (current_observation.center_y_px - previous_observation.center_y_px) / delta_t_s
        speed_px_s = (velocity_x_px_s ** 2 + velocity_y_px_s ** 2) ** 0.5
        return velocity_x_px_s, velocity_y_px_s, speed_px_s
    
    def _calculate_area_growth_ratio(
        self,
        track_state: _TrackState,
        current_timestamp_ms: float,
    ) -> float | None:
        target_timestamp_ms = current_timestamp_ms - self._approach_window_ms
        reference_observation = None

        for observation in reversed(track_state.observations):
            if observation.timestamp_ms <= target_timestamp_ms:
                reference_observation = observation
                break

        if reference_observation is None or reference_observation.area_px <= 0.0:
            return None

        current_observation = track_state.observations[-1]
        return current_observation.area_px / reference_observation.area_px