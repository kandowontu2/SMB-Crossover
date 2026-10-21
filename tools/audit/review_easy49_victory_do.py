"""Independent frozen-C review; preserve its source-WATCH and budget limits."""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
C = V / 'agent-lsr-victory-repair-c'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root49-victory-review-do.json'
    assert not output.exists()
    fp = C / 'implementation-freeze.json'
    assert sha(fp) == '3a1d954e4f279fe850c3f5686d9ae03a90cc1d585438164070d2ca4cb68a4462'
    f = json.loads(fp.read_text())
    pp = C / 'persistent-controls/freeze.json'
    assert sha(pp) == '472157f88175f7af6459a174a96a3dcaec9725ff38ed5e15f865c7ef9f006bf1'
    p = json.loads(pp.read_text())
    checked = []
    for base, doc in [(C, f), (pp.parent, p)]:
        for name, digest in doc['files'].items():
            path = base / name
            assert sha(path) == digest, path
            checked.append(dict(path=path.relative_to(R).as_posix(), sha256=digest))
    parent_path = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
    assert sha(parent_path) == f['parent_manifest_sha256']
    parent = json.loads(parent_path.read_text())
    assert len(parent['source_hashes']) == 440
    assert all(sha(R / n) == h for n, h in parent['source_hashes'].items())
    source = C / 'source'
    assert len(f['source_catalog']) == 441
    assert all(sha(source / n) == h for n, h in f['source_catalog'].items())
    changes = {n for n, h in f['source_catalog'].items() if parent['source_hashes'].get(n) != h}
    assert changes == set(f['after_files'])
    for n, h in f['after_files'].items():
        assert sha(C / 'after' / n) == h
    for n, h in f['parent_source_files'].items():
        assert parent['source_hashes'][n] == h
    for artifacts in f['compiled_artifacts']:
        for row in artifacts.values():
            path = Path(row['path'])
            assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    proposal = json.loads((C / 'proposal.json').read_text())
    for n, row in proposal['source_anchors'].items():
        assert sha(R / n) == row['sha256'], n
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('victory_do_image', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    builds = json.loads((C / 'build-report.json').read_text())['builds']
    maps = []
    for mapper in ('mmc3', 'mmc5'):
        old = module.Image(V / 'root49-easy-combined-cg/source/build' / f'smb-crossover-{mapper}.nes')
        new = module.Image(source / 'build' / f'smb-crossover-{mapper}.nes')
        assert old.ram == new.ram
        seg = lambda im, name: next(x for x in im.segs.values() if x['name'] == name)
        os, ns = seg(old, 'PLAYER'), seg(new, 'PLAYER')
        oc, nc = seg(old, 'RYU_COLD'), seg(new, 'RYU_COLD')
        assert ns['size'] - os['size'] == 30
        assert nc['size'] - oc['size'] == 184
        assert ns['start'] == os['start'] and nc['start'] == oc['start']
        row = next(b for b in builds if b['mapper'] == mapper and not b['baseline'])
        allowed = set(row['rare_call_operand_offsets'])
        for a, b in [(os, ns), (oc, nc)]:
            start = a['ooffs'] + a['size']
            allowed.update(range(start, b['ooffs'] + b['size']))
        changed = {i for i, (a, b) in enumerate(zip(old.raw, new.raw)) if a != b}
        assert len(changed) == 216 and changed <= allowed
        assert new.raw[:16] == old.raw[:16] and new.raw[524304:] == old.raw[524304:]
        for folder, cases in [('component-v3', 30), ('release-controls-v2', 6), ('persistent-controls', 30)]:
            result = json.loads((C / folder / f'component-{mapper}/native-output/result.json').read_text())
            assert result['cases'] == cases and result['failure_count'] == 0
        maps.append(dict(mapper=mapper, ROM_sha256=sha(new.path), old_RAM_exact=len(old.ram),
                         changed_bytes=len(changed), only_rare_operands_and_appended_tails=True,
                         PLAYER_append_actual=30, RYU_COLD_append_actual=184,
                         original_PLAYER_budget_report=28, compiled_budget_correction=2))
    # Recompute the actual controller-route prefix claims instead of trusting the review label.
    before = R / 'build/roster-through-2-2/agent-lsr-by-simon-live-i-5-v0-mmc3'
    after = R / 'build/roster-through-2-2/agent-lsr-victory-repair-c-prefix-i-a-5-v0-mmc3'
    counts = {}
    for name in ('audio-events.csv', 'chr.csv', 'events.csv', 'inputs.csv', 'oam.csv',
                 'render.csv', 'scroll-writes.csv', 'stomp-events.csv', 'trace.csv'):
        def rows(folder):
            with (folder / name).open(newline='') as stream:
                return [r for r in csv.DictReader(stream) if int(r['frame']) < 14047]
        a, b = rows(before), rows(after)
        assert a == b, name
        counts[name] = len(a)
    actual = json.loads((after / 'result.json').read_text())
    assert actual['stage_entries']['1-0'] == 14784 and actual['frames'] == 15829
    cpu = json.loads((C / 'cpu-report-v2.json').read_text())
    assert sum(x['cases'] for x in cpu['native_C']) == 120
    assert all(x['ordinary_added_cycles'] == 0 and x['rare_cycle_delta_histogram'] == {'10': 30, '14': 30}
               for x in cpu['native_C'])
    report = dict(status='PASS_INDEPENDENT_FROZEN_RARE_VICTORY_C_WITH_COMPILED_SIZE_CORRECTION',
        script_sha256=sha(__file__), freeze_sha256=sha(fp), persistent_supplement_sha256=sha(pp),
        checked_receipt_files=checked, source_files=441, changed_source_paths=sorted(changes),
        source_anchors_verified=len(proposal['source_anchors']), mappers=maps,
        native_cases=72, additive_full_inventory_cases=60, persistent_span_bytes=300,
        nonzero_ammo_counters=192, native_Mario_Luigi_fallback_cases=120,
        prefix_literal_before_first_rare_call=counts, castle_clear_2_1_entry=14784,
        actual_later_route_failure=actual['failure'],
        budget_correction='Actual compiled PLAYER append is30B, not28B in freeze budget. With Bill F/N PLAYER8110 and MMC3 SMC49 the combined free space is3B; MMC5 has19B. Original immutable freeze retained.',
        qualifications=f['qualifications'] + [
            'EasyLink uses a separate RgBillBurst source framegraph; common timer advancement alone does not establish its victory animation parity.',
            'Original C component used a one-byte inventory witness; the separately frozen supplement checks all300 persistent bytes and192 nonzero ammo counters.',
            'B ordinary +20cycle experiment is retained negative ancestry, not the final C implementation.'],
        main_changed=False, accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(output))


if __name__ == '__main__':
    main()
