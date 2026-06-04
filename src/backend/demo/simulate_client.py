"""
Demo WebSocket simulator client.

Simulates the mobile app for the TFG jury: instead of streaming frames from an
iPhone camera, it reads images stored on the server (the ``samples/`` folder),
encodes them exactly like the real client (JPEG -> base64) and sends them to the
live-session WebSocket endpoint. The detection + risk-assessment responses are
printed to the console in a human-readable table.

Designed to be run against the dockerized server in demo mode
(``HORTENSIA_DEMO_MODE=1``), where session validation is skipped.

Usage:
    python -m backend.demo.simulate_client
    python -m backend.demo.simulate_client --url ws://localhost:8888 --samples ./samples
    python -m backend.demo.simulate_client --repeat 5 --delay 0.3

Environment variables (used as defaults):
    SERVER_WS_URL   Base WebSocket URL of the server (default ws://localhost:8888)
    SAMPLES_DIR     Directory containing the sample images
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import time
import uuid
from io import BytesIO
from pathlib import Path

try:
    import websockets
except ImportError as exc:  # pragma: no cover - clearer message for the jury
    raise SystemExit(
        "The 'websockets' package is required. Install it with:\n"
        "    pip install -r backend/demo/requirements.txt"
    ) from exc

from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
DEFAULT_SAMPLES_DIR = Path(__file__).resolve().parent / "samples"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _encode_image_to_jpeg_b64(path: Path) -> str:
    """Load an image from disk and return it as a base64-encoded JPEG string."""
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        buffer = BytesIO()
        rgb.save(buffer, format="JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _discover_images(samples_dir: Path) -> list[Path]:
    if not samples_dir.exists():
        raise SystemExit(f"Samples directory does not exist: {samples_dir}")
    images = sorted(
        p for p in samples_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not images:
        raise SystemExit(
            f"No images found in {samples_dir}.\n"
            f"Drop some .jpg/.png files there and run the simulator again."
        )
    return images


def _build_frame_message(frame_b64: str) -> str:
    """Build a FrameMessage JSON payload matching the server's protocol."""
    now = _now_ms()
    telemetry = {
        "frame_id": str(uuid.uuid4()),
        "capture_started_at": now,
        "capture_finished_at": now,
        "encode_finished_at": now,
        "sent_at": now,
    }
    message = {
        "type": "frame",
        "data": frame_b64,
        "timestamp": float(now),
        "telemetry": telemetry,
    }
    return json.dumps(message)


def _print_detection(label: str, payload: dict) -> None:
    """Pretty-print a DetectionMessage payload."""
    objects = payload.get("objects", [])
    scene = payload.get("scene_risk") or {}
    processing = payload.get("procesing_ms")

    print()
    print("=" * 72)
    header = f"  {label}"
    if processing is not None:
        header += f"   (processing: {processing:.1f} ms)"
    print(header)
    print("=" * 72)

    if not objects:
        print("  No objects detected.")
    else:
        print(
            f"  {'#':>2}  {'class':<16}{'conf':>6}  {'zone':<8}"
            f"{'dom_risk':<10}{'obj_risk':>9}  {'approaching':>11}"
        )
        print("  " + "-" * 66)
        for idx, obj in enumerate(objects):
            obj_risk = obj.get("object_risk")
            obj_risk_str = f"{obj_risk:.3f}" if obj_risk is not None else "  -  "
            print(
                f"  {idx:>2}  "
                f"{obj.get('class_name', '?'):<16}"
                f"{obj.get('confidence', 0.0):>6.2f}  "
                f"{str(obj.get('zone', '?')):<8}"
                f"{str(obj.get('effective_risk_level', '?')):<10}"
                f"{obj_risk_str:>9}  "
                f"{str(bool(obj.get('is_approaching'))):>11}"
            )

    if scene:
        print("  " + "-" * 66)
        print(
            f"  SCENE RISK  ->  instant: {scene.get('instant', 0.0):.3f}   "
            f"smoothed: {scene.get('smoothed', 0.0):.3f}   "
            f"severity: {str(scene.get('severity', '?')).upper()}"
        )
        dominant = scene.get("dominant_class_name")
        if dominant:
            print(f"  Dominant object: {dominant}")


async def _receive_until_detection(websocket) -> dict | None:
    """Read server messages until a detection arrives (skips status messages)."""
    while True:
        raw = await websocket.recv()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        msg_type = payload.get("type")
        if msg_type == "detection":
            return payload
        if msg_type == "error":
            print(f"  [server error] {payload.get('message')} ({payload.get('code')})")
            return None
        if msg_type == "status":
            print(f"  [server status] {payload.get('status')}: {payload.get('message')}")
            # keep waiting for the detection that follows this status update
            if payload.get("status") == "connected":
                return "__connected__"  # type: ignore[return-value]


async def run(url: str, samples_dir: Path, repeat: int, delay: float) -> None:
    images = _discover_images(samples_dir)
    base_url = url.rstrip('/')
    print(f"Server: {base_url}")
    print(f"Found {len(images)} image(s) in {samples_dir}")
    print(f"Repeat per image: {repeat}   delay between frames: {delay}s")
    # Each image gets its own WebSocket connection so the SceneRiskAnalyzer
    # starts with a clean smoothed-risk state per image. The --repeat frames
    # of the same image still share a connection, which is what we want for
    # temporal tracking to accumulate correctly.
    for image_path in images:
        frame_b64 = _encode_image_to_jpeg_b64(image_path)
        endpoint = f"{base_url}/ws/live/{uuid.uuid4()}"
        async with websockets.connect(endpoint, max_size=None) as websocket:
            # Drain the initial 'connected' status message emitted by the server.
            result = await _receive_until_detection(websocket)
            if result != "__connected__":
                print("  [warning] did not receive the expected 'connected' status")

            for attempt in range(1, repeat + 1):
                label = image_path.name
                if repeat > 1:
                    label = f"{image_path.name}  (frame {attempt}/{repeat})"

                await websocket.send(_build_frame_message(frame_b64))
                detection = await _receive_until_detection(websocket)
                if detection and detection != "__connected__":
                    _print_detection(label, detection)

                if delay > 0 and attempt < repeat:
                    await asyncio.sleep(delay)

    print()
    print("Done. All sample frames have been processed.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HortensIA detection WebSocket simulator")
    parser.add_argument(
        "--url",
        default=os.getenv("SERVER_WS_URL", "ws://localhost:8888"),
        help="Base WebSocket URL of the server (default: %(default)s)",
    )
    parser.add_argument(
        "--samples",
        type=Path,
        default=Path(os.getenv("SAMPLES_DIR", str(DEFAULT_SAMPLES_DIR))),
        help="Directory with sample images (default: %(default)s)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="How many times to send each image (useful to exercise temporal tracking)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay in seconds between consecutive frames (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        asyncio.run(run(args.url, args.samples, max(args.repeat, 1), max(args.delay, 0.0)))
    except KeyboardInterrupt:
        print("\nInterrupted.")


if __name__ == "__main__":
    main()
