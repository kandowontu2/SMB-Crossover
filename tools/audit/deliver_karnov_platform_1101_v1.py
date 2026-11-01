"""Publish the tested pipe/platform repair; keep the full roster goal open."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'build/karnov-native-platform-1101-v1'
D=R/'docs/qa/checkpoints/2026-11-01/karnov-platform-nightly-v1'
DEST=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='58e50db6ceead7c3706087c92d6e49014f05ff8b80b000be30c27b4e7dfa11f2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    from nightly_patch_guard_v1 import check
    assert sha(O/'candidate.nes')==PIN
    assembly=json.loads((O/'assembly.json').read_text())
    assert assembly['candidate_sha256']==PIN
    assert sha(DEST)==assembly['base_sha256']
    controls=json.loads((O/'manager-CPU.json').read_text());assert controls['passed'] and controls['candidate_sha256']==PIN
    runs=[R/'build'/n/'probe' for n in ['karnov-native-platform-crossing-1101-v1','karnov-native-platform-stack-1101-v2','karnov-platform-menu-1101-v1']]
    results=[]
    for run in runs:
        q=json.loads((run/'capture/result.json').read_text());binding=json.loads((run/'capture/binding.json').read_text())
        assert q['passed'] and binding['exit_code']==0 and binding['ROM_sha256']==PIN
        results.append(q)
    stack=json.loads((runs[1]/'capture/stack.json').read_text());assert stack['minimum_sampled_SP']>=160
    assert results[0]['both_tall_pipes_crossed'] and results[1]['both_tall_pipes_crossed']
    assert results[2]['heading_errors']==results[2]['visible_mask_writes']==0 and not results[2]['anomalies']
    check(DEST)
    D.mkdir(parents=True,exist_ok=True)
    files=[Path(__file__),O/'assembly.json',O/'manager-CPU.json']+list(O.glob('*.s'))
    files += [R/'tools/audit'/n for n in ['prepare_karnov_native_platform_1101_v1.py','check_karnov_native_platform_1101_v1.py','prepare_karnov_platform_crossing_1101_v1.py','prepare_karnov_platform_stack_1101_v1.py','prepare_karnov_platform_route_1101_v1.py','prepare_karnov_stage_route_1101_v4.py','prepare_karnov_stage_route_1101_v3.py','prepare_karnov_stage_route_1101_v2.py','prepare_karnov_stage_route_1101_v1.py','prepare_karnov_current_selection_1101_v1.py','prepare_current_roster_menu_1101_v1.py']]
    files += [R/'tools'/n for n in ['prepare_dragon_power_platform_v1.py','prepare_dragon_power_two_platforms_v1.py']]
    for run in runs:
        files += [run/'controller.lua',run/'ready.json',run/'capture/result.json',run/'capture/binding.json']
    files += [runs[1]/'capture/stack.json',runs[0]/'capture/stage-endpoint.png']
    packet=D/'source-and-native.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(set(files)):z.write(p,p.relative_to(R).as_posix())
    assert packet.stat().st_size<500000
    DEST.write_bytes((O/'candidate.nes').read_bytes())
    assert sha(DEST)==PIN;check(DEST)
    receipt=dict(passed=True,installed=True,complete=False,backup_created=False,ROM_sha256=PIN,output_sha256=PIN,
        replaced_sha256=assembly['base_sha256'],destination=str(DEST),selectable_identities=86,total_menu_identities=90,
        checkpoint=str(D.relative_to(R)),owning_candidate=str(O/'candidate.nes'),owning_build_recipe='tools/audit/prepare_karnov_native_platform_1101_v1.py',
        source_packet=dict(path=str(packet.relative_to(R)),sha256=sha(packet),bytes=packet.stat().st_size),
        inherited_source_checkpoint='docs/qa/checkpoints/2026-11-01/kirby-approach-nightly-v3',
        native_pipe_crossings=2,each_crossing_frames=3013,native_menu_identities=90,native_menu_transitions=124,
        manager_CPU_cases=controls['unchanged_Goku_and_foreign_manager_cases'],sampled_native_stack=stack,
        limits=['No full 1-1 or shortcut completion claim. A subsequent automatic route fell into the first pit; route planning remains unfinished.',
                '160 manager CPU comparisons preserve tested Goku/foreign behavior; this is not a full Goku playthrough.',
                'Native stack sampling is not exhaustive IRQ-cut verification. Previous Kirby code is byte-preserved outside these declared spans.',
                'Remaining characters, attacks, original audio, campaigns and all-character/all-powerup qualification remain unfinished.'])
    (D/'handoff.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (D/'README.md').write_text('# Karnov native-platform repair\n\nROM SHA-256: `'+PIN+'`.\n\nKarnov now uses the existing native elevators before both tall 1-1 pipes. Real platform support is reconciled with his original actor before its next update, allowing him to move and jump off. Original jump constants are unchanged. Two cold controller runs clear both pipes; 160 old/new manager CPU cases preserve tested Goku/foreign behavior. All90 menu identities and124 transitions pass the heading/rendering observer.\n\nThe native stack observer sampled minimum SP170. This is not exhaustive interrupt-cut proof. Full-stage, shortcut, every-character and every-powerup verification remain incomplete. No roster unlock was added. The source packet inherits the preceding Kirby checkpoint; the assembly receipt records every changed span and its exact preimage.\n')
    current=R/'docs/qa/continuation-current.json';q=json.loads(current.read_text())
    q['installed_nightly']=receipt;q['current_owning_candidate']=str(O/'candidate.nes');q['current_owning_build_recipe']=receipt['owning_build_recipe']
    q['source_override_required']='Compose the complete367 Kirby source repairs, then this Karnov platform assembly patch: resident bridge, bank26 manager/dispatch, actor support reconciliation and both revised cookie copies. Do not substitute older Main or kernel images.'
    current.write_text(json.dumps(q,indent=2)+'\n')
    (O/'source-stage.json').write_text(json.dumps(dict(passed=True,ROM_sha256=PIN,checkpoint=str(D),scope='Qualified WIP pipe repair, not full goal completion'),indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
