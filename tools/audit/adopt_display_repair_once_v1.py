"""Adopt the exact qualified HUD/timing repair, preserving the preceding CV3 build."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PACK = D / 'world-firebar-padding-v2'
PARENT = '2cb5fca0757c3e347c264eab0bf3f22bd02d851787f38802a4af3cb0c3aa1fa5'
FINAL = '6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
SUFFIXES = ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.build.log', '.cv3-mirror.json']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--menu-final', type=Path, required=True)
    parser.add_argument('--expected-menu-sha256', required=True)
    a = parser.parse_args()
    out = PACK / 'adoption-v1'
    assert not out.exists(), 'Inspect retained adoption state before any continuation.'
    default = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    dated = installed.with_name('SMB-Crossover-2026-10-26-6c69e506-MMC5.nes')
    assert sha(default) == sha(installed) == PARENT
    assert sha(PACK / 'candidate.nes') == FINAL and not dated.exists()
    assert sha(a.menu_final) == a.expected_menu_sha256
    menu = json.loads(a.menu_final.read_text())
    assert menu['passed'] and menu['native_run'] and menu['ROM_sha256'] == FINAL
    manifest = a.menu_final.parent / 'manifest.json'
    assert sha(manifest) == menu['manifest_sha256']
    bound = json.loads(manifest.read_text())
    for p, h in bound.items():
        assert sha(p) == h, p
    aggregate_path = D / 'parodius-menu6c69-preparation-v1/menu/baseline-early/lifecycle-proof.json'
    aggregate = json.loads(aggregate_path.read_text())
    assert aggregate['passed'] and aggregate['runner_exit'] == 0 and aggregate['ROM_sha256'] == FINAL
    assert len(aggregate['components']) == 6 and all(q['passed'] for q in aggregate['components'].values())
    hard_path = D / 'root-padding6c69-hard1f-v1/native/comparison/proof.json'
    hard = json.loads(hard_path.read_text())
    assert hard['passed'] and hard['ROM_sha256'] == FINAL
    assert hard['cadence']['complete_game_totals'] == {'candidate': {'updates': 240, 'draws': 167}, 'baseline': {'updates': 240, 'draws': 167}}
    checks = [dict(name='current all-six menu1800 native guards', passed=True, receipt=str(a.menu_final), sha256=sha(a.menu_final)),
              dict(name='current strict Hard1F240 source/hardware/cumulative cadence', passed=True, receipt=str(hard_path), sha256=sha(hard_path))]
    for name in ['root-hud-cpu-v1', 'root-gateway-cpu-v1', 'root-hud-interrupt-v1', 'cpu-v1']:
        p = PACK / name / 'proof.json'
        q = json.loads(p.read_text())
        assert q['passed']
        assert FINAL in [q.get('ROM_sha256'), q.get('candidate_ROM_sha256')]
        checks.append(dict(name=name, passed=True, receipt=str(p), sha256=sha(p)))
    baseline = json.loads((D / 'cv3-remaining-legacy-wrapper-v2/freeze-v2/readiness-source-only.json').read_text())
    previous = {q['path']: q['sha256'] for q in baseline['source_files']}
    catalog = json.loads((D / 'cv3-parodius-combined-f35-v1/builds-v1/source-inventory-partitions.json').read_text())
    primary = catalog['primary_source_tool_asset_paths']
    assert len(primary) == 638
    changed = []
    expected = {}
    for row in primary:
        n = row['path']
        p = ROOT / n
        old = previous.get(n)
        assert (sha(p) if p.exists() else None) == old, n
        new = sha(PACK / 'source' / n)
        assert n == 'src/metasprite_engine.s' or new == row['sha256'], n
        expected[n] = new
        if old != new:
            changed.append(dict(path=n, before_sha256=old, after_sha256=new))
    assert len(changed) == 12
    out.mkdir()
    shutil.copy2(installed, out / ('previous-' + PARENT + '.nes'))
    for suffix in SUFFIXES:
        p = default.with_suffix(suffix)
        if p.exists():
            q = out / 'previous-default' / p.name
            q.parent.mkdir(exist_ok=True)
            shutil.copy2(p, q)
    for row in changed:
        p = ROOT / row['path']
        if p.exists():
            q = out / 'previous-source' / row['path']
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, q)
    try:
        for row in changed:
            shutil.copy2(PACK / 'source' / row['path'], ROOT / row['path'])
        for mapper, digest in [(None, FINAL), ('mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                               ('mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
            output = out / ('candidate.nes' if mapper is None else 'ordinary-' + mapper + '.nes')
            cmd = [sys.executable, '-B', str(ROOT / 'tools/build_mmc5_expanded.py'), '--output', str(output)]
            if mapper:
                cmd += ['--flag-off', mapper]
            with (out / (('expanded' if mapper is None else mapper) + '-ROOT-build.log')).open('w') as log:
                subprocess.run(cmd, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
            assert sha(output) == digest, output
            checks.append(dict(name='fresh ROOT ' + (mapper or 'expanded') + ' compile', passed=True, sha256=digest))
        for n, h in expected.items():
            assert sha(ROOT / n) == h, n
        for suffix in SUFFIXES:
            assert (out / 'candidate.nes').with_suffix(suffix).is_file()
        for target in [dated, installed]:
            stage = target.with_name(target.name + '.staging-' + FINAL[:8])
            assert not stage.exists()
            shutil.copy2(out / 'candidate.nes', stage)
            assert sha(stage) == FINAL
            stage.replace(target)
        for suffix in SUFFIXES:
            shutil.copy2((out / 'candidate.nes').with_suffix(suffix), default.with_suffix(suffix))
        assert sha(default) == sha(installed) == sha(dated) == FINAL
    except BaseException:
        for row in changed:
            p = ROOT / row['path']
            if row['before_sha256'] is None:
                p.unlink(missing_ok=True)
            else:
                shutil.copy2(out / 'previous-source' / row['path'], p)
        for p in (out / 'previous-default').iterdir():
            shutil.copy2(p, default.parent / p.name)
        shutil.copy2(out / ('previous-' + PARENT + '.nes'), installed)
        raise
    checks.append(dict(name='all638 source inputs and installed/default/dated hash', passed=True))
    result = dict(passed=True, adopted=True, goal_complete=False, rom_sha256=FINAL, parent_rom_sha256=PARENT,
                  source_files=changed, checked_primary_source_inputs=638, checks=checks,
                  menu_manifest_bindings_verified=len(bound), installed=str(installed), dated_build=str(dated),
                  rollback=str(out), original4285_deadline_negative_preserved=True,
                  natural_full_HUD_Buffer2_overlap_native_qualified=False,
                  historical_death_area_and_other_CV3_native_results_not_relabelled=True,
                  remaining='Current native menu and strict Hard1F controls plus fresh CPU/IRQ/caller checks only. '
                            'Natural pending-full-HUD/Buffer2 overlap, cramped bar labels, crowded sprite visibility, '
                            'Turtle/Chip lag, missing music, all37 current1-1/item/campaign verification remain open.')
    (out / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    public = ROOT / 'docs/qa/display-repair-adoption-2026-10-26.json'
    shutil.copy2(out / 'proof.json', public)
    print(json.dumps(dict(adopted=True, ROM_sha256=FINAL, installed=str(installed), proof=str(public))))


if __name__ == '__main__':
    main()
