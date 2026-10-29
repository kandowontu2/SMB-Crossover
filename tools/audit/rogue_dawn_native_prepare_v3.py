"""Prepare source terrain reads using genuine DBG labels without assumed sizes."""
from pathlib import Path
import json
import sys
import current_roster_compact_11_v1 as base
import rogue_dawn_native_prepare_v1 as prior


def main():
    prior.main()
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    rom = Path(sys.argv[sys.argv.index('--rom') + 1]).resolve()
    ready = output / 'ready.json'
    record = json.loads(ready.read_text())
    raw, symbols, address, location, _ = base.linked(rom)
    # A data label has a genuine address/segment, but ca65 does not emit a
    # routine-like size field for this table. v2 was archived UNLAUNCHED;
    # its size-field assumption is superseded rather than relabelled tested.
    assert symbols['MTileAttribute']['type'] == 'lab'
    assert address('MTileAttribute') == 0xEF36
    assert address('MTILE_SOLID') == 1 and address('MTILE_CLIMB') == 2
    start = location('MTileAttribute')
    assert (start - 16) // 8192 == 127
    attributes = list(raw[start:start + 256])
    assert len(attributes) == 256
    previous = 'ROSTER_CONFIG=' + base.lua(record['config']) + '\n'
    record['config']['rogue_tile_attributes'] = attributes
    run = output / 'run.lua'
    text = run.read_text()
    assert text.startswith(previous)
    run.write_text('ROSTER_CONFIG=' + base.lua(record['config']) + '\n' + text[len(previous):])
    record['bindings'][str(run)] = base.sha(run)
    record['bindings'][str(Path(__file__).resolve())] = base.sha(__file__)
    record['source_terrain_attributes'] = dict(
        symbol='MTileAttribute', bank=127, CPU='EF36', bytes=256,
        source='Exact current ROM/DBG labelled bytes; no emulated-memory writes or inferred ground flags',
        size_note='DBG data labels have no size field; no function-like size assumption')
    ready.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(ready=str(ready), sha256=base.sha(ready))))


if __name__ == '__main__':
    main()
