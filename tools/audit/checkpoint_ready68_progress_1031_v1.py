"""Save the installed68 source/native checkpoint and stage only owned files."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile

R = Path(__file__).resolve().parents[2]
Q = R/'docs/qa/checkpoints/2026-10-31'
N = R/'build/current68-benj-peach-native-1031-v1/peach'
D = Q/'current68-benj-peach-native-v1'
NEW = '01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, data):
    assert not p.exists(), p
    p.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')


def git(*args):
    return subprocess.run(['git', *args], cwd=R, capture_output=True, text=True, check=True).stdout


def main():
    assert not git('diff', '--cached', '--name-only').strip()
    assert not D.exists()
    result = json.loads((N/'capture/result.json').read_text())
    binding = json.loads((N/'capture/binding.json').read_text())
    assert result['passed'] and binding['exit_code'] == 0
    assert result['ROM_sha256'] == binding['ROM_sha256'] == NEW
    for p, digest in binding['bindings'].items():
        assert sha(p) == digest, p
    assert result['main_updates'] == result['source_Main'] == result['source_movement'] == 180
    assert result['vector_guards'] == 360 and result['timing']['lag_nmi'] == 0
    pngs = sorted((N/'capture').glob('*.png'))
    assert len(pngs) == 4
    files = {p for p in N.rglob('*') if p.is_file()} | {Path(__file__), R/'tools/audit/prepare_current68_benj_peach_native_1031_v1.py'}
    assert all(p.suffix.lower() in ['.py', '.lua', '.json', '.csv', '.log', '.png'] for p in files)
    assert len(files) < 64 and sum(p.stat().st_size for p in files) < 4194304
    D.mkdir(parents=True)
    archive = D/'native-results.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(files):
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for p in files:
            assert z.read(p.relative_to(R).as_posix()) == p.read_bytes()
    save(D/'manifest.json', dict(passed=True, candidate=NEW, variant=6, identity='SMB1 Peach',
        controlled_Main_updates=180, vector_restores=360, lag_NMIs=0,
        actual_UI_DMA_checks=result['actual_UI_DMA_checks'], normal_palette='163027',
        root_reviewed_full_frame_PNGs={p.name: sha(p) for p in pngs},
        archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix(): sha(p) for p in sorted(files)},
        limits='Normal palette/UI/movement only; not fire/star/area progression, full1-1 or every-powerup qualification.'))
    (D/'README.txt').write_text('Root reran the corrected SMB1 Peach controller-only visual policy against the installed68 hash01a40d40. All four full frames were reviewed: selection, lives, gameplay entry and movement endpoint. Correct original normal palette163027 is retained;180 genuineMain updates/360 real NMI+IRQ restores/no lag NMIs. HUD still says MARIO. No video, full-level, every-powerup or goal-complete claim.\n', encoding='utf-8', newline='\n')
    selected = {Path(__file__), R/'README.md', R/'docs/qa/functional-roster-ready68-smb3plus-2026-10-31.json'}
    for name in ['smb3plus-current66-source-v1', 'smb3plus-current68-native-v1', 'current68-benj-peach-native-v1', 'cf-preload-name-root-review-v1']:
        selected.update(p for p in (Q/name).iterdir() if p.is_file())
    selected.update(R/p.strip() for p in (Q/'cf-preload-name-source-v1/owned-files.txt').read_text().splitlines() if p.strip())
    source_members = json.loads((Q/'smb3plus-current66-source-v1/source-members.json').read_text())
    selected.update(R/p for p in source_members if p.startswith('tools/'))
    for name in ['prepare_smb3plus_current66_native_1031_v1.py', 'publish_ready68_smb3plus_1031_v1.py',
                 'prepare_current68_benj_peach_native_1031_v1.py', 'propose_smb3plus_low_table_factor_1031_v1.py',
                 'review_cf_preload_checkpoint_1031_v1.py', 'cf_p1_native_first_grant_1031_v1.py',
                 'prepare_contra_force_p1_shared_factor_proposal_v4.py']:
        selected.add(R/'tools/audit'/name)
    selected.add(R/'tools/reference/contra_force_p1_shared_factor_proposal_v3.s')
    p1 = Q/'contra-force-p1-experimental-resources'
    selected.add(p1/'native-first-amendment-v2.json')
    for source, target in [(R/'build/contra-force-p1-shared-factor-proposal-v4/proposal.json', p1/'native-first-proposal-v4.json'),
                           (R/'build/smb3plus-low-table-factor-proposal-1031-v1/proposal.json', Q/'smb3plus-current66-source-v1/low-table-factor-proposal-v1.json')]:
        assert not target.exists()
        shutil.copy2(source, target)
        selected.add(target)
    latest = Path.home()/'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'
    assert sha(latest) == NEW
    progress = R/'docs/qa/continuation-2026-10-31-ready68.json'
    save(progress, dict(status='ACTIVE_EXPANDED_ROSTER_GOAL_INCOMPLETE', installed_playable=68,
        installed=str(latest), installed_SHA256=NEW, individual_identities=84,
        pending_individual_identities=16, pending_Battletoads_family_placeholder=1,
        SMB3plus=dict(source_handoff='8c5c861f81ac849f8f4f28aa76f9f5db0be70a2d866b26994e2fbb2c3ca198b0',
            installed=True, menu_cycle=['Mario', 'Luigi', 'Toad', 'Peach'],
            original_controller_cases=224, original_controller_edges=2016,
            graphics_pairs=9072, foreign_movement_pairs=1344, real_vector_cuts=3380,
            native_Toad_Main=359, native_Toad_lag_NMIs=14, native_Peach_Main=360, native_Peach_lag_NMIs=0,
            remaining=['Ground pound/custom stomp delay', 'Some special art consumers', 'Toad kick SFX', 'Full1-1/every-powerup checks']),
        SMB1Peach=dict(normal_palette='163027', rerun_on_installed68=True, Main_updates=180, vector_restores=360, lag_NMIs=0),
        ContraForce=dict(ready=False, preload_name_source='416bd1b73c2704eaf1e71d0dc01730bd2b6bd81c38465064d35b80f05f6ccca6',
            remaining=['Paired P1 palette/OAM lifecycle and stale epoch retirement', 'Current68 source integration', 'Native admission']),
        Battletoads=dict(ready=False, remaining=['Current-parent own lifecycle integration', 'Cold service router proof', 'Native admission']),
        cap_bytes=70000000000, last_preflight_workspace_bytes=54562087776,
        all_characters_1_1_and_every_powerup_complete=False, goal_complete=False))
    selected.add(progress)
    paths = []
    for p in sorted(selected):
        p = p.resolve()
        assert p.is_relative_to(R) and p.is_file(), p
        assert p.name != 'current-roster-progress-2026-10-27.json'
        assert p.suffix.lower() not in ['.nes', '.o', '.dbg', '.lbl', '.mp4', '.avi', '.wav', '.bin'], p
        assert p.stat().st_size < 100000000, p
        paths.append(p.relative_to(R).as_posix())
    git('add', '--', *paths)
    staged = git('diff', '--cached', '--name-only').splitlines()
    assert set(staged) <= set(paths) and 'docs/qa/current-roster-progress-2026-10-27.json' not in staged
    print(json.dumps(dict(staged_files=len(staged), staged_bytes=sum((R/p).stat().st_size for p in staged),
                         installed_SHA256=NEW, goal_complete=False)))


if __name__ == '__main__':
    main()
