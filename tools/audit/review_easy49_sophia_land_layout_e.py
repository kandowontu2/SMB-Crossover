"""Bind the append-only landing wrapper and its one changed caller."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/root49-sophia-land-fix-a'
C = R / 'build/verification/agent-lsr-sophia-feet-implementation-a/source-c'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(R / 'build/verification/agent49k-samus-water-up-direction-component-a'))
    from image import Image
    out = D / 'layout-e.json'
    assert not out.exists()
    catalog = json.loads((D / 'source-catalog-e.json').read_text())
    assert len(catalog) == 455
    for name, digest in catalog.items():
        assert sha(D / 'source-e' / name) == digest, name
    builds, maps = {}, []
    for mapper in ('mmc3', 'mmc5'):
        a = Image(C / 'build' / f'smb-crossover-{mapper}.nes')
        b = Image(D / 'source-e/build' / a.path.name)
        tick = a.hook('RemainingAudioTick')
        assert tick == b.hook('RemainingAudioTick')
        wrapper = b.hook('SophiaLandAudioTick')
        assert wrapper['physical_bank'] == 7 and b.sym('SophiaLandAudioTick')['size'] == 47
        start = wrapper['rom_offset']
        assert a.raw[start:start+47] == b'\xff'*47
        assert b.raw[start:start+3] == bytes([0x20, tick['address'] & 255, tick['address'] >> 8])
        proc = a.hook('AudioUpdate')
        size = a.sym('AudioUpdate')['size']
        call = bytes([0x20, tick['address'] & 255, tick['address'] >> 8])
        positions = [i for i in range(proc['rom_offset'], proc['rom_offset']+size-2) if a.raw[i:i+3] == call]
        assert len(positions) == 1
        offset = positions[0]
        assert b.raw[offset:offset+3] == bytes([0x20, wrapper['address'] & 255, wrapper['address'] >> 8])
        changed = [i for i, (x, y) in enumerate(zip(a.raw, b.raw)) if x != y]
        assert changed == sorted(list(range(start, start+47)) + [offset+1, offset+2]), len(changed)
        assert a.ram == b.ram
        previous_segments = {s['name']: s for s in a.segs.values()}
        current_segments = {s['name']: s for s in b.segs.values()}
        for name, segment in previous_segments.items():
            assert all(segment.get(k) == current_segments[name].get(k) for k in ('start', 'size', 'ooffs')), name
        assert set(current_segments) - set(previous_segments) == {'SOPHIA_LAND_AUDIO'}
        stream = b.hook('AvSfxSophiaLand')['address']
        assert stream >> 8 == (stream+20) >> 8
        for baseline in (False, True):
            name = f'smb-crossover-{mapper}' + ('-baseline' if baseline else '')
            builds[name] = {}
            for ext in ('nes', 'lbl', 'dbg', 'map'):
                path = D / 'source-e/build' / (name+'.'+ext)
                builds[name][ext] = dict(path=path.relative_to(R).as_posix(), sha256=sha(path), bytes=path.stat().st_size)
            if baseline:
                assert builds[name]['nes']['sha256'] == {'mmc3': '0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146', 'mmc5': '34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd'}[mapper]
        maps.append(dict(mapper=mapper, parent_ROM_sha256=sha(a.path), ROM_sha256=sha(b.path),
            wrapper=wrapper, wrapper_bytes=47, wrapper_raw=b.raw[start:start+47].hex(),
            changed_caller_ROM_offset=offset, changed_ROM_bytes=49,
            all_other_ROM_bytes_literal=True, all_previous_segment_placements_literal=True,
            all_RAM_symbols_literal=True, original_audio_code_streams_music_DPCM_literal=True,
            genuine21byte_stream_onepage=True, remaining_bank7_bytes=16+8*8192-(start+47)))
    report = dict(status='PASS_APPEND_ONLY_LANDING_WRAPPER_LAYOUT_ALL4_BUILDS', script_sha256=sha(__file__),
        source_catalog_sha256=sha(D / 'source-catalog-e.json'), source_files=455, builds=builds, maps=maps,
        qualifications=['Native landing/mixer/pause/old24 ABI+ISR and caller-cycle review is pending.',
            'Only frame-quantized images and source retrigger frames are targeted; subframe NSF write order remains distinct.',
            'No final runtime route/media claims transfer automatically from source-c.'],
        main_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], sha256=sha(out), ROMs=[m['ROM_sha256'] for m in maps])))


if __name__ == '__main__':
    main()
