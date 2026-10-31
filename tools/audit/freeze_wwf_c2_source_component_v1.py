"""Freeze true selected-state WWF source relocation and finite CPU receipts."""
from pathlib import Path
import hashlib,json,re,zipfile
R=Path(__file__).resolve().parents[2]
L=R/'build/wwf-c2-symbol-relocation-v3'
O=R/'build/wwf-c2-source-qualified-v1'
D=R/'docs/qa/checkpoints/2026-10-31/wwf-c2-source-component-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def main():
    assert not O.exists()and not D.exists();O.mkdir();D.mkdir(parents=True)
    inputs=R/'build/wwf-c2-relocation-controls-v2'
    tests=[inputs/'controls.json',inputs/'inputs/controls.json',inputs/'directories/controls.json',inputs/'AI/controls.json',R/'build/wwf-c2-addressing-controls-v1/controls.json',R/'build/wwf-c2-interrupt-controls-v1/controls.json']
    proof=json.loads((L/'build-proof.json').read_text());reports=[json.loads(p.read_text())for p in tests]
    assert all(q['passed']for q in reports)
    for q in [proof,*reports]:
        for p,h in q['bindings'].items():assert sha(p)==h,p
    covered=set(map(int,reports[1]['observed']['relocated']['handlers']))|set(map(int,reports[2]['handler_counts']))
    assert len(covered)==60
    labels=proof['labels'];source=(L/'vm.s').read_text();calls=[];pc=None
    for line in source.splitlines():
        m=re.match(r'WfN_([A-F0-9]{4}):',line)
        if m:pc=int(m[1],16)
        m=re.match(r'\s+(jsr|jmp) (WfCb\w+)',line)
        if m:calls.append(dict(native_PC=pc,linked_PC=labels[f'WfN_{pc:04X}'],transfer=m[1],callback=m[2]))
    limits=[
        'No cartridge/common source, shared allocation, MMC5 mapping, native run, readiness or installation is changed.',
        'The nine callback bodies remain genuine dynamically executed donor-environment oracles. Their replacement by SMB terrain/contact/audio implementations is not established.',
        'The 556 directory-entry cases prove authored script execution in declared CPU contexts, not natural host eligibility for every wrestling action.',
        '60 of 90 handler entries execute in retained cohorts. The remaining30 are assembled from the same original instruction source and symbol proof but are not dynamically covered.',
        'Private interrupt probes cover real6502 save/restore and resumed source contracts, including nestedIRQ. They are not the current cartridge/common NMI/IRQ implementation or donor-callback internal instruction coverage.',
        'The source phase wrappers are foreground-nonreentrant. Future NMI music must use independent context and must preserve every borrowed scratch byte; it cannot recursively enter these foreground APIs.',
        'The initialized native2KiB snapshot remains an external fixture dependency. A real cold host constructor and phase-correct terrain/contact adapter are subsequent work.'
    ]
    api=dict(source=True,isolated_lab=True,no_host_allocation=True,
        entries={n:labels[n]for n in ['WfInitDescriptors','WfSelectAction','WfAdoptRequests','WfVmTick','WfVmDispatch','WfReadOperand']},
        phase_order=['native controller poll with held/fresh inputs','WfSelectAction X=actor0/1,Y=0/2; Y=FF is explicit AI tail','WfAdoptRequests once after input selection','WfVmTick with original71 phase and8D video counter; each actor updates every2 source video frames'],
        identity='Actor0 reads descriptor2B; actor1 reads2A. Genuine descriptors retain original stats, per-wrestler script directory and side effects.',
        state=dict(base=0xc000,bytes=2048,projection='Every genuine state operand below2000 uses WfState+(operand&7FF); original code/data pointers translate through genuine source symbols.'),
        scoped_pairs=dict(physical_R0_R7=proof['scoped_R0_R7'],pointer_fields=proof['pair_helpers'],dispatch='JMP(WfState+$01F), no zero-page dispatch alias',reads='Five13B helpers reload canonical C2 pointer before every indirect LDA;1F and25 share a physical pair only in separate helper phases.'),
        pointer_rules='Only the five declared16-bit pointer fields translate code/data addresses. Paired source writes preserve original order. Indexed actor state is declaredX0/1; every405 actual indexed instruction is compared for all64flags. E9BB retains16-bit00D3+Y addressing, including original01D2 forYFF, at selectedC1D2.',
        scratch_context=dict(private_C2=[0xdfd0,0xdfd4],foreground_bytes=2,callback_bytes=2,public_stack_extra=10,oracle_gateway_stack_extra=22),
        returned_ABI='Actual original returnedAXYP/SP, not a generic preserving routine. Public/callback wrappers restore every physicalR0..7 byte around genuine compiled code. Callback outputs, including flags, mapper/APU writes and ordered source state are exact.',
        callbacks=[dict(name=name,original_entry=int(address),compiled_wrapper=labels[name],environment_stub=labels['WfEnv_'+name],gateway=labels['WfOracle_'+name],calls=[q for q in calls if q['callback']==name])for address,name in proof['callback_original'].items()],
        handlers=[dict(opcode=op,linked_entry=labels[f'WfOpcode{op:02X}'],dynamically_covered=op in covered)for op in range(8,0x62)],
        interrupt_contract='On an interrupt every borrowed physicalR0..7 byte and live upper page1 must be preserved, along with AXYP and actual PC. Private tested probe saves all8, permits legal nestedIRQ after save, restores and RTIs. Source/callback phase scratch is untouched by the probe.',limitations=limits)
    save(O/'integration-api.json',api)
    footprint=dict(source=True,VM_code_bytes=proof['code_bytes'],dispatch_bytes=180,scripts_bytes=3634,A3_used_bytes=7726,descriptors_directory_bytes=498,C2_helpers_bytes=1157,C2_state_bytes=2048,private_phase_scratch_bytes=4,indirect_ZP_pairs=4,borrowed_ZP_bytes=8,long_branch_native_PCs=proof['long_branch_sites'],native_callback_code_bytes_included=False,selected_cache_resources_granted=False)
    save(O/'footprint.json',footprint)
    note='''True symbolic WWF C2 state relocation, isolated CPU source component.

The compiled VM contains the original per-wrestler interpreter, all90 genuine opcode handlers, six original81-byte descriptors,145 native action-directory words and full3634-byte script bundle. No prerecorded action timeline or generic attack replaces source instructions. All RAM operands are genuine selected-state symbols. Three expanded branches use assembled6502 branch/JMP sequences. Original dispatch is JMP through the selected C2 word.

The four scoped R0..7 pairs serve only five actual indirect read helpers. Every read reloads its canonical selected-state pointer. The public and callback wrappers separately save all8 physical scratch bytes on the real CPU stack and restore actual incoming/returned flags and registers. The dynamically executed original callback oracle deliberately clobbers all8 afterward; compiled source still returns exact scratch state.

Controls:132 input cases/8448 updates including actor1;556 action entries/35584 updates;768 fullflag AI calls. Original66 cases/4224 updates reproduce the prior source recovery. Ordered selected-state writes, callback inputs/outputs/order, native mapper/audio effects and returnedAXYP/SP are exact under declared address projection. Handler coverage remains60/90. Addressing additionally checks259200 actual indexed instructions,81920 E9BB16-bit page1 aliases and163840 pointer-helper cases. Real assembled privateNMI/IRQ/nestedIRQ probes pass2748 cuts at916 reached instruction seams, minimumSP199. These probes do not claim actual MMC5/commonISR integration.

Footprint:3912 code +180 dispatch +3634 scripts =7726 A3 bytes;498 descriptor/directory bytes;1157 C2 helper bytes;2048 selected-state bytes;4 phase-context bytes. Original donor callbacks, real host constructor, terrain/contact/ring/progression/audio adapters and host mapping remain outside this component. No host lease or unlock is implied.

Replay generated source with the pinned ca65/ld65 recipes and guarded output paths in build-proof.json/link/build logs, always into a NEW laboratory root. The donor ROM is an external hash-pinned input. The2KiB native fixture is included; donor ROM and parent cartridge images are not archived. No six duplicated cache images are produced.

Retained negatives:missing action0 genuineimport(v1);overlapping oracle gateway/environment slots(v2);first C2 observer omitted native mapperwrites for Audio12(v1 controls). The corrected observer includes those exact writes rather than changing source. Original older source-control report prose saying dense state relocation is absent is inherited; this successor's explicit source/projection/control scope supersedes that description without altering the frozen reports.
'''
    (O/'README.txt').write_text(note)
    toolnames=['prepare_wwf_c2_symbol_relocation_v1.py','prepare_wwf_c2_symbol_relocation_v2.py','prepare_wwf_c2_symbol_relocation_v3.py','wwf_c2_relocation_model_v1.py','wwf_c2_relocation_model_v2.py','wwf_c2_relocation_controls_v1.py','wwf_c2_relocation_controls_v2.py','wwf_c2_addressing_controls_v1.py','wwf_c2_interrupt_controls_v1.py','wwf_action_source_controls_v2.py','wwf_action_directory_controls_v1.py','wwf_action_ai_controls_v1.py','prepare_wwf_action_source_lab_v2.py','wwf_action_vm_recovery_1031_v1.py','wwf_roster_source_review_v1.py','private_build_outputs_v1.py']
    files={R/'tools/audit'/n for n in toolnames}|{Path(__file__),*L.iterdir(),*tests,O/'integration-api.json',O/'footprint.json',O/'README.txt'}
    files|={R/'build/wwf-c2-symbol-relocation-v1/negative.json',R/'build/wwf-c2-symbol-relocation-v2/build-proof.json',R/'build/wwf-c2-symbol-relocation-v2/environment-negative.json',R/'build/wwf-c2-relocation-controls-v1/directories/controls.json',R/'build/wwf-c2-relocation-controls-v1/inputs/controls.json',R/'build/wwf-action-donor-native-1031-v1/discovery/capture/ram-match-entry.bin',R/'docs/qa/checkpoints/2026-10-31/wwf-action-source-component-v1/handoff.json',R/'docs/qa/checkpoints/2026-10-31/wwf-host-resource-fit-v1/handoff.json'}
    files|=set((R/'build/wwf-c2-interrupt-controls-v1').iterdir())
    files={p for p in files if p.is_file()}
    external={Path(p)for q in [proof,*reports]for p in q['bindings']}
    bindings={str(p.resolve()):sha(p)for p in sorted(files|external)}
    members={p for p in files if p.suffix not in ['.o','.dbg','.lbl','.map','.dep','.lst']and(p.suffix!='.bin'or p.name=='ram-match-entry.bin')}
    assert len(members)<128 and sum(p.stat().st_size for p in members)<12000000
    with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(members):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(O/'source-only.zip')as z:
        assert len(z.namelist())==len(members)
        for p in members:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    for p,h in bindings.items():assert sha(p)==h,p
    handoff=dict(source=True,source_CPU_lab=True,no_host_allocation=True,native_host=False,installed=False,status='TRUE_C2_WWF_SOURCE_ORACLE_PASS_NO_HOST_UNLOCK',source_build=sha(L/'build-proof.json'),bindings=bindings,members={p.relative_to(R).as_posix():sha(p)for p in sorted(members)},archive_sha256=sha(O/'source-only.zip'),archive_bytes=(O/'source-only.zip').stat().st_size,footprint=footprint,actor_input_cases=132,input_updates=8448,directory_cases=556,directory_updates=35584,AI_flag_cases=768,dynamic_handlers=60,total_handlers=90,actual_interrupt_cuts=2748,interrupt_seams=916,min_interrupt_SP=199,limitations=limits)
    save(O/'handoff.json',handoff)
    for name in ['handoff.json','source-only.zip','integration-api.json','footprint.json','README.txt']:(D/name).write_bytes((O/name).read_bytes())
    (D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(files)if p.parent==R/'tools/audit'and p.name.startswith(('wwf_c2','prepare_wwf_c2','freeze_wwf_c2')))+'\n'+D.relative_to(R).as_posix()+'/\n')
    print(json.dumps(dict(passed=True,handoff=str(D/'handoff.json'),SHA256=sha(D/'handoff.json'),bindings=len(bindings),members=len(members),archive_bytes=handoff['archive_bytes'])))
if __name__=='__main__':main()
