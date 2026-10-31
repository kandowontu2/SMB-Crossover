"""Freeze the isolated Thomas source lab; never install, stage Git, or run Mesen."""
from pathlib import Path
import hashlib,json,re,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-31/thomas-original-source-component-v1'
P=R/'build/thomas-original-component-v5';M=R/'build/thomas-melee-component-v2';C=R/'build/thomas-original-controls-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    assert not O.exists();O.mkdir(parents=True)
    controls=json.loads((C/'controls.json').read_text(encoding='utf-8'));assert controls['result']=='PASS'
    assert controls['source_stage_sha256']==sha(M/'source-stage.json')
    files=set()
    def add(p):
        p=Path(p).resolve();assert p.is_file(),p;files.add(p)
    tools=['prepare_thomas_original_source_1031_v1.py','thomas_original_cpu_1031_v1.py',
        'check_thomas_original_source_1031_v1.py','check_thomas_original_source_1031_v2.py',
        'prepare_thomas_component_1031_v3.py','check_thomas_original_source_1031_v3.py',
        'prepare_thomas_melee_1031_v1.py','check_thomas_original_source_1031_v4.py',Path(__file__).name,
        'private_build_outputs_v1.py','verify_native_relocation.py']
    for n in tools:add(R/'tools/audit'/n)
    roots=[R/'build/thomas-original-source-v2',P,M]+[R/f'build/thomas-original-controls-v{i}'for i in range(1,5)]
    for root in roots:
        for p in root.rglob('*'):
            if p.is_file():add(p)
    # Rehash every explicitly bound dependency, including actual compiler outputs.
    # All compiler outputs remain local evidence; none enter the source ZIP.
    for p in list(files):
        if p.suffix=='.json':
            def walk(v):
                if isinstance(v,dict):
                    for k,value in v.items():
                        if isinstance(k,str)and isinstance(value,str)and re.fullmatch('[0-9a-f]{64}',value):
                            q=Path(k)
                            if q.is_absolute()and q.is_file():
                                assert sha(q)==value,(str(p),k,'binding drift');add(q)
                        walk(value)
                elif isinstance(v,list):
                    for value in v:walk(value)
            walk(json.loads(p.read_text(encoding='utf-8')))
    # Palette renderer source is a real asset-generation dependency.
    add(R/'build/full-menu-final-art-v1/export.py')
    menu=R/'build/contra-force-menu-admission-1031-v2/joint/src/full_roster_menu.s'
    start=R/'build/bt-ready-menu-1031-v2/joint/src/cf_menu_body.inc'
    add(menu);add(start)
    facts=dict(status='SOURCE_RECOVERED_ISOLATED_COMPONENT_NOT_ROSTER_ADMITTED',
      donor=dict(path='C:/NES/Kung Fu (Japan, USA) (En).nes',sha256=controls['donor_sha256'],mapper=0,prg_bytes=32768,chr_bytes=8192),
      component=dict(path=str(M/'component.bin'),sha256=sha(M/'component.bin'),source_stage_sha256=sha(M/'source-stage.json'),
        packed_sizes=dict(control_animation=1204,tables=166,health=411,body_overlap_melee=274,typed_attack_query=22,geometry_tables=56,subtotal_code_data=2133,
            art_patterns=4672,art_descriptor_metadata=1230,total_without_audio_or_host_adapters=8035,original_audio_region=1983),
        size_correction='Initial melee API conservatively estimated query24B; actual linked THOMAS_GEOM128hex minus original274B is22B. No source/code change; canonical measured total8035B.',
        lab_abi='Native donor RAM offsets retained inside isolated CPU lab; source code6000,health6500,tables6800,geometry6A00,data6C00 are lab locations, not host leases.',
        external_health_dependencies='Named original nonplayer services/data remain explicit lab imports. No absolute alias stands in for a ported host service.'),
      authentic_behavior=dict(controls='Right/Left,Downcrouch,Upjump,Bpunch,Akick; original edge/stance restrictions retained',
        movement='Original049E fractional20hex accumulation gives1/2pixel updates; no invented acceleration',
        jump='Original11-position9B9C Ytable and9B82 cadence; allair/ground attack phases execute original source',
        health='04A6 starts30hex;0 remains alive, subtractingbelow0 enters original signednegative death',
        attacks='Original C208 window, C65B rectangles and C0F3 inclusive overlap; distinct standing/crouch/air punch/kick',
        art='42 original background commands executed by original DAEA/DB3E PPUwriter; palette role[0F,27,30,0F], both original facings, max8parts, no blank8x16pairs',
        art_caveat='Only exact same-position floor2A matches in native row22 are subtracted, matching prior authenticated idle extraction. Original index0 is transparent, index3 opaqueblack retained. Source metadata has16bit pair IDs; no hardware tile/bank assignment.',
        audio='F831 reconstructed source at original address; all1983 audio bytes preserved. Genuine input event queues and ordered APU writes match. Audio relocation/host ownership remains unqualified.'),
      tests=dict(control_receipt=str(C/'controls.json'),control_sha256=sha(C/'controls.json'),
        original_reset_start_parser_frames=600,independent_original_nmi_frames=503,real_boundary_states=31,
        allflag_input_movement_animation_pairs=5120,player_health_damage_pairs=16128,geometry_pairs=672,original_attack_window_pairs=1408,
        total_differential_pairs=23328,source_frame_cpu_delta=[0,3],original_prg_source_reproduction='Exact all32768 bytes using recovered source plus explicit untouched incbin ranges',
        comparison='Actual6502 A/X/Y/P/SP/applicationRAM/storeorder/simulatedPPU+OAM/orderedAPUevents',
        qualification_limit='Untimed original NROM CPU oracle supplies ready PPUstatus. No Mesen/raster/deadline/currenthost/Main/owner/IRQ/native qualification.'),
      next_concrete_host_steps=[
        'Approve selectedThomas state/code/CHR ownership after actual current resource closure; no7Bmenu claim.',
        'Map native control state privately, retain native oneintegrator/sourcejump deltas and attack windows; join true current head/feet/support/camera and native end progression.',
        'Normalize baked background pose offset against sourceB6 once, so host jump does not move art twice.',
        'Connect original rectangles to true host damage/defeat and exact native HP/life/upgrade transitions.',
        'Source-link coldloader, sceneFresh, actor body, worldpalette, audio acquisition/retirement and genuine NMI before menu readiness.',
        'Coordinate actual current Startmask compaction with WWF; slot10Thomas bit40hex currently cleared onStart.'
      ],
      resource_note='8035B is measured source/art size, not an8KB fit/allocation. Host wrappers/state/pointer tables and audio are additional; art can remain per-pose banked CHR instead of code-cache resident.',
      current_start_constraints=dict(slot=10,Thomas_bit='FmAlts40hex',Shinobi_bit='FmAlts04hex',actual_menu_source=str(menu),actual_start_source=str(start),
        helper_current_bytes=393,helper_limit=400,remaining7='Also proposed WWF6; wholly unclaimed byThomas',current_BT_CF_source='e538d2b809b1dac9b70a0a1b23a1b33b3d361297b25fac0b556d8eae5c7721ed'),
      retained_negatives=[
        'Initialv1 compiler-location assumption failed before any compiler invocation; v2 usesactual guarded workspace tools.',
        'InitialaudioCFG treated known LDx8/BNE as possiblefallthrough into tableF881; corrected staticconstantflags, full original PRG comparison passes.',
        'Firstartpacking assumed one4KB tile-indexspace; actual1468x16pairs require4672B. Finalmetadata usesu16pairIDs, no forcedhardwaremapping.',
        'Firstmelee link cfg emitted6A/6C before6800; linker rejected it. Newv2 ascendinglayout links without overwritingearlier source.',
        'Long sequentialv1 controls died before laterstance policies; retained but not used for final stance coverage. Final independent cohorts fork a genuine600framecoldstate.',
        'Earlyairattack buttonedge was remembered before eligible phase4/5; finalcontroller-only timing at10..13 reaches bothairpunch14hex andairkick24hex, original product unchanged.',
        'Provisional melee API querysize24B is corrected to actual22B in this canonical receipt; predecessor estimates unchanged.'
      ],
      untouched='No shared/canonical source, installed ROM, menu, Start, allocation, native process or Git state changed.')
    dump(O/'component-plan-and-controls.json',facts);add(O/'component-plan-and-controls.json')
    # Keep complete local binding verification while omitting ROM/code outputs from source ZIP.
    source=[]
    for p in sorted(files):
        if p.suffix.lower()in ['.nes','.o','.exe']or p.name in ['original.prg','original.chr','component.bin','reproduce.bin']:
            continue
        source.append(p)
    archive=O/'source-and-controls.zip';members={}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in source:
            if p.is_relative_to(R):name=p.relative_to(R).as_posix()
            else:name='external-reference/'+p.drive.rstrip(':')+'/'+p.as_posix().split(':',1)[-1].lstrip('/')
            z.write(p,name);members[name]=sha(p)
    dump(O/'archive-members.json',members)
    owned=[str(p.relative_to(R)).replace('\\','/')for p in sorted(files)if p.is_relative_to(R)and('thomas-'in p.as_posix()or p.name in tools[:9])]
    (O/'owned-files.txt').write_text('\n'.join(owned)+'\n',encoding='utf-8')
    add(O/'archive-members.json');add(O/'owned-files.txt')
    bindings={str(p):sha(p)for p in sorted(files)}
    dump(O/'handoff.json',dict(status='FROZEN_ISOLATED_SOURCE_COMPONENT',facts_sha256=sha(O/'component-plan-and-controls.json'),
        source_stage_sha256=sha(M/'source-stage.json'),controls_sha256=sha(C/'controls.json'),bindings=bindings,
        archive=dict(path=str(archive),sha256=sha(archive),members=len(members),bytes=archive.stat().st_size),
        source_owned_files=str(O/'owned-files.txt'),shared_or_installed_changes=False,native_runs=0))
    print(json.dumps(dict(result='PASS',handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(bindings),zip_members=len(members),zip_bytes=archive.stat().st_size)))

if __name__=='__main__':main()
