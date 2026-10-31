"""Stage exact reviewed source/native research without unrelated user edits."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

R = Path(__file__).resolve().parents[2]
Q = R/'docs/qa/checkpoints/2026-10-31'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(['git', *args], cwd=R, capture_output=True, text=True, check=True).stdout


def main():
    assert not git('diff','--cached','--name-only').strip()
    selected = {Path(__file__)}
    for name in ['wwf-action-source-recovery-v1','smb3plus-low-table-factor-v1',
                 'smb3plus-low-factor-native-v1','battletoads-jmp-router-resources']:
        selected.update(p for p in (Q/name).iterdir() if p.is_file())
    members = json.loads((Q/'smb3plus-low-table-factor-v1/source-members.json').read_text())
    selected.update(R/p for p in members if p.startswith('tools/') and Path(p).suffix in ['.py','.s','.inc'])
    selected.update(R/'tools/audit'/n for n in [
        'prepare_wwf_action_discovery_1031_v1.py','wwf_action_vm_recovery_1031_v1.py',
        'freeze_wwf_action_recovery_1031_v1.py','prepare_smb3plus_low_factor_native_1031_v1.py',
        'prepare_smb3plus_low_factor_native_retry_1031_v1.py','freeze_smb3plus_factor_native_1031_v1.py',
        'review_bt_jmp_row_proposal_1031_v1.py','cf_p1_restore_factor_resource_grant_1031_v1.py',
        'cf_p1_restore_source_amendment_1031_v1.py','measure_bt_jmp_row_cold_proposal_v1.py',
        'prepare_contra_force_p1_native_restore_proposal_v1.py',
        'prepare_contra_force_p1_native_restore_proposal_v2.py'])
    selected.add(R/'tools/reference/bt_jmp_row_cold_proposal_v1.s')
    selected.update(R/'tools/reference'/('contra_force_p1_native_restore_proposal_v'+str(v)+'.s') for v in [1,2])
    target = Q/'contra-force-p1-experimental-resources'
    for n in ['native-restore-factor-grant-v1.json','native-restore-source-amendment-v2.json']:
        selected.add(target/n)
    for source, name in [
        (R/'build/contra-force-p1-native-restore-proposal-v1/proposal.json','native-restore-rejected-source-proposal-v1.json'),
        (R/'build/contra-force-p1-native-restore-proposal-v2/proposal.json','native-restore-corrected-source-proposal-v2.json'),
        (R/'build/contra-force-p1-restore-arena-controls-v3/controls.json','native-restore-synthetic-arena-controls-v3.json'),
        (R/'build/bt-jmp-row-cold-proposal-v1/proposal.json','BT-jmp-router-proposal-v1.json')]:
        dest = target/name
        assert not dest.exists()
        shutil.copy2(source,dest);selected.add(dest)
    latest = Path.home()/'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'
    assert sha(latest) == '01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'
    progress = R/'docs/qa/continuation-2026-10-31-unlock-source.json'
    assert not progress.exists()
    d = dict(status='ACTIVE_GOAL_SOURCE_AND_NATIVE_PROGRESS_NO_NEW_UNLOCK_THIS_STEP',
        previous_goal_turn='progress: installed68 and SMB1 Peach native verification, pushedf8070579',
        installed_playable=68, installed_SHA256=sha(latest), installed=str(latest),
        M3_factor=dict(candidate='e54b91fa15b335bb17fd24fa7a0b667ef50bf31c8fad900d6c1a1ec38526116a',
            source_handoff='fea3b4521242846abe7b38053f2bb0283d261c626cd351c1ba48f3d405fdb260',
            native=True, installed=False, unchanged_captured_PNGs=8,
            Toad=dict(Main=359,ISR=720,lag_NMIs=14), Peach=dict(Main=360,ISR=720,lag_NMIs=0),
            source_qualified_reclaim_bytes=398, CF_conditional_reservation=67, remaining_M3=331,
            required_next='Genuine source composition onto final CF/BT common child; all broader abilities/routes remain incomplete.'),
        WWF=dict(playable_host=False, original_controller_trace_dispatches=1076,
            original_CPU_input_cases=66, original_actor_updates=4224, source_art_matches=4224,
            required_next=['Genuine action VM host translation','84-page source art/palette fit','Original looping music','Native host admission and full route/powerup tests']),
        CF=dict(ready=False, P1_restore_source='a75ec54c06142d0619af5dced2e0b6351375f65c0566d3feb24613725d8e5a25',
            P1_restore_actual_linked=False, synthetic_arena_valid_epochs=6, synthetic_arena_invalid_cookie_bytes=16,
            shared_source_join_pending=True, native=False),
        BT=dict(ready=False, linked223_router_finite_pass=True,
            actual_native_world32_successor='9b1089d254dfb18ceb5bb2bc14951f2b782aa40cf82fcde63b9cb07d82f456c6',
            final_source_freeze_in_progress=True, native=False),
        actual_source_constraints=['main.o has256 segments; adding a suffix directly exceeds ca65 capacity.',
            'Actual Rogue audio2.o imports __M3_GFX_SIZE__; keep true combined footprint, not prefix size.',
            'RODATA reuse plan requires all final common objects empty/no metadata consumers before source change.',
            '93:AFA7..<AFF6 is live79B bbox code and must remain intact.'],
        storage_cap_bytes=70000000000, last_native_preflight_workspace_bytes=55006055326,
        native_capture_policy='4PNG/64files/512MiB per run;90s wall retry retains full360-frame controller policy after terminal60s timeout. No videos.',
        goal_complete=False, all_characters_1_1_and_every_powerup_complete=False)
    progress.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n');selected.add(progress)
    paths=[]
    for p in sorted(selected):
        p=p.resolve();assert p.is_relative_to(R) and p.is_file(),p
        assert p.name!='current-roster-progress-2026-10-27.json'
        assert p.suffix.lower() not in ['.nes','.o','.dbg','.lbl','.mp4','.avi','.wav','.bin'],p
        assert p.stat().st_size<100000000,p
        paths.append(p.relative_to(R).as_posix())
    git('add','--',*paths)
    staged=git('diff','--cached','--name-only').splitlines()
    assert set(staged)<=set(paths) and 'docs/qa/current-roster-progress-2026-10-27.json' not in staged
    print(json.dumps(dict(staged_files=len(staged), staged_bytes=sum((R/p).stat().st_size for p in staged),
        installed_SHA256=sha(latest), goal_complete=False)))


if __name__ == '__main__':
    main()
