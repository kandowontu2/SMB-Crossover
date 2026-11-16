"""Read-only authored 1UP placement census on the actual current image."""
from hashlib import sha256
from pathlib import Path
import json
import re

R = Path(__file__).resolve().parents[2]
PIN = '7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
LEVELS_SHA = 'ccfeacb8766a401c1fee7ce70125c8c3981e002855345c68a468e0748b0d1ece'
H = lambda value: sha256(value).hexdigest()


def inspect(raw):
    assert H(raw) == PIN
    source = (R/'src/level_tiles.s').read_bytes()
    assert H(source) == LEVELS_SHA
    rows = []
    stage = label = None
    data = bytearray()
    def finish():
        if not label or not data or data[-1] != 253:
            return
        blob = bytes(data)
        page = 0
        for offset in range(2, len(blob)-1, 2):
            a, b = blob[offset:offset+2]
            row = a & 15
            if b & 128:
                page += 1
            if row == 13 and not b & 64:
                page = b & 31
                continue
            if row >= 12 or b & 112 or b & 15 not in (3, 8):
                continue
            occurrences = raw.count(blob)
            assert occurrences == 1, (stage, label, occurrences)
            rows.append(dict(stage=stage, label=label, kind='hidden1UP' if b & 15 == 3 else 'brick1UP',
                             x=page*256+(a>>4)*16, y=32+row*16, object_hex=blob[offset:offset+2].hex(),
                             source_offset=offset, ROM_file=raw.find(blob), level_SHA256=H(blob)))
    for line in source.decode().splitlines():
        if line.startswith(';level '):
            stage = line[len(';level '):].strip()
        found = re.match(r'^(L_(?:Ground|Underground)Area\d+):', line)
        if found:
            finish()
            label, data = found[1], bytearray()
        elif label:
            if '.byte' in line:
                data.extend(int(v, 16) for v in re.findall(r'\$([\da-fA-F]{2})', line.split(';')[0]))
                if data and data[-1] == 253:
                    finish()
                    label, data = None, bytearray()
            elif re.match(r'^[A-Za-z_][A-Za-z_0-9]*:', line):
                label, data = None, bytearray()
    known = [q for q in rows if q['label'] == 'L_GroundArea6' and q['kind'] == 'hidden1UP']
    assert len(known) == 1 and (known[0]['x'], known[0]['y']) == (1024, 128)
    report = dict(passed=True, actual_ROM_SHA256=PIN, level_source_SHA256=LEVELS_SHA,
                  rows=rows, gameplay_executed=False, outputs=0,
                  scope='Authenticated authored coordinates only; nearby supports, rendering, input and reach remain unqualified')
    report['receipt_SHA256'] = H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    return report


if __name__ == '__main__':
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    print('RESULT '+json.dumps(inspect(raw), separators=(',', ':')), flush=True)
