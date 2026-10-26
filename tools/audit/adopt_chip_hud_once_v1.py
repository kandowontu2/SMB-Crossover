"""Adopt the exact targeted-tested movement/HUD build and retain its rollback."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PACK = D / 'root-chip-hud-composed-v1'
PARENT = '6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
FINAL = '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
SUFFIXES = ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.build.log', '.cv3-mirror.json']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def checked(path, digest=None):
    if digest:
        assert sha(path) == digest, path
    q = json.loads(Path(path).read_text())
    assert q['passed'], path
    return q


def main():
    out = PACK / 'adoption-v1'
    assert not out.exists(), 'Inspect retained adoption state before continuing.'
    default = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    dated = installed.with_name('SMB-Crossover-2026-10-26-3cee18ca-MMC5.nes')
    assert sha(default) == sha(installed) == PARENT
    assert sha(PACK / 'candidate.nes') == FINAL and not dated.exists()
    menu_path = D / 'parodius-menu3cee-native-final-v1/proof.json'
    menu = checked(menu_path, 'fb941f0e1f331b094e66366caf7cc64f9f96e68ea6f0a7c8b6c41eb3a7093017')
    assert menu['native_run'] and menu['ROM_sha256'] == FINAL
    manifest = menu_path.parent / 'manifest.json'
    assert sha(manifest) == menu['manifest_sha256']
    bound = json.loads(manifest.read_text())
    for p, h in bound.items():
        assert sha(p) == h, p
    aggregate = checked(D / 'parodius-menu3cee-preparation-v2/menu/baseline-early/lifecycle-proof.json')
    assert aggregate['ROM_sha256'] == FINAL and len(aggregate['components']) == 6
    assert all(q['passed'] for q in aggregate['components'].values())
    hard_path = D / 'root-composed3cee-hard1f-v1/native/comparison/proof.json'
    hard = checked(hard_path, '0c6802218e123c3ea1d74bc979d890202bdf898bfb68f415431906746b607542')
    assert hard['ROM_sha256'] == FINAL and not hard['cadence']['all_draw_prefix_deferrals']
    assert hard['cadence']['complete_game_totals'] == {'candidate': {'updates': 240, 'draws': 168}, 'baseline': {'updates': 240, 'draws': 167}}
    plays_path = D / 'root-chip-hud-playthroughs-v1/native/proof.json'
    plays = checked(plays_path)
    assert plays['complete'] and plays['ROM_sha256'] == FINAL
    assert {r['identity'] for r in plays['runs']} == {'chip', 'dale'}
    for r in plays['runs']:
        assert r['passed'] and r['replay']['passed'] and r['mode'] == 'easy' and r['result']['deaths'] == 0
        assert sha(Path(r['replay']['folder']) / 'proof.json') == r['replay']['proof_sha256']
    review_path = D / 'root-chip-hud-playthroughs-v1/root-review.json'
    review = checked(review_path)
    assert review['ROM_sha256'] == FINAL and review['agent_visual_review'] and review['independent_saved_PNG_RGB_checks'] == 8104
    cpu_path = D / 'chip-hot-control-composed3cee-v1/freeze-v1/receipt.json'
    cpu = checked(cpu_path, '3884f62509f34f7c3204da5d2586cec9bd55f9fd5b0483a9e95c3537509934a9')
    assert cpu['candidate_ROM_sha256'] == FINAL
    for row in cpu['bindings']:
        assert sha(row['path']) == row['sha256'], row['path']
    for row in cpu['fresh_actual_hash_CPU_checks']:
        checked(row['path'], row['sha256'])
    paths = [menu_path, hard_path, plays_path, review_path, cpu_path]
    checks = [dict(path=str(p), sha256=sha(p), passed=True) for p in paths]
    catalog = json.loads((D / 'cv3-parodius-combined-f35-v1/builds-v1/source-inventory-partitions.json').read_text())
    primary = catalog['primary_source_tool_asset_paths']
    assert len(primary) == 638
    changes = []
    expected = {}
    for row in primary:
        n = row['path']
        before = sha(D / 'world-firebar-padding-v2/source' / n)
        after = sha(PACK / 'source' / n)
        assert sha(ROOT / n) == before, n
        expected[n] = after
        if before != after:
            changes.append(dict(path=n, before_sha256=before, after_sha256=after))
    assert {r['path'] for r in changes} == set(json.loads((PACK / 'proof.json').read_text())['changed_source_files'])
    assert len(changes) == 6
    out.mkdir()
    shutil.copy2(installed, out / ('previous-' + PARENT + '.nes'))
    for suffix in SUFFIXES:
        p = default.with_suffix(suffix)
        q = out / 'previous-default' / p.name
        q.parent.mkdir(exist_ok=True)
        shutil.copy2(p, q)
    for row in changes:
        q = out / 'previous-source' / row['path']
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / row['path'], q)
    try:
        for row in changes:
            shutil.copy2(PACK / 'source' / row['path'], ROOT / row['path'])
        for mapper, digest in [(None, FINAL), ('mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                               ('mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
            target = out / ('candidate.nes' if mapper is None else 'ordinary-' + mapper + '.nes')
            command = [sys.executable, '-B', str(ROOT / 'tools/build_mmc5_expanded.py'), '--output', str(target)]
            if mapper:
                command += ['--flag-off', mapper]
            with (out / ((mapper or 'expanded') + '-ROOT-build.log')).open('w') as log:
                subprocess.run(command, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
            assert sha(target) == digest
            checks.append(dict(name='fresh ROOT ' + (mapper or 'expanded') + ' compile', passed=True, sha256=digest))
        for n, h in expected.items():
            assert sha(ROOT / n) == h, n
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
        for row in changes:
            shutil.copy2(out / 'previous-source' / row['path'], ROOT / row['path'])
        for p in (out / 'previous-default').iterdir():
            shutil.copy2(p, default.parent / p.name)
        shutil.copy2(out / ('previous-' + PARENT + '.nes'), installed)
        raise
    result = dict(passed=True, adopted=True, goal_complete=False, ROM_sha256=FINAL, parent_ROM_sha256=PARENT,
                  source_files=changes, checked_primary_source_inputs=638, final_menu_bindings_checked=len(bound),
                  current_CPU_bindings_checked=len(cpu['bindings']), checks=checks, installed=str(installed),
                  dated_build=str(dated), rollback=str(out), held_Chip_music_imported=False,
                  scope='Targeted movement overhead and HUD lettering adoption. Chip/Dale Easy1-1 plus exact replay, current menu1800/all6 guards, original Hard1F240 and actual-hash CPU/IRQ controls. Native complete draws improve1000vs997(menu) and168vs167(Hard1F).',
                  remaining='Tiny lettering/crowded body visibility/natural Buffer2 overlap, Turtle and authentic Chip music lag, missing music, all37 current1-1/every-item/Hard/shortcut/campaign matrix remain open. Earlier Mario/Luigi6c69 and other historical native results are not relabeled3cee.')
    (out / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    public = ROOT / 'docs/qa/chip-hud-adoption-2026-10-26.json'
    shutil.copy2(out / 'proof.json', public)
    print(json.dumps(dict(adopted=True, ROM_sha256=FINAL, installed=str(installed), receipt=str(public))))


if __name__ == '__main__':
    main()
