"""Freeze the isolated assembled WWF action component and finite CPU receipts."""
from pathlib import Path
import collections
import hashlib
import json
import re
import zipfile

R=Path(__file__).resolve().parents[2]
L=R/'build/wwf-action-source-lab-v2'
O=R/'build/wwf-action-source-component-qualified-v1'
D=R/'docs/qa/checkpoints/2026-10-31/wwf-action-source-component-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')


def main():
    assert not O.exists() and not D.exists()
    proof=json.loads((L/'build-proof.json').read_text())
    tests=[R/'build'/n/'controls.json'for n in ['wwf-action-source-controls-v2','wwf-action-directory-controls-v1','wwf-action-ai-controls-v1']]
    reports=[json.loads(p.read_text())for p in tests]
    assert proof['actual_source_total_bytes']==7560 and all(q['passed']for q in reports)
    for q in [proof,*reports]:
        for p,h in q['bindings'].items():assert sha(p)==h,p
    reference=R/'build/wwf-action-vm-recovery-1031-v1/controls.json'
    old=json.loads(reference.read_text());assert old['passed']and old['genuine_script_updates']==4224
    for p,h in old['bindings'].items():assert sha(p)==h,p
    O.mkdir();D.mkdir(parents=True)
    source=(L/'vm.s').read_text();calls=[];pc=None
    for line in source.splitlines():
        m=re.match(r'WfN_([A-F0-9]{4}):',line)
        if m:pc=int(m[1],16)
        m=re.match(r'\s+(jsr|jmp) (WfCb\w+)',line)
        if m:calls.append(dict(native_PC=pc,transfer=m[1],callback=m[2],source_label=f'WfN_{pc:04X}'))
    labels=proof['variants']['native']['labels'];reloc=proof['variants']['relocated']['labels']
    covered=set(int(x)for x in reports[0]['observed']['relocated']['handlers'])|set(int(x)for x in reports[1]['handler_counts'])
    rows=[dict(opcode=op,native_entry=labels[f'WfOpcode{op:02X}'],relocated_entry=reloc[f'WfOpcode{op:02X}'],source_label=f'WfOpcode{op:02X}',dynamically_covered=op in covered)for op in range(8,0x62)]
    core=reports[1]['observed']; observed_read=set(core['read']);observed_write=set(core['write']);nonstack=(observed_read|observed_write)-set(range(0x100,0x200))
    api=dict(source=True,isolated_CPU_component=True,no_host_allocation=True,
        entries={name:dict(native=labels[name],relocated=reloc[name])for name in ['WfInitDescriptors','WfSelectAction','WfAdoptRequests','WfVmTick','WfVmDispatch','WfReadOperand']},
        native_state_inputs={
            'identity':'Actor0 uses descriptor ID2B; actor1 uses2A. Both IDs must be0..5.',
            'WfInitDescriptors':'Reads original IDs2A/2B and genuine81B records; writes native stats/palette globals exactly as D1A5. No invented blanket state reset.',
            'WfSelectAction':'X=actor0/1,Y=controller offset0/2; held/fresh at0D+2X/0E+2X. Y=FF invokes explicit native AI boundary. Original CB+X/action/contact gates remain active.',
            'WfAdoptRequests':'Runs genuine pending3E/3F to current3C/3D adoption after original input polls; does not synthesize requests.',
            'WfVmTick':'71&1 chooses actor;8D is the original video-frame counter. A selected actor updates every2 video frames, not every host Main and not an invented NMI clock.'},
        return_ABI='Genuine original returned A/X/Y/P/SP; the component is not a preserving wrapper. RTS uses the caller real return frame.',
        callback_ABI='Named JSR/tail imports preserve their original register/state/flag contract. Lab adapters execute actual native callback code against shared source state and the existing caller return frame; host replacements remain unimplemented.',
        callbacks=[dict(name=name,native_entry=pc,isolated_dispatch_slot=proof['variants']['relocated']['callbacks'][name],source_call_sites=[q for q in calls if q['callback']==name])for name,pc in proof['callback_original_entries'].items()],
        handler_table=rows,
        data_origins_retained=True,
        limitations=['No host services, allocation, menu, native launch, audio engine, raster or unlock is installed.',
            'Original-state compatibility currently uses2KiB native RAM plus donor callback environment, not a proven compact host overlay.',
            'Both actor fixtures are explicit CPU cases. The separate556 directory-entry cases do not prove original controller eligibility.',
            '30 opcode entries and additional conditional branches are source-byte proven but not dynamically covered by these cohorts.',
            'Original E9BB STA00D3,Y may reach01D2 forY=FF; preserve/document this original dead-stack behavior before future state/stack relocation.',
            'Native-origin code compares all RAM/stack/writes/cycles. Relocated code compares nonstack RAM and ordered writes plus every live upper-stack byte, with only two exact dispatch-address store sites symbolically translated. Dead return bytes relocate.'])
    save(O/'integration-api.json',api)
    footprint=dict(source=True,no_host_allocation=True,code_bytes=3248,dispatch_table_bytes=180,descriptor_bytes=486,descriptor_pointer_bytes=12,script_bundle_bytes=3634,total_emitted_source_bytes=7560,
        code_and_dispatch_bytes=3428,relocated_code_range=[0x9000,0x9d64],
        original_state_compatibility_envelope_bytes=2048,
        observed_core_nonstack_RAM_union_bytes=len(nonstack),observed_core_ZP_union_bytes=len([a for a in nonstack if a<256]),
        observed_core_reads=sorted(observed_read),observed_core_writes=sorted(observed_write),
        static_RAM_operand_bases=proof['static_RAM_base_operands'],
        observed_native_callback_reads=core['callback_read'],observed_native_callback_writes=core['callback_write'],
        minimum_fixture_stack_pointer=core['min_sp'],
        notes=['Observed counts are coverage measurements, not a maximum state size or sufficient host allocation.',
            'Indexed/indirect operands and30 not-yet-executed handlers must be included in any future compact-state proof.',
            'Original descriptors are81B physical records in non-ID order. D1A5 reads through4F; the authentic extra byte is retained.',
            'The7,560B count excludes the original native callback code/data and future host movement/contact/audio adapters.'])
    save(O/'footprint.json',footprint)
    README='''Isolated source-backed WWF action VM, CPU-only. No host resources or unlock.

The source contains the genuine request adoption, input selector, descriptor producer, E2E8 interpreter, E385 dispatch and all90 opcode handlers08..61. vm.s contains actual labelled6502 instructions and symbolic control transfers; this is not recorded action playback. The original per-wrestler3634B directory/script bundle and six81B records are unchanged. Native-origin assembly matches every emitted original byte. A second true link relocates executable code/dispatch to9000..<9D64 while retaining data origins.

The API exposes explicit AI, ring-clamp, depth-probe, ring-bounds, contact, RNG and three audio-cue callbacks. The isolated CPU adapter executes the original ROM functions dynamically, on the original live return frame and shared state. It returns their real flags/registers/side effects. These environment implementations are not an SMB port and are excluded from the7,560B component size.

Controls reproduce all66 original controller cases/4224 source updates, then the same66 cases for actor1. Each update compares genuine source and assembled native/relocated code: returned AXYP/SP, RAM, ordered writes, callback order/output, mapper and audio state. Native-origin cycles and all stack bytes are exact. Relocated dead return bytes differ; all live upper-stack bytes remain exact. The only nonstack symbolic translation is validated at the two actual E39C/E3A1 handler-address stores. Root's prior original1076-dispatch trace and4224 art matches remain bound.

A separate bounded556-entry cohort starts every authentic nonzero action directory entry for both actors, in the initialized separated and a declared near-opponent context, for35584 updates. It is an action-entry fixture, not evidence every wrestling move is naturally eligible in SMB.60/90 handler entries execute. An additional768 full-flag selector cases reach the genuine native AI tail. Unexecuted handlers are byte/source proven, not dynamically qualified. Native callbacks reached include ring/contact and Audio12; the other callback boundaries remain explicit and unclaimed dynamically.

Footprint:3248B executable code,180B dispatch,486B descriptor records,12B descriptor pointers,3634B scripts =7560B. The lab retains the original2KiB state environment. The action-entry suite observes116 nonstack core bytes,107 in ZP; those are coverage counts, not a safe compact allocation. Original indexed instructions may also touch dead page1 (E9BB/01D2); no silent correction was made. Native callback code, host terrain/progression/contact, full palette/art storage, music/audio and an actual host lifecycle/menu remain future work after resource review.

Build: python tools/audit/prepare_wwf_action_source_lab_v2.py into a NEW output root (the immutable generated source is in this archive). All actual compiler/link outputs were guarded. Then run the three bound source/directory/AI tools into new result roots. The original USA ROM is an external hash-pinned input; the initialized2KiB native fixture is archived here. Existing output directories are deliberately never overwritten.

Retained negatives: v1 descriptor layout assumption failed before compile; corrected authentic81B order in v2. The first relocation observer indexed the high dispatch byte incorrectly; its exact failure is retained, and v2 validates the real table+Y+1 producer. No source semantics were changed to pass either fixture.
'''
    (O/'README.txt').write_text(README)
    tools=[R/'tools/audit'/n for n in ['prepare_wwf_action_source_lab_v1.py','prepare_wwf_action_source_lab_v2.py','wwf_action_source_controls_v1.py','wwf_action_source_controls_v2.py','wwf_action_directory_controls_v1.py','wwf_action_ai_controls_v1.py','private_build_outputs_v1.py','wwf_action_vm_recovery_1031_v1.py','wwf_roster_source_review_v1.py']]+[Path(__file__)]
    files=set(tools)|{p for p in L.iterdir()if p.is_file()}|set(tests)|{O/'integration-api.json',O/'footprint.json',O/'README.txt',R/'build/wwf-action-source-lab-v1/negative.json',R/'build/wwf-action-source-controls-v1/controls.json',reference,R/'build/wwf-action-vm-recovery-1031-v1/executed-PCs.json',R/'build/wwf-action-donor-native-1031-v1/discovery/capture/ram-match-entry.bin',R/'docs/qa/checkpoints/2026-10-31/wwf-action-source-recovery-v1/handoff.json'}
    external={Path(p)for q in [proof,*reports,old]for p in q['bindings']}
    external.update(R/'tools/Windows/cc65/bin'/n for n in ['ca65.exe','ld65.exe'])
    bindings={str(p.resolve()):sha(p)for p in sorted(files|external)}
    # Archive replayable source/data/receipts, not donor ROM or redundant binaries.
    members={p for p in files if p.suffix not in ['.o','.dbg','.lst','.dep','.map','.lbl'] and p.name not in ['native.bin','relocated.bin','native.link.bin','relocated.link.bin']}
    assert len(members)<96 and sum(p.stat().st_size for p in members)<16777216
    archive=O/'source-only.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(members):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(members)
        for p in members:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    for p,h in bindings.items():assert sha(p)==h,p
    handoff=dict(source=True,source_CPU_lab=True,native_host=False,playable_host=False,installed=False,no_host_allocation=True,status='ASSEMBLED_WWF_ACTION_COMPONENT_ORACLE_PASS_NO_HOST_UNLOCK',original_ROM=proof['original_ROM'],code_bytes=3248,source_total_bytes=7560,handlers=90,dynamic_handlers=len(covered),original_cases=66,original_updates=4224,actor_cases=132,controller_tick_pairs=8448,directory_cases=556,directory_tick_pairs=35584,AI_fullflag_cases=768,native_origin_bytes_cycles_exact=True,relocated_controller_cycle_delta=reports[0]['relocated_cycle_delta'],relocated_directory_cycle_delta=reports[1]['relocated_cycle_delta'],bindings=bindings,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,members={p.relative_to(R).as_posix():sha(p)for p in sorted(members)},integration_api_sha256=sha(O/'integration-api.json'),footprint_sha256=sha(O/'footprint.json'),limitations=api['limitations'])
    save(O/'handoff.json',handoff)
    for n in ['handoff.json','integration-api.json','footprint.json','README.txt','source-only.zip']:(D/n).write_bytes((O/n).read_bytes())
    (D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(tools)if p.name not in ['private_build_outputs_v1.py','wwf_action_vm_recovery_1031_v1.py','wwf_roster_source_review_v1.py'])+'\n'+D.relative_to(R).as_posix()+'/\n')
    print(json.dumps(dict(passed=True,handoff=str(D/'handoff.json'),handoff_sha256=sha(D/'handoff.json'),bindings=len(bindings),members=len(members),archive_bytes=archive.stat().st_size)))


if __name__=='__main__':main()
