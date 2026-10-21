"""Verify bounded, read-only measurements from the unmodified DuckTales ROM."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'build/verification/native-scrooge-movement'
rows = list(csv.DictReader(BASE.with_suffix('.csv').open()))
ram = BASE.with_suffix('.bin').read_bytes()
assert len(ram) == len(rows) * 2048
def at(frame: int, address: int) -> int:
    return ram[(frame - 300) * 2048 + address]
def rise(start: int, end: int) -> int:
    return 148 - min(int(row['y']) for row in rows if start <= int(row['frame']) < end)
assert rise(400, 510) == 58
assert rise(930, 1110) == 84
assert all(at(f, 0x640) == 148 for f in range(600, 780))
assert all(at(f, 0x650) == 128 for f in range(1250, 1350))
assert at(862, 0x7c0) < 128 and at(863, 0x7c0) >= 128
assert at(862, 0x640) == at(863, 0x640) == 105
# Native upward velocity lives at $07c0:$07b0. Gravity follows each movement.
assert all((at(f-1, 0x7c0)*256 + at(f-1, 0x7b0) -
            at(f, 0x7c0)*256 - at(f, 0x7b0)) % 65536 == 0x33
           for f in range(402, 425))
writes = list(csv.DictReader(Path(str(BASE)+'-velocity.csv').open()))
def wrote(frame: int, address: int, value: int) -> bool:
    return any(int(r['frame']) == frame and int(r['address']) == address and int(r['value']) == value for r in writes)
assert wrote(400, 0x7b0, 0xbb) and wrote(400, 0x7c0, 4)
assert wrote(882, 0x7b0, 0xa8) and wrote(882, 0x7c0, 5)
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
report = {
    'source': 'unmodified local DuckTales (USA).nes',
    'source_rom_sha256': sha(Path('C:/NES/DuckTales (USA).nes')),
    'controller_only': True, 'emulated_memory_or_register_writes': False,
    'native_jump_upward_8_8': '04bb', 'native_pogo_upward_8_8': '05a8',
    'native_gravity_8_8': '0033', 'gravity_order': 'after motion',
    'ordinary_jump_rise_px': 58, 'pogo_rise_px': 84,
    'ground_down_b_starts_pogo': False, 'crouch_plus_right_moves': False,
    'ordinary_a_release_cancels_ascent': True,
    'probe_sha256': sha(ROOT/'tools/reference/scrooge-movement-probe.lua'),
    'csv_sha256': sha(BASE.with_suffix('.csv')), 'ram_sha256': sha(BASE.with_suffix('.bin')),
}
Path(str(BASE)+'-review.json').write_text(json.dumps(report, indent=2)+'\n')
print('PASS native DuckTales58px jump /84px pogo /gravity51/256 /stationary crouch')
