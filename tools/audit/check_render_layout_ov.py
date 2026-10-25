"""Require byte confinement and unchanged qualified symbols for the render gate."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified
from check_render_dispatch_ov import ENTRIES


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('rom', 'baseline', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.rom)
    before, after = qualified(a.baseline), qualified(a.rom)
    assert all(after.get(k) == v for k, v in before.items() if k != ('_FARCALL_COUNT',))
    delta = after[('_FARCALL_COUNT',)] - before[('_FARCALL_COUNT',)]
    assert delta == 18, delta
    dbg = a.rom.with_suffix('.dbg')
    text = dbg.read_text() if dbg.exists() else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    segments = []
    for line in text.splitlines():
        if not line.startswith('seg\t'):
            continue
        q = dict(s.split('=', 1) for s in line.split('\t', 1)[1].split(',') if '=' in s)
        if q.get('name') == '"HOT_RENDER_GATE"':
            segments.append(q)
    assert len(segments) == 1
    start, size = (int(segments[0][k], 0) for k in ('ooffs', 'size'))
    assert (start - 16) // 8192 == (start + size - 17) // 8192 == 66
    allowed = set(range(start, start + size))
    spans = {}
    for name, desc in ENTRIES.items():
        position = location(old, desc['caller']) + before[desc['local']] - address(old, desc['caller']) + desc['skip']
        allowed.update(range(position, position + 18))
        spans[name] = dict(offset=position, bank=(position - 16) // 8192, bytes=18)
    changes = {i for i, (x, y) in enumerate(zip(old['raw'], new['raw'])) if x != y}
    assert len(old['raw']) == len(new['raw']) and changes <= allowed
    assert old['raw'][:16] == new['raw'][:16] and old['raw'][16 + 1048576:] == new['raw'][16 + 1048576:]
    q = dict(passed=True, accepted=False, ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
             baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(), changed_bytes=len(changes),
             public_call_spans=spans, new_segment=dict(offset=start, bytes=size, bank=66),
             all_preexisting_qualified_symbols_exact=True, farcall_counter_delta=delta, header_and_CHR_exact=True,
             scope='Every changed ROM byte is confined to two existing18-byte calls and the appended bank66 gate. All pre-existing named qualified addresses remain exact except the compile-time farcall counter. No render body, RAM allocation, CHR, native motion, audio or other PRG byte changes.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
