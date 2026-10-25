"""Merge original state goldens and verify every call against the earlier probe."""
from pathlib import Path
import argparse, gzip, hashlib, itertools, json, shutil

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs', type=Path, nargs='+', required=True)
    p.add_argument('--legacy', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    sets = ['seen_instructions', 'ROM_data_reads', 'pointer_components', 'unknown_pointer_origins', 'pointer_accesses']
    result = {n: set() for n in sets}
    maps = ['source_instructions', 'accesses', 'stores', 'profile', 'tracks']
    result.update({n: {} for n in maps})
    legacy = json.loads((a.legacy / 'footprint.json').read_text())
    calls = writes = 0
    dmc, original_loops = set(), {}
    for folder in a.inputs:
        q = json.loads((folder / 'coverage.json').read_text())
        assert q['passed'] and q['provenance_version'] == 2 and q['calls_per_song'] == 18000
        assert q['source_sha256'] == legacy['source_sha256']
        for n in sets:
            result[n].update(tuple(v) if isinstance(v, list) else v for v in q[n])
        for n in ['source_instructions', 'tracks']:
            for k, v in q[n].items():
                assert k not in result[n] or result[n][k] == v
                result[n][k] = v
        for n in ['accesses', 'stores']:
            for k, values in q[n].items():
                result[n].setdefault(k, set()).update(values)
        for k, row in q['profile'].items():
            old = result['profile'].setdefault(k, dict(count=0, cycles=0))
            for n, v in row.items(): old[n] += v
        for song, summary in q['tracks'].items():
            s = int(song)
            fresh = folder / f'song-{s:02x}.jsonl.gz'
            old = a.legacy / f'parodius-{s:02x}.jsonl.gz'
            assert sha(fresh) == summary['capture_sha256']
            assert sha(old) == legacy['tracks'][song]['capture_sha256']
            apu = [0] * 24
            count = 0
            with gzip.open(fresh, 'rt') as f, gzip.open(old, 'rt') as g:
                for n, (line, prev) in enumerate(itertools.zip_longest(f, g)):
                    assert line is not None and prev is not None
                    x, y = json.loads(line), json.loads(prev)
                    assert x['step'] == y['step'] == n and x['cycles'] == y['cycles']
                    assert x['writes'] == y['APU'] and x['full_source_RAM_sha256'] == y['ram_sha256']
                    for at, value in x['writes']:
                        apu[at - 0x4000] = value
                        if at == 0x4015 and value & 16:
                            dmc.add(tuple(apu[16:20]))
                    calls += 1
                    writes += len(x['writes'])
                    count += 1
            assert count == 18002
            for name in [fresh.name, f'song-{s:02x}-peak.json']:
                shutil.copyfile(folder / name, a.output / name)
            original_loops[song] = summary['exact_state_repeats']
    assert sorted(int(s) for s in result['tracks']) == list(range(0x46, 0x9b, 4))
    assert not result['unknown_pointer_origins']
    for n in sets:
        result[n] = sorted(result[n])
    for n in ['accesses', 'stores']:
        result[n] = {k: sorted(v) for k, v in result[n].items()}
    result.update(passed=True, source_only=True, source_sha256=legacy['source_sha256'],
                  calls_per_song=18000, source_reset=0xc542, source_request=0xc58d,
                  source_play=0x80a2, source_mapped_banks=[12, 13, 14, 15],
                  ZP=q['ZP'], RAM=q['RAM'], provenance_version=2,
                  every_call_legacy_ordered_APU_cycles_and_entire_source_RAM_hash_exact=True,
                  original_calls=calls, original_ordered_APU_stores=writes,
                  DMC_register_configs=sorted(dmc), original_exact_state_repeats=original_loops,
                  inputs={str(f / 'coverage.json'): sha(f / 'coverage.json') for f in a.inputs},
                  legacy_footprint_sha256=sha(a.legacy / 'footprint.json'),
                  native_emulator_launched=False, tool_sha256=sha(Path(__file__)),
                  limits='All22 original groups retain source stores/cycles/full RAM. Affine pointer provenance is not by itself a linked relocation proof. No guessed tune names, source-scene map or native timing claim.')
    (a.output / 'coverage.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'original_calls', 'original_ordered_APU_stores', 'DMC_register_configs']}))


if __name__ == '__main__':
    main()
