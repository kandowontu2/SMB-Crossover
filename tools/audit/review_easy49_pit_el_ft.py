"""Independently rehash Pit's EL clear, its explicit corner witness and the separate MMC5 negative."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'specialist-pit-el-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    out = V / 'root49-pit-el-full-ft.json'
    assert not out.exists()
    pins = {
        'phase-index-ab.json': 'd88500b56500f572bf05361332f0094fae9fa45e481517e16c28bab338590fa0',
        'phase-index-ab-freeze.json': 'c40b4fd1b9b09877287519543c02fb7c095f35b1e2732169208e10ef016b434c',
        'handoff-mmc3-x2.json': '8df2ad654dc98b7fc84de1c580baeb2c728ecd11ecc2b74ba4ecdfd224717ece',
        'handoff-mmc5-aa-negative.json': '8406669b1a5ceb02b0303c88a4ed10e30ae8784ab82a8629575136f03b01b6c3',
    }
    for n, h in pins.items():
        assert sha(H / n) == h, n
    frozen = json.loads((H / 'phase-index-ab-freeze.json').read_text())
    for n, row in frozen['files'].items():
        p = R / n
        assert p.is_relative_to(R) and sha(p) == row['sha256'] and p.stat().st_size == row['bytes'], n
    h = json.loads((H / 'handoff-mmc3-x2.json').read_text())
    negative = json.loads((H / 'handoff-mmc5-aa-negative.json').read_text())
    installed = json.loads((R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json').read_text())
    binding = json.loads((H / 'el-binding-a.json').read_text())
    assert binding['source_hashes'] == installed['source_hashes'] and len(binding['source_hashes']) == 441
    assert all(sha(R / n) == value for n, value in installed['source_hashes'].items())
    for build in installed['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in build['artifacts'].values())
    candidate, proof = R / h['candidate'], R / h['proof']
    m = json.loads((proof / 'manifest.json').read_text())
    assert m['verified_through_2_2'] and m['full_frame_audit'] and not m['memory_or_register_writes']
    assert m['result'] == h['result'] and h['result']['frames'] == 24726 and h['result']['polls'] == 24725
    assert h['result']['cleared'] and h['result']['deaths'] == 0 and h['result']['stage_entries']['1-2'] == 24702
    assert sha(proof / 'smb-crossover-mmc3.nes') == h['ROM_sha256'] == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    assert sha(proof / 'inputs.csv') == h['input_sha256'] == '7ee0fabea8d40a0e59881d257b76d7543cf437a58ea981cbfa970a869c45653f'
    assert (candidate / 'inputs.csv').read_bytes() == (proof / 'inputs.csv').read_bytes()
    a, b = rows(candidate / 'trace.csv'), rows(proof / 'trace.csv')
    assert len(a) == len(b) == 24726
    fields = h['comparison']['fields']
    assert len(fields) == 19 and all(all(x[k] == y[k] for k in fields) for x, y in zip(a, b))
    tail = [r for r in b if int(r['frame']) >= 24702]
    assert len(tail) == 25 and int(tail[0]['x']) == 40 and int(tail[-1]['x']) == 76
    render = rows(proof / 'render.csv')
    assert len(render) == 24726 - 499 and all(int(r['behaviorVersion']) == 0 for r in render)
    assert h['support']['receipts'] == 159 and h['support']['unclassified'] == []
    assert h['support']['kinds']['native_landing_then_side_push_corner_takeoff'] == 1
    corner = h['support_review']
    assert int(corner['actual_endframe']['x']) == 721 and int(corner['next_input_result']['y']) == 91
    assert 'not continuous floor support' in corner['qualification']
    nproof = R / negative['proof']
    nm = json.loads((nproof / 'manifest.json').read_text())
    assert not nm['verified_through_2_2'] and nm['full_frame_audit']
    assert negative['result']['failure'] == 'death' and negative['result']['frames'] == 3442
    assert sha(nproof / 'smb-crossover-mmc5.nes') == '3161fa3d8eb002f9a98a7c29cac6347770d955252c49bd0337e5a13b93579d10'
    nt = rows(nproof / 'trace.csv')
    differences = [dict(frame=int(y['frame']), fields={k: [x[k], y[k]] for k in fields if x[k] != y[k]})
        for x, y in zip(b, nt) if any(x[k] != y[k] for k in fields)]
    assert differences[0] == negative['comparison']['first_difference'] and differences[0]['frame'] == 2435
    report = dict(status='PASS_REHASHED_EL_PIT_MMC3_FULL_CLEAR_WITH_EXPLICIT_CORNER_MMC5_NEGATIVE',
        script_sha256=sha(__file__), rehashed_files=len(frozen['files']), pins=pins,
        actual_EL_ROM_sha256=h['ROM_sha256'], result=h['result'], exact19_fields=True,
        real_next_stage_controls=dict(frames=25, x_from=40, x_to=76), support_kinds=h['support']['kinds'],
        corner_qualification=corner['qualification'], MMC5_first_difference=differences[0],
        MMC5_result=negative['result'], source441_and8_main_artifacts_exact=True,
        full_hardware_audit_is_not_video_or_waveform_identity=True, all_arsenal_claim=False,
        source_perfect_or_glitchless_claim=False, final_integrated_recording=False,
        main_changed=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out), report['rehashed_files'])


if __name__ == '__main__':
    main()
