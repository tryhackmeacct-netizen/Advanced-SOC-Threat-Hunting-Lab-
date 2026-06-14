import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))

from app.services.detection_engine import DetectionEngine


def load_sample_events():
    p = Path('sample-logs') / 'mixed_events.json'
    evs = []
    with open(p, 'r', encoding='utf-8') as fh:
        for line in fh:
            evs.append(json.loads(line))
    # normalize using app.ingestion.normalizer
    from app.ingestion.normalizer import normalize
    return [normalize(e) for e in evs]


def test_detection_against_samples():
    events = load_sample_events()
    engine = DetectionEngine()
    cnt = engine.run_once(sigma_dir=Path('sigma-rules'), dry_run_events=events)
    print('Detection engine created alert count (dry_run):', cnt)
    assert cnt >= 1


if __name__ == '__main__':
    test_detection_against_samples()
