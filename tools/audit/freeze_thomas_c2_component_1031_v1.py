"""Freeze eight-byte-scope Thomas C2 cold/accepted-frame source evidence."""
from pathlib import Path
import hashlib,json,re,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/thomas-c2-eight-melee-v1';C=R/'build/thomas-c2-eight-melee-controls-v1';S=R/'build/thomas-c2-scope-controls-v1'
O=R/'docs/qa/checkpoints/2026-10-31/thomas-c2-cold-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    assert not O.exists()or not any(O.iterdir());O.mkdir(parents=True,exist_ok=True)
    controls=json.loads((C/'controls.json').read_text());scope=json.loads((S/'controls.json').read_text())
    assert controls['result']==scope['result']=='PASS' and controls['borrowed_zp_bytes']==8
    assert controls['bindings'][str(P/'source-stage.json')]==sha(P/'source-stage.json')
    files=set()
    def add(p):
        p=Path(p).resolve();assert p.is_file(),p;files.add(p)
    for root in [P,C,S,R/'build/thomas-c2-component-v4',R/'build/thomas-c2-controls-v3',R/'build/thomas-c2-eight-component-v1',R/'build/thomas-c2-eight-controls-v1']:
        for p in root.rglob('*'):
            if p.is_file():add(p)
    tools=['prepare_thomas_c2_component_1031_v1.py','prepare_thomas_c2_component_1031_v2.py','prepare_thomas_c2_component_1031_v3.py',
        'check_thomas_c2_component_1031_v1.py','check_thomas_c2_component_1031_v2.py','check_thomas_c2_component_1031_v3.py',
        'check_thomas_c2_component_1031_v4.py','check_thomas_c2_scope_1031_v1.py','prove_thomas_16_scope_negative_1031_v1.py',Path(__file__).name]
    for n in tools:add(R/'tools/audit'/n)
    parent=R/'docs/qa/checkpoints/2026-10-31/thomas-original-source-component-v1/handoff.json'
    assert sha(parent)=='278b74d2bc28f7d2b2f0379d2fb7f95e5a8e5973d106f8c85499679dae607b61';add(parent)
    # Recurse bindings only, not entire unrelated source-stage or roster graphs.
    queue=list(files);done=set()
    while queue:
        p=queue.pop()
        if p in done or p.suffix!='.json':continue
        done.add(p);j=json.loads(p.read_text(encoding='utf-8'))
        groups=[j.get(k,{})for k in ['bindings','files','source_inputs','outputs','source_files']if isinstance(j,dict)]
        for group in groups:
            if not isinstance(group,dict):continue
            for name,h in group.items():
                if not isinstance(h,str)or not re.fullmatch('[0-9a-f]{64}',h):continue
                q=Path(name)
                if not q.is_absolute()or not q.is_file():continue
                assert sha(q)==h,(str(p),name,'binding drift')
                if q not in files:add(q)
                # The original frozen parent/host handoffs are hash dependencies,
                # not an instruction to duplicate their whole source archives.
                if 'thomas-c2' in q.as_posix():queue.append(q)
    size=int(re.search(r'CODE\s+006000\s+\S+\s+([0-9A-F]+)',(P/'component.map').read_text())[1],16)
    assert size==3641
    facts=dict(status='FROZEN_ISOLATED_C2_SOURCE_NOT_HOST_ADMITTED',
      final_component=dict(path=str(P/'component.bin'),sha256=sha(P/'component.bin'),source_stage_sha256=sha(P/'source-stage.json'),
        compiled_code_and_data_bytes=size,lab_code_range='6000..<6E39',lab_output_bytes=8192,
        selected_C2_state='C000..<C800 native2KB projection',transaction_span='C800..<C818 (24B, including8savedZP and6meleeoutputbytes)',
        host_allocations='NONE. AllC2/code addresses in this packet are isolated lab layout, not a current-roster lease.'),
      interface=dict(ThomasC2ColdInit='A floor0..4, X player0/1, Y initialepoch; caller has selectedC2 ownership and idleBusy0. Clearsprivate state, executes genuine84F0/8563/8610, selects originalidlepose, publishesReadyA7LAST; restores callerAXYP/SP.',
        ThomasC2AcceptedFrame='A originalheldbyte, X1accepted/otherrejected, Yforegroundepochmod256; skipsbusy/unready/duplicate. Executes original frame reset, timers, controllerlatch, movement/input, trueC208window+C65Brectangle, animation/pose. Restores callerAXYP/SP.',
        native_controls='Right1/Left2/Down4/Up8 jump/B40punch/A80kick; source edge/stance timing untouched.',
        outputs='Originalprivate69/68/B6/D4/E5/4A6/FB..FF, latched originalposeC805; attackenabledC808/kindC809/rectangleC80A..C80D.',
        scratch='OnlyphysicalR0..7 borrowed. Original08..0F become directC2fields. Canonicalworking/pointerstate remainsselectedC2; saveC810..C817 restored before return. No NMI-disable interval.',
        private_worker_contract='Rawbodybox offsetX0/4; rawattackbox canonicaloffset0/4; selectedplayer damageX6 only. EnemyserviceX0..5 is not a host API.',
        retained_dependencies='Original coldworldtables80F8..811D and damage metadata/B243 remain named donor dependencies. Audio queues are retained; driver/audio ownership and native deathscript are not integrated.'),
      finite_controls=dict(cold_receipt=str(C/'controls.json'),cold_receipt_sha256=sha(C/'controls.json'),
        original_cold_pairs=640,accepted_actor_pairs=2336,duplicate_unaccepted_busy_inert=7008,
        primitive_receipt=str(S/'controls.json'),primitive_receipt_sha256=sha(S/'controls.json'),
        original_allflag_primitive_and_storeorder_pairs=6912,real_lab_NMI_IRQ_cases=132,
        all64flags='C/Z/I/D/V/N exhaustive with canonicalB/U30; every executingCPU is NES-specificNesMPU, decimalarithmeticdisabled while P.Dpreserved.',
        source_state_projection='Exact2KB application state exceptdeadstack; fullAXYP/SP, every originalprimitive applicationstore in originalorder. Pointer provenance tracked perbyte, not generic wholeword normalization.',
        pointer_details='Only truepair publishers A842/A915/A923 rebind linkedcode/table pointers; coldpointerhighwriters84FC/8505/850D projectC3..C8. Laterlow-only/scalarwrites retain untouchedhigh-byte provenance. Observer tracks logical00..0F; only00..07arephysicalborrowed.',
        vector_contract='CompiledlabISR preservesexactlyR0..7, increments host09, attemptsbusy reentry, executesrealNMI/IRQ vectors andRTI. Host09increment survives; all33SMC canarybytes exact.',
        actual_lab_minimumSP=scope['minimumSP'],cold_CPU_cycles=controls['cold_cycles'],
        exclusions='Not actual currenthostNMI/mapper/audio/raster/PPUdeadline/nativeemulator/terrain/Main qualification. No readiness or installation claim.'),
      predecessor=dict(frozen_original_handoff=str(parent),sha256=sha(parent),
        old16_scope='build/thomas-c2-component-v4 remainsimmutable lab-only; rejectedforhost because08..0F are live enginefields.',
        actual_negative=str(S/'old16-scope-negative.json'),negative_sha256=sha(S/'old16-scope-negative.json'),
        negative='Old16scope hides host09as0 then restoresBA after real INC09; correcthostresultBB islost. New8byte132vectors retainBB.'),
      future_terrain_base=json.loads((P/'source-stage.json').read_text())['future_terrain_base'],
      remaining_host_gaps=['ActualC2/code/CHR allocation and completecookie/selectedThomas/FmAlts40 owner predicates',
        'Realforcedblankloader and C mapping/acquire/retire through current5FFF protocol; idleBusy0 acquisition is only a lab precondition now',
        'Import current world/screen/ground anchor, nativehead/feet/support/ceiling/fall and native progression without a second integrator',
        'Normalize bakedbackground art offsets against originalB6 once; publicpose/bodybox APIs remain genuineoriginal',
        'Connect publishedattackwindow/rectangles to actualhost targets/defeat and selectednativeHP/life/powerup rules',
        'Source audio driver/state/channel/NMIownership; queues alone are not sound qualification',
        'Coordinated Thomas/WWF Startmask compaction; last7menuhelperbytes remainunclaimed'],
      retained_development_negatives=['Firstcoldwrapper checkedY after registersave instead of savedA; newv4 correctlyreloadsstackarguments.',
        'Genericwholeword pointer normalization misclassified pointerhighleft after scalar-low overwrite; instruction-provenance comparison fixesobserver only.',
        'Sixteenphysicalscratchbytes are explicitly non-host-adoptable; eightbyte successor records08..0FdirectC2 andactual host09survival.'],
      changes_outside_private_sources=False,native_runs=0,Git_or_download_changes=False)
    dump(O/'API-controls-and-next-host-step.json',facts);add(O/'API-controls-and-next-host-step.json')
    members={};archive=O/'source-and-controls.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):
            if p.suffix.lower()in ['.nes','.o','.exe']or p.name in ['component.bin','reproduce.bin','original.prg','original.chr','lab-isr.bin']:continue
            if p.is_relative_to(R):name=p.relative_to(R).as_posix()
            else:name='external-reference/'+p.drive.rstrip(':')+'/'+p.as_posix().split(':',1)[-1].lstrip('/')
            z.write(p,name);members[name]=sha(p)
    dump(O/'archive-members.json',members)
    owned=[p.relative_to(R).as_posix()for p in sorted(files)if p.is_relative_to(R)and(('thomas-c2' in p.as_posix())or p.name in tools)]
    (O/'owned-files.txt').write_text('\n'.join(owned)+'\n',encoding='utf-8')
    add(O/'archive-members.json');add(O/'owned-files.txt')
    dump(O/'handoff.json',dict(status='FROZEN_ISOLATED_EIGHT_BYTE_SCOPE_C2_SOURCE',component_sha256=sha(P/'component.bin'),source_stage_sha256=sha(P/'source-stage.json'),
        canonical_API_sha256=sha(O/'API-controls-and-next-host-step.json'),bindings={str(p):sha(p)for p in sorted(files)},
        archive=dict(path=str(archive),sha256=sha(archive),members=len(members),bytes=archive.stat().st_size),
        owned_files=str(O/'owned-files.txt'),shared_changes=False,native_runs=0))
    j=json.loads((O/'handoff.json').read_text());print(json.dumps(dict(result='PASS',handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(j['bindings']),zip_members=len(members),zip_bytes=archive.stat().st_size)))

if __name__=='__main__':main()
