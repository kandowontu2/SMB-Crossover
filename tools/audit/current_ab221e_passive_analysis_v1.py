"""Read saved passive journals, freeze one bounded public checkpoint; no native."""
from pathlib import Path
from collections import Counter
import hashlib,json,shutil

R=Path(__file__).resolve().parents[2];B=R/'build'
OUT=R/'docs/qa/checkpoints/2026-10-27/mega-proto-body-palette-ab221e-native-source-v1'
ROM='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def stamp(x):
    return dict(cycle=x['cpu.cycleCount'],PPU=x['ppu.frameCount'],line=x['ppu.scanline'],dot=x['ppu.cycle'],PC=x['cpu.pc'],bank=x['bank']if'bank'in x else x['currentPCbank'])

def encoded(raw):return bytes(v&0xe3 if i%4==2 else v for i,v in enumerate(raw))

def main():
    assert not OUT.exists()
    candidate=B/'mega_proto_body_palette_9ea.nes';assert sha(candidate)==ROM
    groups={};inputs=[candidate,Path(__file__)];copies=[]
    for identity,profile,journal in [('proto','current-ab221e-proto-handoff-timing-v1','handoff-diagnostic.jsonl'),('megaman','current-ab221e-mega-knuckle-owner-v1','knuckle-owner.jsonl')]:
        p=B/profile;n=p/'native';original=B/('current-ab221e-'+identity+'-hard-arsenal-v1')/'native'
        ready=read(p/'prepared-not-run.json');assert ready['ROM_sha256']==ROM
        assert all(sha(x['path'])==x['sha256']for x in ready['bindings'])
        launch=read(p/'launch.json');assert launch['exit_code']==0 and not launch['changed_inputs']and launch['settings_before']==launch['settings_after']
        assert launch['ready_sha256']==sha(p/'prepared-not-run.json')and launch['ROM_sha256']==ROM
        result=read(n/'result.json');assert result['passed']and result['ROM_sha256']==ROM and result['mode']==1 and result['variant']==int(identity=='proto')and result['late']==0
        assert len(result['cases'])==10 and not result['ownership_or_ammo_seeded']and result['updates']==2222
        assert all(x['native_cleanup']and x['spends']==1 and x['damageCalls']>=1 and x['hpWrites']>0 for x in result['cases'][1:8])
        images=sorted(n.glob('*.png'));assert len(images)==6
        equal=[]
        for file in [n/'inventory.csv',n/'result.json',*images]:
            other=original/file.name;assert file.read_bytes()==other.read_bytes()
            equal.append(dict(name=file.name,sha256=sha(file),bytes=file.stat().st_size))
            inputs.extend([file,other])
        data=[json.loads(x)for x in(n/journal).read_text().splitlines()]
        groups[identity]=dict(p=p,n=n,original=original,result=result,rows=data,comparison=equal)
        inputs +=[p/'prepared-not-run.json',p/'launch.json',n/journal]
        for file in [p/x for x in ['prepared-not-run.json','observer-config.json','run.lua','command.json','source-controls.json','launch.json']]:copies.append((file,identity/'unused'if False else Path(identity)/file.name))
        for file in [n/x for x in ['result.json','inventory.csv',journal,'capture-budget.json']]+images:copies.append((file,Path(identity)/'native'/file.name))
    rows=groups['proto']['rows'];armed=[x for x in rows if x['event']=='diagnostic-window-armed'];assert len(armed)==1 and armed[0]['trigger_item']==9
    assert len(rows)==967 and (groups['proto']['n']/'handoff-diagnostic.jsonl').stat().st_size<=2000000
    ppu=[x['ppu.frameCount']for x in rows];assert max(ppu)-min(ppu)<200 and min(ppu)==armed[0]['first_PPU']
    matches=[];dma_checks=[];enables=[]
    for sequence in sorted({x['nmi_sequence']for x in rows}):
        part=[x for x in rows if x['nmi_sequence']==sequence]
        request=[x for x in part if x['event']=='dma-request'];done=[x for x in part if x['event']=='E008-completed-DMA']
        if request:
            assert len(request)==len(done)==1;rq=request[0];end=done[0]
            source=bytes.fromhex(rq['source256']);hardware=bytes.fromhex(end['hardware256'])
            assert len(source)==len(hardware)==256 and end['writes']==256 and encoded(source)==hardware
            assert rq['ppu.spriteRamAddr']==end['ppu.spriteRamAddr']==0
            off=[x for x in part if x['event']=='PPUMASK-before-original-assert'and x['value']&24==0 and x['cpu.cycleCount']<rq['cpu.cycleCount']]
            assert off
            enable=[x for x in part if x['event']=='PPUMASK-before-original-assert'and x['value']&24];assert len(enable)==1
            e=enable[0];assert e['cpu.cycleCount']>end['cpu.cycleCount']
            line,dot=e['ppu.scanline'],e['ppu.cycle'];assert 241<=line<=260 or line==-1 and dot<=274
            margin=274-dot if line==-1 else (261-line)*341+274-dot
            enables.append(dict(sequence=sequence,enable=stamp(e),deadline_margin_PPU_dots=margin,NMI_CPU=e['nmi_CPU']))
            dma_checks.append(dict(sequence=sequence,completion=stamp(end),writes=256,literal_source_hardware=source==hardware,ignored_attribute_differences=[i for i in range(256)if source[i]!=hardware[i]]))
        entries=[x for x in part if x['event']=='nmi-entry'and x['offset1']==47 and x['item']==0]
        if entries and request:matches.append((sequence,part,entries[0]))
    assert len(matches)==1 and len(dma_checks)==len(enables)==32
    sequence,part,entry=matches[0];packet=bytes.fromhex(entry['queue1'])[:48];assert packet[-1]==0
    oldpath=B/'current-9ea-proto-arsenal-diagnostic-v2/native/handoff-diagnostic.jsonl';oldrows=[json.loads(x)for x in oldpath.read_text().splitlines()]
    oldentry=next(x for x in oldrows if x['event']=='nmi-entry'and x['nmi_sequence']==sequence)
    oldpacket=bytes.fromhex(oldentry['queue1'])[:54]
    assert oldpacket[:47]+b'\0'==packet and oldpacket[47:]==bytes.fromhex('3f11030f161000')
    parser=[x for x in part if x['event']=='actual-parser-command'];assert len(parser)==8 and parser[-1]['destination']==0
    oldparser=[x for x in oldrows if x['event']=='actual-parser-command'and x['nmi_sequence']==sequence]
    parser_cycles=parser[-1]['cpu.cycleCount']-parser[0]['cpu.cycleCount'];oldcycles=oldparser[-1]['cpu.cycleCount']-oldparser[0]['cpu.cycleCount']
    assert [x['destination']for x in parser[:-1]]==[0x2023,0x2037,0x2057,0x204a,0x3f1d,0x3f19,0x3f10]
    assert parser_cycles==1171 and oldcycles-parser_cycles==152
    chr_start=next(x for x in part if x['event']=='chr-entry');chr_end=next(x for x in part if x['event']=='chr-real-RTS-entry')
    assert chr_end['chr_CPU']==chr_end['cpu.cycleCount']-chr_start['cpu.cycleCount']==420 and chr_start['reload']==1 and chr_end['reload']==0
    dma=next(x for x in part if x['event']=='E008-completed-DMA');enable=next(x for x in part if x['event']=='PPUMASK-before-original-assert'and x['value']&24)
    critical=next(x for x in enables if x['sequence']==sequence);assert critical['deadline_margin_PPU_dots']==30 and critical['NMI_CPU']==2343
    timing=dict(actual_native=True,sequence=sequence,entry=stamp(entry),packet_bytes=47,packet_hex=packet.hex(),command_destinations=[hex(x['destination'])for x in parser[:-1]],
                parser_cycles=1171,old_parser_cycles=1323,actual_parser_saving_CPU=152,
                CHR_entry=stamp(chr_start),CHR_real_RTS_entry=stamp(chr_end),actual_CHR_cycles=420,
                completed_DMA=stamp(dma),actual_enable=stamp(enable),actual_NMI_to_enable_CPU=2343,
                original_guard_margin_PPU_dots=30,original_guard_margin_CPU=10,model14CPU_replaced_by_actual10CPU=True,
                scoped_DMA_checks=dma_checks,scoped_render_enables=enables,window_PPU=[min(ppu),max(ppu)],rows=len(rows),
                all_scope_DMA_raw_to_E3_hardware=True,old9ea_original_FALSE_preserved=True,
                scope='32 actual scoped DMAs; global2413/2062safe are original native guards/results, not a claim that this journal contains every DMA. PreviousNMI2586 retained47B/reload1 withoutDMA, followed by real2587 delivery.',
                limits='Actual30dot/10CPU margin is narrow. No universalDMC/globalbudget/allroute/nativeframe-rate guarantee. NMI elapsed saves151CPU versus old2494, while parser saves152; request->E008 is518CPU here versus old517, consistent with DMA phase difference, without an isolated wholeNMI causal claim.')
    bodyrows=groups['megaman']['rows'];entries=[x for x in bodyrows if x['event']=='body-real-renderer-entry'];assert len(entries)==9
    raw=candidate.read_bytes();record=raw[16+33*8192+0x109d:16+33*8192+0x109d+37];assert record[0]==36
    signed=lambda n:n if n<128 else n-256
    body=[]
    for e in entries:
        ret=next(x for x in bodyrows if x['event']=='body-real-renderer-return'and x['draw_serial']==e['draw_serial'])
        assert e['physicalC']==33 and e['CurrentBankC']==161 and e['pointer']==0xd09d and e['actualHeader']==36
        assert bytes.fromhex(e['actualPointerBytes'])[:37]==record==bytes.fromhex(e['expected_FIST_bytes'])
        assert not(e['InjuryTimer']or e['GuestHurtTicks']or e['MmDeathFlag'])and ret['returned_carry']==1
        assert ret['CurrentOAMOffset']==e['CurrentOAMOffset']+36 and ret['cpu.sp']==e['expected_return_SP']
        scratch=bytes.fromhex(e['R0_7']);expected=[]
        for i in range(9,0,-1):
            tile,attr,y,x=record[1+(i-1)*4:1+i*4];px=scratch[4]+256*scratch[5]+signed(x);py=scratch[6]+256*scratch[7]+signed(y)
            assert 0<=px<256 and 256<=py<512
            atr=((scratch[3]&252)|attr)if attr&32 else scratch[3]|attr
            expected.extend([py&255,tile,atr&243,px])
        start=(e['CurrentOAMOffset']+(e['RgOamRotation']if e['GuestOamRotationActive']else 0))&255
        before=bytes.fromhex(e['source256']);after=bytes.fromhex(ret['source256']);indices={(start+i)&255 for i in range(36)}
        assert bytes(after[(start+i)&255]for i in range(36))==bytes(expected)
        changes=[i for i in range(256)if before[i]!=after[i]];assert changes and set(changes)<=indices
        pub=next(x for x in bodyrows if x['event']=='full-GameLoop-final-source'and x['cpu.cycleCount']>ret['cpu.cycleCount'])
        full=bytes.fromhex(pub['source256']);want=Counter(bytes(expected[i:i+4])for i in range(0,36,4));have=Counter(full[i:i+4]for i in range(0,256,4));assert want<=have
        body.append(dict(serial=e['draw_serial'],entry=stamp(e),return_stamp=stamp(ret),physicalC=33,header=36,source_parts=9,
                         logical_offset_before=e['CurrentOAMOffset'],logical_offset_after=ret['CurrentOAMOffset'],physical_start=start,
                         changed_byte_count=len(changes),exact_original_record_emission=True,all9_tuples_retained_in_final_GameLoop_source=True))
    published=None;body_dma=[];chr_checks=[];chrbase=16+raw[4]*16384
    for e in bodyrows:
        if e['event']=='full-GameLoop-final-source':published=e
        elif e['event']=='E008-completed-DMA':
            source=bytes.fromhex(e['source256']);hardware=bytes.fromhex(e['hardware256'])
            assert e['writes']==256 and len(source)==len(hardware)==256 and encoded(source)==hardware
            assert published and source==bytes.fromhex(published['source256'])
            body_dma.append(dict(completion=stamp(e),actual_writes=256,latest_GameLoop_source_exact=True,literal=source==hardware))
        elif e['event']=='actual-endFrame-hardware-CHR':
            for i in [0,1]:
                page=e['physicalCHR'+str(i)];actual=bytes.fromhex(e['bodyCHRphysicalPage'+str(i)])
                assert actual==raw[chrbase+page*1024:chrbase+(page+1)*1024]
            chr_checks.append(dict(PPU=e['ppu.frameCount'],pages=[e['physicalCHR'+str(i)]for i in [0,1]]))
    assert len(body_dma)==13 and len(chr_checks)==16
    result=dict(passed=True,native_confirmation=True,ROM_sha256=ROM,agent_visual_review=True,
                viewed_wholeframes=['megaman/native/item-03.png','proto/native/item-03.png'],
                visual_scope='Both actual selected Knuckle wholeframes show the player body plus ring/HUD. ROOT separately viewed all6 per character. No exhaustiveart/all9visible/pixel improvement claim. Metal/Pharaoh brief-effect samples remain skipped.',
                same_candidate_byte_exact={k:v['comparison']for k,v in groups.items()},
                actual_results={k:{x:v['result'][x]for x in ['passed','wall','updates','complete256_DMAs','NMI_safe_enables','NMI_checks','IRQ31_checks','CHR_checks','minSP','mode','variant','late','screenshots']}for k,v in groups.items()},
                timing=timing,body=dict(actual_renderer_calls=body,source_record_hex=record.hex(),actual_completed_DMA=body_dma,actual_endFrame_CHR_ROM_exact=chr_checks,
                    limits='FirstendFrame1172 is prior visible carry/page63; first laterDMA1173 follows actual new publication/page117. Source body writes and completeDMA are proved; first-eight opaque visibility is not simulated or universally certified. Nine actualcalls in this repaired window vs ten old calls must not be equated as identical crossROM cadence.'),
                original_causes=dict(Proto=str(oldpath),Proto_sha256=sha(oldpath),Mega=str(B/'current-9ea-mega-knuckle-diagnostic-v1/native/knuckle-owner.jsonl'),
                    Mega_sha256=sha(B/'current-9ea-mega-knuckle-diagnostic-v1/native/knuckle-owner.jsonl'),original_FALSE_not_retagged=True),
                limits='Finite matureactor Hardonefacing10components each; notEasy/naturalreveal/RNG/empty/fullpool/exhaustion/oppositeface/audio-waveform/whole1-1/allroster/timinggeneralization. No productionadoption performed.',
                input_bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in dict.fromkeys(inputs+[oldpath])])
    # Exactly three sparse overlay leaves plus the actual named entrypoint;
    # receipts only, never ROM/DBG/source trees/runtime/rawstream payloads.
    source_names=['mm_player_prg_owner_metasprite_engine.s','mm_player_prg_owner_megaman_weapons.s','proto_normal_palette_ack_9ea_source.s','mega_proto_body_palette_9ea_entrypoint.s','mm_player_prg_owner.patch','proto_normal_palette_ack_9ea.patch']
    receipt_names=['mm_player_prg_owner_build.json','mm_player_prg_owner_controls.json','mm_player_prg_owner_pose_controls.json','mm_player_prg_owner_build_controls.json','mm_player_prg_owner_handoff.json','proto_normal_palette_ack_9ea_build.json','proto_normal_palette_ack_9ea_cpu.json','proto_normal_palette_ack_9ea_caller.json','proto_normal_palette_ack_9ea_flagoff.json','mega_proto_body_palette_9ea_build.json','mega_proto_body_palette_9ea_handoff.json']
    copies +=[(B/n,Path('source')/n)for n in source_names]+[(B/n,Path('source/receipts')/n)for n in receipt_names]
    for identity in ['megaman','proto']:
        p=B/('current-ab221e-'+identity+'-hard-arsenal-v1')
        copies +=[(p/n,Path('original-combined')/identity/n)for n in ['prepared-not-run.json','config.json','run.lua','command.json','source-controls.json']]
    assert len(copies)==59 and len({str(dst)for _,dst in copies})==59
    for src,dst in copies:
        target=OUT/dst;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);assert target.read_bytes()==src.read_bytes()
    (OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    report='''ab221e actual two-passive confirmation, preserved source/native checkpoint

Both same-candidate fullCSV/result/all6PNG files are byte-exact to their original
uninstrumented combined profiles. Mega2623wall/2222updates/2426DMA; Proto2626/
2222/2413DMA. Bothlate0/minSP204/numericHard1. Original9ea causes stay historical.

Actual Proto NMI2587 atPPU2595: queued47B/sevencommands; native parser1171CPU vs
old1323 (-152). Genuine CHR publication420CPU remains. All256DMA completes
CPU77250596 atpre-render-1:233; enableCPU77250600 at-1:244. Originalguard-1:274
therefore leaves ACTUAL30PPUdots/10CPU, replacing the source projection14CPU.
NMIentry77248257/241:36; elapsed2343CPU. Scoped32DMAs match rawsource to physical
E3 hardware, all32enables safe. Journal967rows/901314B/PPU2591..2626. Narrowmargin
is not universalDMC/globalbudget/cadence closure; actual request->E008518CPU
vs old517 explains why parser saving152 is not identical to elapsed saving151.

Actual Mega9 renderer calls now physicalC33/D09D/header36. Every successful
realreturn increments logicalOAM36, and exact original nine tuples are emitted
inside the rotated span, with all outside bytes untouched; allnine persist in
completedGameLoop source. Scoped13fullDMAs exactly carry latest publishedsource
and normalizedphysicalhardware;16endFrameCHR snapshots match actualROMpages.
FirstendFrame1172 precedes the relevantDMA; it is not relabeled as newbodyepoch.
Actual item03wholeframes forMega/Proto were agent-viewed: playerbody and ring
are present. Source/DMA does not certify allnineparts visible under8spritelimit.

No native launch/source/production/default/settings/Git mutation by this agent.
Three overlay leaves +namedentrypoint/patches, sourceCPU/buildreceipts, original
combinedmetadata, two actual passive inputs/launch/results/CSV/journals and six
PNGs each are copied byte-exact. NoROM/DBG/binary/rawstream/runtime/sourceclone.
Original sources remain at their original hashes; no FALSE is backfilled.
Metal/Pharaoh visual samples remain missing; older distinctROM coverage is not
retagged. Whole1-1 ROOT runs and adoption remain separate.
'''
    (OUT/'report.txt').write_text(report,newline='\n')
    public=sorted(OUT.rglob('*'));public=[p for p in public if p.is_file()];assert len(public)==61
    manifest=dict(passed=True,ROM_sha256=ROM,source_and_native_checkpoint=True,source_payload_exact=True,native_run_by_agent=False,
        source_tool=str(Path(__file__).relative_to(R)),source_tool_sha256=sha(__file__),
        files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p))for p in public],
        copy_origins=[dict(public=str(dst),original=str(src.resolve()),sha256=sha(src))for src,dst in copies])
    mp=OUT/'manifest.json';mp.write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
    assert all(sha(OUT/x['path'])==x['sha256']for x in manifest['files'])
    print(json.dumps(dict(passed=True,checkpoint=str(OUT),manifest_sha256=sha(mp),analysis_sha256=sha(OUT/'analysis.json'),files=62,bytes=sum(p.stat().st_size for p in OUT.rglob('*')if p.is_file()),actual_margin_CPU=10,body_calls=9)))

if __name__=='__main__':main()
