"""Rehash frozen Rygar ancestry and independently review three current GQ tapes."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'specialist-gq-pit-rygar-transfer-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def rows(p):
    with Path(p).open(newline='') as f:
        return list(csv.DictReader(f))


def freeze(folder, name, expected):
    p = folder / name
    assert sha(p) == expected, p
    d = read(p)
    assert sha(R / d['index']) == d['index_sha256']
    for n, item in d['files'].items():
        f = (R / n).resolve()
        assert f.is_relative_to(R) and sha(f) == item['sha256'], n
        assert f.stat().st_size == item['bytes'], n
    return len(d['files'])


def native_binding(d, rom):
    """Verify every recorded hook/table's physical bank and literal ROM bytes."""
    if isinstance(d, dict):
        if {'rom_offset', 'physical_bank', 'bytes', 'address'} <= d.keys():
            offset = d['rom_offset']
            assert offset == 16 + d['physical_bank'] * 8192 + (d['address'] & 8191)
            assert rom[offset:offset + len(d['bytes'])] == bytes(d['bytes'])
            assert len(d['bytes']) == 8
        for v in d.values():
            native_binding(v, rom)
    elif isinstance(d, list):
        for v in d:
            native_binding(v, rom)


def main():
    out = V / 'root49-gq-routes-gu.json'
    assert not out.exists()
    counts = {
        'Rygar_EL': freeze(V / 'specialist-rygar-el-a', 'phase-index-ab-freeze.json',
            '8dffac7c57cfec9bca7f4c761c3e97332636cd983ce3c50fa855ff0e70ef0084'),
        'GQ_three_routes': freeze(H, 'phase-index-b-freeze.json',
            '1b9766ad7315bfe291d57aa44d17285d5251b89b86139a8aad7e88b715d5dc98'),
    }
    assert counts == {'Rygar_EL': 798, 'GQ_three_routes': 127}
    el_inventory = read(V / 'specialist-rygar-el-a/inventory.json')
    el_root = V / 'root49-link-watch-ej/source'
    assert len(el_inventory['source_hashes']) == 441
    for n, h in el_inventory['source_hashes'].items():
        assert sha(el_root / n) == h, n
    for artifacts in el_inventory['images'].values():
        for n, h in artifacts.items():
            assert sha(R / n) == h, n
    manifest = R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json'
    assert sha(manifest) == 'b8d20e8cab676894da899801146554f310dc4c339453c7b0897cfe92833c623f'
    installed = read(manifest)
    assert len(installed['source_hashes']) == 442
    assert all(sha(R / n) == h for n, h in installed['source_hashes'].items())
    for b in installed['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    assert not (R / 'src/bill_source_body.s').exists()
    rom = (R / 'build/smb-crossover-mmc3.nes').read_bytes()
    el = read(V / 'specialist-rygar-el-a/handoff-aa.json')
    et, ez = rows(R / el['proof'] / 'trace.csv'), rows(R / el['candidate'] / 'trace.csv')
    assert len(et) == len(ez) == 20988
    fields = el['comparison']['fields']
    assert len(fields) == 19
    assert all(all(a[k] == b[k] for k in fields) for a, b in zip(et, ez))
    assert (R / el['proof'] / 'inputs.csv').read_bytes() == (R / el['candidate'] / 'inputs.csv').read_bytes()
    for branch in el['opaque_branches']:
        p = R / branch['path']
        assert sha(p / 'manifest.json') == branch['manifest_sha256']
        root = read(p / 'manifest.json')['winning_reusable_root']
        assert root == branch['cold_verification'] and root['verified_coldboot']
        assert root['ram_bytes_identical'] == 10240
        assert not root['savestate_loads'] and not root['emulated_writes']
        assert sha(p / 'winning-inputs.csv') == root['inputs_sha256']
        assert sha(p / 'winning-ram.bin') == root['ram_sha256']
    result = {}
    expected = {'rygar': (7, 20988, 20964, 76), 'pit': (6, 24726, 24702, 76),
        'bass': (9, 26689, 26665, 66)}
    for name, (identity, length, entry, finish_x) in expected.items():
        h = read(H / f'handoff-{name}-a.json')
        proof, ancestor = R / h['proof'], R / 'build/roster-through-2-2' / h['ancestry']['proof']
        for n, value in h['files'].items():
            assert sha(proof / n) == value, (name, n)
        assert sha(proof / 'manifest.json') == h['manifest_sha256']
        assert sha(proof / 'smb-crossover-mmc3.nes') == h['ROM_sha256'] == installed['builds'][0]['artifacts']['nes']['sha256']
        m = read(proof / 'manifest.json')
        assert m['verified_through_2_2'] and m['full_frame_audit'] and m['controller_only']
        assert not m['memory_or_register_writes']
        assert not h['savestate_loads'] and not h['emulated_memory_register_PC_or_coordinate_grants']
        assert not h['recorded'] and h['native_exit'] == 0
        assert h['actual_identity'] == dict(observed=True, frame=541, mode=0,
            selected=identity, variant=0, outlinesOff=1)
        assert m['result'] == h['result'] and h['result']['cleared'] and h['result']['all_six_stages']
        assert h['result']['frames'] == length and h['result']['polls'] == length - 1
        assert h['result']['deaths'] == 0 and h['result']['failure'] is None
        assert h['result']['stage_entries']['1-2'] == entry
        assert sha(proof / 'inputs.csv') == h['input_sha256']
        assert (proof / 'inputs.csv').read_bytes() == (ancestor / 'inputs.csv').read_bytes()
        a, b = rows(ancestor / 'trace.csv'), rows(proof / 'trace.csv')
        assert len(a) == len(b) == length and h['comparison']['fields'] == fields
        assert all(all(x[k] == y[k] for k in fields) for x, y in zip(a, b))
        tail = [x for x in b if int(x['frame']) >= entry]
        assert len(tail) == 25 and int(tail[0]['x']) == 40 and int(tail[-1]['x']) == finish_x
        assert all(x['world'] == '1' and x['level'] == '2' for x in tail)
        render = rows(proof / 'render.csv')
        assert [int(x['frame']) for x in render] == list(range(500, length + 1))
        assert all(x['behaviorVersion'] == '0' for x in render)
        assert h['stomp']['illegal_guest_events'] == h['stomp']['resident_opcode_mismatches'] == 0
        binding = read(R / h['support']['binding'])
        assert sha(R / h['support']['binding']) == h['support']['binding_sha256']
        native_binding(binding, rom)
        assert not h['support']['unclassified']
        assert Counter(x['kind'] for x in h['support']['details']) == h['support']['kinds']
        result[name] = dict(result=h['result'], all19_actual_fields_exact_EL=True,
            real_next_stage_controls=h['next_stage_controls'], actual_identity=h['actual_identity'],
            supports=h['support']['kinds'], hardware_audit_frames=len(render),
            handoff_sha256=sha(H / f'handoff-{name}-a.json'))
        if name == 'bass':
            offset = binding['metatile_attributes_rom_offset']
            attrs = rom[offset:offset + 256]
            assert list(attrs) == binding['metatile_attributes']
            launches = [x for x in map(json.loads, (proof / 'support-events.jsonl').read_text().splitlines()) if x['event'] == 'Launch']
            classified = []
            for z in launches:
                assert z['fresh'] & 128
                if z['state']:
                    assert z['state'] in (1, 2) and z['jumpUsed'] == 1 and z['yHigh'] in (0, 1)
                    kind = 'accepted_air_secondary_jump'
                elif z['springAnimation']:
                    assert z['yHigh'] == 1 and z['springAnimation'] == 2
                    assert z['tile2'] == z['tile13'] == 0x67
                    assert len([a for a in z['actors'] if a[1] == 1 and a[2] == 50 and abs(a[4]-z['x']) <= 16 and a[5] == z['feetY']]) == 1
                    kind = 'actual_compressed_spring'
                elif attrs[z['tile2']] & 1 or attrs[z['tile13']] & 1:
                    assert z['yHigh'] == 1 and z['feetY'] % 16 == 0
                    kind = 'actual_terrain_at_native_feet'
                else:
                    assert z['yHigh'] == 1
                    assert len([a for a in z['actors'] if a[1] == 1 and a[2] in (37, 38, 39, 40) and a[5] == z['feetY'] and a[6] == a[0]]) == 1
                    kind = 'actual_platform_with_own_collision_token'
                classified.append(kind)
            assert Counter(classified) == h['support']['kinds'] and len(launches) == 238
            assert [x['frame'] for x in launches if x['yHigh'] == 0] == [14037]
    report = dict(status='PASS_REHASHED_GQ_RYGAR_PIT_BASS_MMC3_EASY_ROUTES',
        script_sha256=sha(__file__), frozen_files_rehashed=counts,
        old_EL_immutable_sources441_and_artifacts8_exact=True,
        current_GQ_sources442_and_artifacts8_exact=True, routes=result,
        limitations=['Pit includes one explicitly classified native landing/side-push corner catch; no glitchless claim.',
            'Rygar and Pit support logs inspect pre-input fresh A attempts; Bass logs actual accepted Launch calls.',
            'Hardware render/CHR/OAM/scroll/APU audit is not decoded movie review or audible waveform equivalence.',
            'No complete arsenal, MMC5, Hard, final successor or final recording claim.'],
        runtime_changes=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out), counts)


if __name__ == '__main__':
    main()
