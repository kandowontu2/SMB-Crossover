"""Adopt clean731 only after its exact native menu and timing receipts qualify."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PACK = D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
PARENT = '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
FINAL = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
SUFFIXES = ['.nes','.dbg','.lbl','.map','.build.json','.build.log','.cv3-mirror.json']
CHANGES = ['smb1base-mmc5-expanded.cfg','src/character_select.s','src/menu_vram_budget.s','src/reset.s']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def checked(p, digest=None):
    if digest:
        assert sha(p) == digest, p
    value = json.loads(Path(p).read_text(encoding='utf-8'))
    assert value['passed'], p
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--menu-proof', type=Path, required=True)
    parser.add_argument('--menu-proof-sha256', required=True)
    parser.add_argument('--menu-visual-proof', type=Path, required=True)
    parser.add_argument('--menu-visual-proof-sha256', required=True)
    args = parser.parse_args()
    out = D/'clean731-adoption-v1'
    assert not out.exists(), 'Inspect retained adoption state; no automatic retry.'
    default = ROOT/'build/smb-crossover-mmc5-expanded.nes'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    dated = installed.with_name('SMB-Crossover-2026-10-26-731c918b-MMC5.nes')
    assert sha(default) == sha(installed) == PARENT
    assert sha(PACK/'candidate.nes') == FINAL and not dated.exists()
    menu = checked(args.menu_proof, args.menu_proof_sha256)
    visual = checked(args.menu_visual_proof, args.menu_visual_proof_sha256)
    assert menu['ROM_sha256'] == visual['ROM_sha256'] == FINAL
    assert menu['native_run'] is True and menu['all_original6_and_additive_timing_passed'] is True
    assert visual.get('agent_visual_review') is True, 'Explicit actual wholeframe review required.'
    assert visual['actual_owned_selection_frame_count'] == 164
    assert len(visual['actual_owned_selection_frames_reviewed']) == 164
    assert menu['visual_proof_sha256'] == sha(args.menu_visual_proof)
    root_pixels = checked(D/'ROOT-clean731-menu-static-v1/proof.json')
    root_visual = checked(D/'ROOT-clean731-menu-static-v1/ROOT-eight-wholeframe-review.json')
    assert root_pixels['ROM_sha256'] == root_visual['ROM_sha256'] == FINAL
    assert root_pixels['owned_actual_frames'] == 164 and root_pixels['total_static_pixels'] == 8480768
    for key in ['manifest_sha256']:
        manifest = args.menu_proof.parent/'manifest.json'
        assert sha(manifest) == menu[key]
        for path, h in json.loads(manifest.read_text(encoding='utf-8')).items():
            assert sha(path) == (h['sha256'] if isinstance(h,dict) else h), path
    timing = checked(D/'root-presentation450-731-v1/ROOT-review-v1/proof.json')
    hard = checked(D/'root-clean731-hard1f-v1/native-launch-v1/comparison/proof.json')
    assert timing['ROM_sha256'] == hard['ROM_sha256'] == FINAL
    assert not hard['cadence']['all_draw_prefix_deferrals']
    assert hard['cadence']['complete_game_totals'] == {
        'candidate':{'updates':240,'draws':168},'baseline':{'updates':240,'draws':168}}
    source = checked(D/'mm-proto-clean-menu-candidates-v1/proof.json')
    cpu = checked(D/'mm-proto-clean-menu-candidates-v1/cpu-v3/proof.json')
    caller = checked(D/'root-clean731-menu-caller-v1/proof.json')
    irq = checked(D/'root-clean731-menu-interrupt-v1/proof.json')
    assert cpu['candidate_ROM_sha256'] == caller['candidate_ROM_sha256'] == irq['ROM_sha256'] == FINAL
    assert any(row['ROM_sha256'] == FINAL and row['original_ordinary_shots_reinstated'] for row in source['variants'])
    assert sha(ROOT/'src/protoman_legacy_shots.inc') == sha(PACK/'source/src/protoman_legacy_shots.inc') == 'ad0241e8872468679f0cb33b7aa4c179e1bd185a3ae45905633f6d304027a73e'
    catalog = json.loads((D/'cv3-parodius-combined-f35-v1/builds-v1/source-inventory-partitions.json').read_text(encoding='utf-8'))
    primary = catalog['primary_source_tool_asset_paths']
    assert len(primary) == 638
    expected = {}
    changes = []
    for item in primary:
        name = item['path']
        before = sha(D/'root-chip-hud-composed-v1/source'/name)
        after = sha(PACK/'source'/name)
        assert sha(ROOT/name) == before, name
        expected[name] = after
        if before != after:
            changes.append(dict(path=name,before_sha256=before,after_sha256=after))
    added = 'src/menu_vram_budget.s'
    assert not (ROOT/added).exists() and added not in expected
    changes.append(dict(path=added,before_sha256=None,after_sha256=sha(PACK/'source'/added)))
    expected[added] = changes[-1]['after_sha256']
    assert sorted(r['path'] for r in changes) == sorted(CHANGES)
    out.mkdir()
    for suffix in SUFFIXES:
        old = default.with_suffix(suffix)
        target = out/'previous-default'/old.name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(old,target)
    shutil.copy2(installed,out/'previous-installed.nes')
    for row in changes:
        if row['before_sha256']:
            target=out/'previous-source'/row['path']
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/row['path'],target)
    builds = []
    try:
        for row in changes:
            shutil.copy2(PACK/'source'/row['path'],ROOT/row['path'])
        for mode,digest in [(None,FINAL),('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
            target=out/('candidate.nes' if mode is None else 'ordinary-'+mode+'.nes')
            command=[sys.executable,'-B',str(ROOT/'tools/build_mmc5_expanded.py'),'--output',str(target)]
            if mode:
                command+=['--flag-off',mode]
            with (out/((mode or 'expanded')+'-build.log')).open('w',encoding='utf-8') as log:
                subprocess.run(command,cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
            assert sha(target)==digest
            builds.append(dict(target=mode or 'expanded',ROM_sha256=digest,passed=True))
        for name,h in expected.items():
            assert sha(ROOT/name)==h,name
        for target in [dated,installed]:
            stage=target.with_name(target.name+'.staging-'+FINAL[:8])
            assert not stage.exists()
            shutil.copy2(out/'candidate.nes',stage)
            assert sha(stage)==FINAL
            stage.replace(target)
        for suffix in SUFFIXES:
            shutil.copy2((out/'candidate.nes').with_suffix(suffix),default.with_suffix(suffix))
        assert sha(default)==sha(installed)==sha(dated)==FINAL
    except BaseException as error:
        for row in changes:
            if row['before_sha256']:
                shutil.copy2(out/'previous-source'/row['path'],ROOT/row['path'])
            else:
                (ROOT/row['path']).unlink(missing_ok=True)
        for old in (out/'previous-default').iterdir():
            shutil.copy2(old,default.parent/old.name)
        shutil.copy2(out/'previous-installed.nes',installed)
        (out/'failure.json').write_text(json.dumps(dict(passed=False,adopted=False,error=repr(error),
            traceback=traceback.format_exc(),rollback_default_sha256=sha(default),
            rollback_installed_sha256=sha(installed)),indent=2)+'\n',encoding='utf-8')
        raise
    proof=dict(passed=True,adopted=True,goal_complete=False,ROM_sha256=FINAL,parent_ROM_sha256=PARENT,
               source_files=changes,checked_primary_inputs=len(expected),builds=builds,
               menu_proof=dict(path=str(args.menu_proof),sha256=sha(args.menu_proof)),
               menu_visual_proof=dict(path=str(args.menu_visual_proof),sha256=sha(args.menu_visual_proof)),
               finite_timing_receipt_sha256=sha(D/'root-presentation450-731-v1/ROOT-review-v1/proof.json'),
               pressure_comparison_sha256=sha(D/'root-clean731-hard1f-v1/native-launch-v1/comparison/proof.json'),
               original_shots_retained=True,installed=str(installed),dated_build=str(dated),rollback=str(out),
               limits='Targeted menu and level-start timing adoption only. Existing37 route clears remain exact3cee evidence, not retagged. Body/shot flicker, every-powerup, other-mode/shortcut, missing music, broader performance and campaign work remain open.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(out/'proof.json',ROOT/'docs/qa/presentation-timing-adoption-2026-10-26.json')
    print(json.dumps(dict(adopted=True,ROM_sha256=FINAL,installed=str(installed))))


if __name__ == '__main__':
    main()
