"""Compact replayable NES CPU correction + cold/phase/contact source milestone."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
L=R/'build/wwf-selected-contact-v2';H=R/'build/wwf-isolated-host-phase-v4'
O=R/'build/wwf-selected-host-qualified-v1';D=R/'docs/qa/checkpoints/2026-10-31/wwf-selected-host-lab-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')

def main():
    assert not O.exists()and not D.exists();O.mkdir();D.mkdir(parents=True)
    builds=[L/'build-proof.json',H/'build-proof.json']
    tests=[R/'build'/p/'controls.json'for p in ['wwf-c2-nes-cpu-controls-v1','wwf-isolated-host-phase-controls-v3','wwf-isolated-host-phase-controls-v5','wwf-selected-contact-controls-v3','wwf-selected-contact-interrupts-v1']]
    reports=[json.loads(p.read_text())for p in builds+tests]
    assert all(q.get('passed',q.get('source',False))for q in reports)
    for q in reports:
        for p,h in q['bindings'].items():assert sha(p)==h,p
    labels=reports[0]['labels']
    api=dict(source=True,isolated_CPU_lab=True,no_host_allocation=True,native_host=False,
        actual_compiled_entries={n:labels[n]for n in ['WfHostCold','WfHostFrame','WfEnv_WfCbActorContact','WfEnv_WfCbActorDepthProbe','WfEnv_WfCbRandom','WfCbActorContact','WfCbActorDepthProbe','WfCbRandom']},
        cold='A=actor0 identity0..5, X=actor1 identity0..5, Y=host seed. Clears selected2KiB state, establishes actual actor0ID2B/actor1ID2A, original8039/803B dispatch bootstrap, then genuine D1A5 descriptor producer and original8044..80DB/C8E2..C91C match-state source. No RAM snapshot constructor.',
        phase='A=held NES input, X=fresh edge mask, Y=pause. One accepted video-frame call; actor0 selector/adoption every unpaused call, VM only when original71parity is0, phase modulo6 advances unpaused, original8D video counter advances everycall. PhysicalNMI/lag scheduling is not implemented.',
        contact='Original CD02..CE29 and D0B3..D0BF are real selected-state source, not an oracle. The existing scoped wrappers retain all8 physical scratch bytes. Actual CMP(pointer),Y uses a compiled A-preserving pointer helper. Source contact still expects two wrestlers; host enemy proxy/mapping is future work.',
        CPU='Existing project NesMPU retainsD and performs binary ADC/SBC; all previous C2 input/directory/AI/addressing/interrupt cohorts are rebound unchanged.',
        selected_ranges=dict(VM=[0xa000,0xbe2e],state=[0xc000,0xc800],lab_host_context=[0xc800,0xc810],descriptors=[0xc8c0,0xcab2],frozen_helpers=[0xd400,0xd885],host_code_data=reports[1]['footprint']['range'],selected_contact=reports[0]['footprint']['range'],frozen_phase_scratch=[0xdfd0,0xdfd4]),
        genuine_state_roles={'42/43':'Descriptor byte9 body-anchor height, subtracted by original bodyY producer; not a proven health meter.','79/7A':'Original damage/endurance/health operations; native per-frame recovery belongs to still-unportedCF14 closure.','30/31':'Signed source body/jump displacement used by original bodyY expression.','2E/2F':'Ring-depth/ground-plane Y, distinct from jump displacement.'},
        future_resource_constraints=['Every address here is private lab space only. No host PRG/CHR/WRAM lease is granted by this packet.','The16B lab context atC800 must be relocated by source before any proposed native music-stateC800..<C8C0 use; no overlap is silently accepted.','A future actual shared integration must bind current7b7/e538 source and genuine native symbols, not copy the earlierf0b7 inventory parent wholesale.'],
        remaining_semantics=['Original CF14 recovery/grapple/timer closure is not included in the single-hero phase adapter.','RingClamp/RingBounds/AI and three sound cues still execute donor oracles. Native SMB terrain/progression/contact marshaling is not implemented.','Source contact results still refer to another wrestler. No assumption that every native enemy supports rope/pin/grapple actions.','No original music engine relocation/loop/mixer or audible/native host qualification.','No selected cache loader/epoch/retirement/common ISR/physical clock/menu/readiness installation.'])
    save(O/'integration-api.json',api)
    note='''Isolated WWF selected host-source milestone. No cartridge changes or unlock.

The frozen symbolic VM from480ab1b3 remains intact. New compiled source adds a real cold producer, accepted-video-frame single-hero phase adapter, and selected native contact/depth/RNG closure. The VM image is byteexact. Contact source is399B; host cold/phase source plus constants647B; host context16B. The phase adapter is deliberately narrower than the complete donor frame loop:CF14 recovery/grapple logic, native SMB world boundaries, physical clock, audio engine and cache ownership remain future work.

The original per-wrestler scripts/descriptor behavior are preserved.24 genuine cold cases and4608 accepted-frame pairs match an assembled original-state phase capsule. Selected contact source passes320 RNG +640 depth +9216 contact fullflag cases. All publicAXYP/SP, scoped scratch, projected ordered state writes and source sound/map sideeffects match. Actual APU-write cases in this direct sound-queue scope are0; this is not audible music/SFX qualification. Another2796 actual privateNMI/IRQ/nestedIRQ cuts at932 reached seams resume exactly (minSP199). These are isolated probes, not current MMC5/common interrupts.

CPU-model correction:stockpy65 honorsD arithmetic, while NES retainsD but ADC/SBC remains binary. A new receipt reruns132inputs/8448updates,556directorycases/35584updates,768AIflagcases,504960actual addressing cases,2748privateinterruptcuts and24cold/4608phase pairs with projectNesMPU. Earlier frozen equality understockpy65 remains valid at that narrower scope. Source images are unchanged by the correction.

Retained actual contact failure was NOT caused by decimal mode:both D-clear and NesMPU reproduce it when the new cold adapter omits original8039/803B initialization of native far-dispatch high byte0A=80. NativeFF1F then jumps0012. The corrected cold child includes those genuine source instructions before descriptor/match initialization. Both failure receipts and the diagnostic original-instruction trace are archived. Other retained compile/observer negatives are also bound.

Original42/43, labelledfinal_health in older reports, are descriptor-byte9 body-anchor heights used in original rendering, not a proven health meter. Native79/7A participate in damage/endurance operations. The immutable old label is corrected here without altering archived results.

No whole checkout, donor ROM, parent host ROM or six duplicated cache images is archived. Source-only ZIP includes actual assembled source, guarded build recipes, finite receipts, negatives and the CPU-model note. The donor ROM and previousC2source packet are external hash-pinned inputs. Rebuild only into NEW output roots with all compiler/config outputs validated before execution.
'''
    (O/'README.txt').write_text(note)
    tools=[p for p in(R/'tools/audit').glob('*.py')if p.name.startswith(('prepare_wwf_isolated_host_phase_','wwf_isolated_host_phase_controls_','prepare_wwf_selected_contact_','wwf_selected_contact_controls_','wwf_selected_contact_interrupts_','wwf_c2_nes_cpu_controls_'))]
    files=set(tools)|{Path(__file__),O/'integration-api.json',O/'README.txt',*builds,*tests,R/'tools/audit/verify_native_relocation.py',R/'docs/qa/checkpoints/2026-10-31/wwf-c2-source-component-v1/handoff.json'}
    files|={p for p in L.iterdir()if p.is_file()}|{p for p in H.iterdir()if p.is_file()}
    for name in ['wwf-isolated-host-phase-v1','wwf-isolated-host-phase-v2','wwf-selected-contact-controls-v1','wwf-selected-contact-controls-v2','wwf-isolated-host-phase-controls-v1','wwf-isolated-host-phase-controls-v4']:
        base=R/'build'/name
        files|={p for p in base.glob('*.json')if p.is_file()}
    nes=R/'build/wwf-c2-nes-cpu-controls-v1'
    files|={p for p in nes.rglob('*')if p.is_file()and p.suffix in ['.json','.s','.cfg']}
    # Preserve actual original VM/helper/data source once; no parent images.
    old=R/'build/wwf-c2-symbol-relocation-v3'
    files|={p for p in old.iterdir()if p.is_file()and p.suffix in ['.s','.cfg','.json']}
    external={Path(p)for q in reports for p in q['bindings']}
    bindings={str(p.resolve()):sha(p)for p in sorted(files|external)}
    members={p for p in files if p.suffix not in ['.o','.dbg','.lbl','.map','.dep','.lst','.bin']}
    assert len(members)<160 and sum(p.stat().st_size for p in members)<12000000
    with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(members):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(O/'source-only.zip')as z:
        assert len(z.namelist())==len(members)
        for p in members:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    for p,h in bindings.items():assert sha(p)==h,p
    handoff=dict(source=True,isolated_CPU_lab=True,no_host_allocation=True,native_host=False,installed=False,status='SELECTED_WWF_COLD_PHASE_CONTACT_NES_CPU_PASS_NO_HOST_UNLOCK',source_build=sha(L/'build-proof.json'),bindings=bindings,members={p.relative_to(R).as_posix():sha(p)for p in sorted(members)},archive_sha256=sha(O/'source-only.zip'),archive_bytes=(O/'source-only.zip').stat().st_size,VM_bytes=7726,selected_contact_bytes=399,cold_phase_bytes=647,lab_context_bytes=16,dynamic_VM_handlers=60,total_VM_handlers=90,cold_cases=24,accepted_frame_pairs=4608,selected_contact_cases=10176,selected_interrupt_cuts=2796,actual_common_ISR_claim=False,limitations=api['remaining_semantics'])
    save(O/'handoff.json',handoff)
    for n in ['handoff.json','source-only.zip','integration-api.json','README.txt']:(D/n).write_bytes((O/n).read_bytes())
    (D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(set(tools)|{Path(__file__),R/'tools/audit/wwf_c2_nes_cpu_controls_v1.py'}))+'\n'+D.relative_to(R).as_posix()+'/\n')
    print(json.dumps(dict(passed=True,handoff=str(D/'handoff.json'),SHA256=sha(D/'handoff.json'),bindings=len(bindings),members=len(members),archive_bytes=handoff['archive_bytes'])))
if __name__=='__main__':main()
