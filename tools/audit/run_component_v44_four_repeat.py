"""Repeat the default-off four-Goomba walking arena on the exact43/44 ROMs."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
for version, tag, checkpoint in (
    ('v43', 'buffer44-four-repeat-before-a', 'roster-audit-v43'),
    ('v44a', 'buffer44-four-repeat-after-a', 'roster-audit-v44-provisional-a'),
):
    subprocess.run([sys.executable, 'tools/profiling/profile_plain_walking.py',
        version, '--tag', tag, '--characters', '2,1,9', '--mappers', 'mmc5',
        '--source', 'tools/profiling/plain_walking_four_repeat_v42.lua',
        '--checkpoint', str(ROOT / 'build/checkpoints' / checkpoint)], cwd=ROOT, check=True)
subprocess.run([sys.executable, 'tools/profiling/compare_plain_walking.py',
    'build/profiling/plain-walking-v43-buffer44-four-repeat-before-a',
    'build/profiling/plain-walking-v44a-buffer44-four-repeat-after-a', '--output',
    'build/verification/plain-walking-v43-v44a-four-repeat-comparison.json'], cwd=ROOT, check=True)
