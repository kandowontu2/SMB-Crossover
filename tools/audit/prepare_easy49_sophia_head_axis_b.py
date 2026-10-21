"""Prepare an isolated full normal-flat source head/corner selector over C."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
D = V / 'root49-sophia-head-axis-b'
P = V / 'root49-combined-working-c'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    catalog = json.loads((P / 'source-catalog.json').read_text())
    for n, h in catalog.items():
        assert sha(P / 'source' / n) == h, n
        p = D / 'source' / n
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(P / 'source' / n, p)
    shutil.copytree(P / 'source/build/generated', D / 'source/build/generated')
    shutil.copyfile(P / 'build.py', D / 'build.py')
    template = R / 'tools/audit/templates/sophia_head_axis_b.s'
    path = D / 'source/src/sophia_source_terrain.s'
    text = path.read_text()
    assert text.count('  jsr SophiaPriorXOverlapsCell') == 1
    text = text.replace('  jsr SophiaPriorXOverlapsCell', '  jsr SophiaHeadSourceAxis')
    path.write_text(text + '\n' + template.read_text())
    native = R / 'build/roster-through-2-2/root49-sophia-head-corner-a-11-v0-mmc3/head-corner-a.csv'
    rows = list(csv.DictReader(native.open()))
    first = next(z for z in rows if z['event'] == 'Separate' and int(z['frame']) == 939)
    q = {k: int(v) if v.lstrip('-').isdigit() else v for k, v in first.items()}
    x = q['Player_PageLoc'] * 256 + q['Player_X_Position'] + (q['MmXFraction'] + 256 * q['MmXFraction+1']) / 65536
    y = q['Player_Y_Position'] + (q['MmYFraction'] + 256 * q['MmYFraction+1']) / 65536
    oldx = q['RyWallOldPage'] * 256 + q['RyWallOldX'] + (q['RyWallOldXFine'] + 256 * q['RyWallOldXFrac']) / 65536
    left = q['RgTempPage'] * 256 + (q['RgTempX'] & 240)
    bottom = q['R2'] + 48
    vpen, hpen = bottom - (y + 16.5), x + 17.5 - left
    assert oldx + 17.5 == left and vpen > hpen > 0
    result = dict(status='PREPARED_PRIVATE_NORMAL_FLAT_HEAD_AXIS_REPAIR_NOT_VALIDATED', script_sha256=sha(__file__),
                  parent_catalog_sha256=sha(P / 'source-catalog.json'), template_sha256=sha(template),
                  native_receipt=dict(path=native.relative_to(R).as_posix(), sha256=sha(native), actual_row=q,
                                      prior_right=oldx+17.5, cell_left=left, vertical_penetration=vpen, horizontal_penetration=hpen,
                                      source_final_axis='side', old_native_axis='head'),
                  source_sha256={n: sha(D / 'source' / n) for n in catalog},
                  source_reference=dict(path='reference/crossover2/extracted/scripts/com/smbc/data/HitTester.as',
                                        sha256=sha(R / 'reference/crossover2/extracted/scripts/com/smbc/data/HitTester.as')),
                  phase_cap_bytes=500000000, final_reserve_bytes=50000000, global_cap_bytes=70000000000,
                  qualifications=['Final source calcAxis arithmetic is implemented, not the Flash Ground-list deferred scheduling.',
                                  'Existing normal-flat eligibility and direct-below vertical test remain. Rotated/attached forms stay separate.'],
                  main_changed=False, goal_complete=False)
    (D / 'preparation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], actual_Vpen=vpen, actual_Hpen=hpen)))


if __name__ == '__main__':
    main()
