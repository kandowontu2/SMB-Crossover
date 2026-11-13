"""Measure the full native Ladder adapter before constructing any ROM candidate."""

import argparse
from hashlib import sha256
import json
import re
import zipfile
from unittest.mock import patch

import compose_karnov_equipment_1113 as Refactor
import check_karnov_bomb_1112 as B

Audit=Refactor.Audit
SOURCE=Audit.Bomb.R/'tools/reference/karnov_ladder_native_1113.s'
ALLOCATION=Audit.Bomb.R/'docs/qa/allocations/karnov-equipment-tails-1113.json'
ORIGINS=dict(LADDER_MAIN=0xaa1a,LADDER_AUX=0xaf20,LADDER_EXTRA=0xce00)
CAPACITIES=dict(LADDER_MAIN=492,LADDER_AUX=132)
PROPOSED_CAPACITIES=dict(LADDER_MAIN=492,LADDER_AUX=132,LADDER_EXTRA=512,LADDER_TAIL=44)
LAYOUT={
    'KrLadderFrame':'LADDER_EXTRA','KrLadderStep':'LADDER_MAIN','KrLadderGrow':'LADDER_MAIN',
    'KrLadderRetract':'LADDER_MAIN','KrLadderActivate':'LADDER_MAIN','KrLadderInit':'LADDER_MAIN',
    'KrLadderProbes':'LADDER_EXTRA','KrLadderTerrain':'LADDER_EXTRA','KrLadderProbe':'LADDER_EXTRA',
    'KrLadderWorld':'LADDER_EXTRA','KrLadderCell':'LADDER_AUX','KrLadderDrawCell':'LADDER_EXTRA',
    'KrLadderWriteBlank':'LADDER_TAIL','KrLadderNativeQuad':'LADDER_AUX','KrLadderCamera':'LADDER_EXTRA',
    'KrLadderQueueFree':'LADDER_EXTRA','KrLadderSceneClear':'LADDER_EXTRA',
    'KrLadderFullRedraw':'LADDER_MAIN','KrLadderAttribute':'LADDER_EXTRA',
    'KrLadderWorldSnap':'LADDER_TAIL'}


def current_bomb(raw):
    """Authenticate every existing Bomb loan against its actual owning source."""
    owner=Audit.Bomb;constants=dict(owner.SYMBOLS)
    def packet_offset(hit):
        name='KrShotPacket'+hit[1]
        constants[name]=owner.SYMBOLS['KrShotPacket']+int(hit[1])
        return name
    constants['KrHudHintCell']=owner.SYMBOLS['VRAM_Buffer1']+18
    text=re.sub(r'\bKrShotPacket\+(\d+)',packet_offset,owner.SOURCE.read_text())
    text=text.replace('VRAM_Buffer1+18','KrHudHintCell')
    code,labels=owner.assemble_segments(text,owner.ORIGINS,constants)
    for name,body in code.items():
        role='combat'if name.endswith('_TAIL')else'options'
        page,_,origin=owner.OWNED[role]
        at=owner.CHR+page*1024+owner.ORIGINS[name]-origin
        assert raw[at:at+len(body)]==body,(name,'Current Bomb source differs')
    return labels


def equipment_controls(raw):
    """Relink only existing named Bomb leases for Ladder controls/name UI."""
    owner=Audit.Bomb;current=current_bomb(raw)
    text=owner.SOURCE.read_text()
    begin=text.index('KrBombAllowed:');end=text.index('; Native Select follows',begin)
    text=text[:begin]+'''KrBombAllowed:
    cmp #4
    bcc KrBombAllow
    cmp #7
    beq KrBombAllow
    clc
    rts
KrBombAllow:
    sec
    rts

'''+text[end:]
    begin=text.index('KrBombCycle:');end=text.index('; Original AE3D',begin)
    cycle=text[begin:end].replace('cpx #5','cpx #6').replace('ldx #4','ldx #5')
    cycle=cycle.replace('.byte $00,$01,$03,$07,$ff','.byte $00,$01,$02,$03,$07,$ff')
    cycle=cycle.replace('.byte $01,$02,$08,$80','.byte $01,$02,$04,$08,$80')
    text=text[:begin]+cycle+text[end:]
    marker='.segment "SELECTION_LOAN"'
    assert text.count(marker)==1
    text=text.replace(marker,'''KrLadderHudNames:
    .byte $0b,$18,$16,$0b,$24,$24,$24,$24,$24
    .byte $15,$0a,$0d,$0d,$0e,$1b,$24,$24,$24

'''+marker)
    before='''    ldx #4
    cmp #1
    bne KrBombHudFire'''
    assert text.count(before)==1
    text=text.replace(before,'''    ldx #4
    cmp #1
    beq KrBombHudOwned
    inx
    cmp #2
    bne KrBombHudFire''')
    changes={'.byte $01,$08,$80,$00,$02':'.byte $01,$08,$80,$00,$02,$04',
        '.byte $bd,$be,$bf,$00,$bb':'.byte $bd,$be,$bf,$00,$bb,$00',
        '.byte $30,$34,$38,$00,$3c':'.byte $30,$34,$38,$00,$3c,$00',
        '.byte $00,$09,$12,$1b,$24':'.byte $00,$09,$12,$1b,$24,$2d',
        'lda KrBombHudNewName,y':'lda KrLadderHudNames-36,y'}
    for before,after in changes.items():
        assert text.count(before)==1,before
        text=text.replace(before,after)
    constants=dict(owner.SYMBOLS)
    def offset(hit):
        key='KrShotPacket'+hit[1];constants[key]=constants['KrShotPacket']+int(hit[1]);return key
    constants['KrHudHintCell']=constants['VRAM_Buffer1']+18
    text=re.sub(r'\bKrShotPacket\+(\d+)',offset,text).replace('VRAM_Buffer1+18','KrHudHintCell')
    code,labels=owner.assemble_segments(text,owner.ORIGINS,constants)
    assert all(len(body)<=owner.LOAN_END[n]-owner.ORIGINS[n]for n,body in code.items())
    assert len(code['LADDER_LOAN'])==156 and len(code['SHIELD_LOAN'])==65,{n:len(v)for n,v in code.items()}
    assert len(code['HUD_NAME_TAIL'])==27
    # The original name helper still ends exactly before the requested44B.
    assert owner.ORIGINS['HUD_NAME_TAIL']+len(code['HUD_NAME_TAIL'])==0xcdd4
    # Native HUD's zero tile entry means no icon. This leaves the new reusable
    # Ladder's stock cells blank while its name and ordinary Down+B hint work.
    bundle=B.Cpu.Flower.Host.C.Start.W.bundle(raw)
    icon=B.M.address(bundle,'KrHudIcon')
    icon_at=owner.CHR+1021*1024+icon-0xd600
    assert icon==0xdd71
    before=raw[icon_at:icon_at+10]
    assert before==(bytes.fromhex('ae7dc8e003f026bd')+current['KrBombHudTiles'].to_bytes(2,'little')),before.hex()
    after=(bytes.fromhex('ae7dc8bd')+labels['KrBombHudTiles'].to_bytes(2,'little')+
        bytes((0xf0,(B.M.address(bundle,'KrHudLease')-(icon+8))&255,0xea,0xea)))
    assert len(after)==len(before)
    return code,labels,dict(existing_lease_code_sizes={n:len(body)for n,body in code.items()},
        all_existing_named_lease_bounds_retained=True,new_selected_option=2,new_owned_mask=4,
        cycle=[0,1,2,3,7,255],name='LADDER',reusable_no_BCD_digits=True,
        level_art_separate=True,no_new_Ladder_inventory_icon=True,
        native_icon_prefix=dict(pc=icon,file_offset=icon_at,before=before.hex(),after=after.hex()),
        no_ROM_candidate=True)


def measure(raw):
    allocation=json.loads(ALLOCATION.read_text())
    assert allocation['source_commit']=='137e7f5b'and allocation['total_bytes']==624
    trial,info=Refactor.trial(raw)
    assert Refactor.inverse(trial)==raw
    for region in allocation['regions']:
        at=region['file_offset'];n=region['bytes']
        before=trial[at:at+n]
        assert before==b'\xea'*n and sha256(before).hexdigest()==region['preimage_SHA256']
    bundle=B.Cpu.Flower.Host.C.Start.W.bundle(raw)
    names=('ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_X_Position','Player_PageLoc',
        'CurrentBankC','NmiDisable','DisableScreenFlag','VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset',
        'KrSourceFrame','KrSourceWeapons','KrOptionsControls','KrOptionsTick','KrSoundCallback','Kr_ED1A',
        'KrTerrainResult')
    constants={n:B.M.address(bundle,n)for n in names}
    constants.update(current_bomb(raw))
    aliases=dict(NativeGetBlockBufferAddr='GetBlockBufferAddr',NativeAttributes='MTileAttribute',
        NativeWriteBlockMetatile='WriteBlockMetatile',NativeFarCallCommon='FarCallCommon')
    constants.update({alias:B.M.address(bundle,name)for alias,name in aliases.items()})
    constants['NativeSafecallA']=B.M.address(bundle,'SafecallA_SMC')+1
    for name,original in zip(('NativeTopLeft','NativeTopRight','NativeBotLeft','NativeBotRight'),
            ('MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight')):
        assert(B.M.location(bundle,original)-16)//8192==3
        constants[name]=B.M.address(bundle,original)+0x2000
    constants.update({f'NativeVRAM{i}':B.M.address(bundle,'VRAM_Buffer1')+i for i in range(10)})
    # These coordinates are a resource request, not a pattern/font mutation.
    constants.update(LadderLeftGlyph=0x2c,LadderRightGlyph=0x2d)
    # Explicit proposed partition. Ungranted C2 locations are assembly
    # coordinates only; measure() never overlays them or returns a ROM.
    text=re.sub(r'^\.segment.*\n','',SOURCE.read_text(),flags=re.M)
    text=re.sub(r'^(\w+):',lambda hit:(f'.segment "{LAYOUT[hit[1]]}"\n'if hit[1]in LAYOUT else'')+hit[0],text,flags=re.M)
    origins=dict(ORIGINS,LADDER_TAIL=0xcdd4)
    code,labels=Audit.Bomb.assemble_segments(text,origins,constants)
    _,_,control_report=equipment_controls(raw)
    sizes={name:len(body)for name,body in code.items()}
    total=sum(sizes.values())
    extra=json.loads((ALLOCATION.parent/'karnov-ladder-extra-1113.json').read_text())
    assert extra['additional_code_bytes']==556 and extra['original_state_repurposing']['bytes']==27
    assert extra['private_art']['bytes']==32
    for region in extra['regions']:
        at=region['file_offset'];n=region['bytes']
        assert sha256(raw[at:at+n]).hexdigest()==region['preimage_SHA256']
    return code,labels,dict(parent_SHA256=sha256(raw).hexdigest(),refactor_SHA256=sha256(trial).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),sizes=sizes,total_bytes=total,
        assembled_payload_SHA256={n:sha256(body).hexdigest()for n,body in code.items()},
        reserved_bytes=1180,aggregate_excess=max(0,total-1180),
        current_partition_fits=all(sizes[n]<=PROPOSED_CAPACITIES[n]for n in sizes),
        proposed_capacities=PROPOSED_CAPACITIES,
        proposed_partition_fits=all(sizes[n]<=PROPOSED_CAPACITIES[n]for n in sizes),
        current_control_and_HUD_lease_plan=control_report,
        resource_reservation='4c027e30',feature_qualified=False,no_ROM_candidate=True,output_files=0)


def storage_plan(raw):
    report,code=Audit.reference_proof(raw,include_code=True)
    extension=(0xce00,0xd000)
    direct=[];indexed=[];indirect=[]
    for pc,owner,op,mode,operand in code:
        if mode in('abs','abx','aby')and extension[0]<=operand<extension[1]:
            direct.append((pc,owner,op,mode,operand))
        if mode in('abx','aby')and operand<extension[0]<=operand+255:
            indexed.append((pc,owner,op,mode,operand))
        if mode in('iny','inx','ind'):indirect.append((pc,owner,op,mode,operand))
    assert not direct,direct
    expected_indexed={0xcc8b:(0xcd24,5),0xdd3f:(0xcd55,35),0xcdc0:(0xcd8c,44),
        0xcdc5:(0xcd2a,35),0xcd97:(0xcd4e,6)}
    assert {pc:operand for pc,_,_,_,operand in indexed}=={pc:p[0]for pc,p in expected_indexed.items()}
    bounds=[dict(pc=pc,base=base,max_index=maximum,max_effective_address=base+maximum)
        for pc,(base,maximum)in expected_indexed.items()]
    assert all(row['max_effective_address']<0xcdd4 for row in bounds)
    at=Audit.Bomb.CHR+1020*1024+256
    before=raw[at:at+512]
    assert before==bytes(512)
    b=B.Cpu.Flower.Host.C.Start.W.bundle(raw)
    native_at=B.M.location(b,'KrCarrierRowSetup')
    native_pc=B.M.address(b,'KrCarrierRowSetup')
    current=raw[native_at:native_at+27]
    expected=(bytes.fromhex('a605bd')+B.M.address(b,'KrCarrierDestHi').to_bytes(2,'little')+
        bytes.fromhex('8504a904e009d002a9018507e0089005a90220')+
        B.M.address(b,'KrHudMapC').to_bytes(2,'little')+b'\x60')
    assert current==expected,(current.hex(),expected.hex())
    with zipfile.ZipFile(Audit.PACKET)as z:
        combat=z.read('host/kr-combat-v7.inc').decode()
        hud=z.read('host/kr-hud-host-v9.inc').decode()
        render=z.read('host/kr-render.inc').decode()
        terrain=z.read('host/kr-terrain.inc').decode()
    assert 'cmp #6\n jcs KcNoVictim'in combat
    assert 'ldy KC_CANON\n lda KcEnemyBits,y'in combat and 'KcEnemyBits:.byte 1,2,4,8,16,32'in combat
    assert 'ldx #35\nKrHudCopy:'in hud and 'cpx #9\n bne KrHudName'in hud
    bombtext=Audit.Bomb.SOURCE.read_text()
    assert 'cpy #36'in bombtext and 'cpx #9'in bombtext and 'ldy #6'in hud
    art_begin=B.M.address(b,'KrArtImage');art_end=B.M.address(b,'KrArtEnd')
    assert(art_begin,art_end)==(0xb7ab,0xbcec)
    assert 'KrPoseLo=$d000'in render and 'lda #$d0\n sta R1'in render
    assert 'lda #$c0\n sta R1\n ldy #0\n ldx #8'in terrain
    metadata_writes=[]
    for pc,owner,op,mode,operand in code:
        if op in('STA','STX','STY','INC','DEC','ASL','LSR','ROL','ROR')and mode in('abs','abx','aby'):
            upper=operand+(255 if mode in('abx','aby')else 0)
            if operand<0xc63f and upper>=0xc624:metadata_writes.append((pc,owner,op,mode,operand))
    expected_metadata={0xdb50:0xc564,0xdb58:0xc565,0xdb65:0xc584,0xdb6d:0xc585,
        0xdb7e:0xc564,0xdb86:0xc565,0xdb8e:0xc584,0xdb96:0xc585}
    assert {pc:operand for pc,_,_,_,operand in metadata_writes}==expected_metadata
    with zipfile.ZipFile(Audit.PACKET)as z:options=z.read('host/karnov-options-portable-v7.inc').decode()
    assert 'Kr_C534: ASL A'in options and 'Kr_C541: TAY'in options
    rows=[int(v,16)for v in re.findall(r'^Kr_C5(?:8[DF]|9[13579BDF]): \.byte \$([a-f0-9]+)',options,re.M|re.I)]
    assert rows==list(range(0x2b,0x3e,2)),rows
    metadata_bounds=[dict(pc=pc,base=base,max_index=0x3d,max_effective_address=base+0x3d)
        for pc,base in expected_metadata.items()]
    assert all(row['max_effective_address']<0xc624 for row in metadata_bounds)
    tail_at=Audit.Bomb.CHR+1019*1024+(0xcdd4-0xc900)
    assert raw[tail_at:tail_at+44]==b'\xff'*44
    assert not any(0xcdd4<=operand<0xce00 for _,_,_,mode,operand in code if mode in('abs','abx','aby'))
    classifications={0xcb2d:'Native block-buffer pointer R6/R7 below8000',
        0xcb6e:'Native MmSolidTerrain pointer below8000',
        0xb488:'Readonly A3 pose image B7AB..BCEB',
        0xb48a:'KrCopyArt writes exactly D000..D540',
        0xb06f:'New-life constructor zeroes only C000..C7FF',
        0xb3e8:'Native player terrain block-buffer pointer below8000'}
    assert {pc for pc,*_ in indirect}==set(classifications)
    assert B.M.address(b,'MmSolidTerrain')+416<0x8000
    return dict(proposed_only=True,conditional_runtime=extension,additional_runtime_bytes=512,
        physical_carrier_page=1020,physical_page_offset=256,file_offset=at,
        current_carrier_preimage_SHA256=sha256(before).hexdigest(),
        current_loader_row9_pages=1,proposed_loader_row9_pages=3,
        current_combat_copy_bytes=1280,proposed_combat_copy_bytes=1792,
        loader_pc=native_pc,loader_file_offset=native_at,
        loader_current_bytes=current.hex(),single_immediate_operand_file_offset=native_at+14,
        existing_all37_reachable_instructions=report['actual_reached_instructions'],
        direct_references_into_proposed_runtime=direct,
        bounded_indexed_reads=bounds,
        indirect_contracts=[dict(pc=pc,contract=classifications[pc])for pc,*_ in indirect],
        readonly_pose_copy=(0xd000,0xd000+art_end-art_begin),
        original_Ladder_metadata=(0xc624,0xc63f),conservative_indexed_writer_candidates=metadata_writes,
        source_bounded_writer_effective_addresses=metadata_bounds,no_reached_effective_writer_into_metadata=True,
        metadata_indirect_writer='Only original new-life clear; proposed Ladder will own its former27B transport',
        proposed_existing_Bomb_tail=(0xcdd4,0xce00),tail_bytes=44,tail_file_offset=tail_at,
        tail_preimage_SHA256=sha256(raw[tail_at:tail_at+44]).hexdigest(),
        options_unchanged_range=(0xd600,0xde00),no_mutation_or_resource_grant=True)


def loader_geometry(raw):
    from verify_native_relocation import NesMPU
    b=B.Cpu.Flower.Host.C.Start.W.bundle(raw)
    pc=B.M.address(b,'KrCarrierRowSetup');at=B.M.location(b,'KrCarrierRowSetup')
    current_bank=B.M.address(b,'CurrentBankC');rows=[]
    native_bank=raw[16+29*8192:16+30*8192]
    dest=(0xc0,0xc4,0xc8,0xcc,0xd0,0xd4,0xd8,0xdc,0xc9,0xcd,0xd6,0xda)
    for row in range(12):
        results=[]
        for expanded in(False,True):
            m=bytearray(65536);m[0xa000:0xc000]=native_bank
            assert m[pc+14]==1
            if expanded:m[pc+14]=3
            m[5]=row;m[current_bank]=m[0x5116]=3
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,7,91,0x21,224;c.stPushWord(0x5aff)
            for _ in range(60):
                if c.pc==0x5b00:break
                assert m[c.pc]!=0;c.step()
            else:raise AssertionError(('Loader row bound',row,expanded,hex(c.pc)))
            assert c.sp==224 and m[4]==dest[row]
            assert m[current_bank]==m[0x5116]==(3 if row<8 else 2)
            pages=3 if expanded and row==9 else 1 if row==9 else 4
            assert m[7]==pages
            results.append((c.a,c.x,c.y,c.p,c.sp,m[4],m[current_bank],pages))
        assert results[0][:-1]==results[1][:-1],row
        rows.append(dict(row=row,bank=results[1][6],destination=dest[row]*256,
            parent_pages=results[0][-1],proposed_pages=results[1][-1]))
    ranges=[(r['bank'],r['destination'],r['destination']+r['proposed_pages']*256)for r in rows]
    for i,(bank,lo,hi)in enumerate(ranges):
        for other,begin,end in ranges[i+1:]:assert bank!=other or hi<=begin or end<=lo
        if bank==2:assert hi<=0xd000 or lo>=0xd600
    return dict(standalone_actual_helper_executions=24,all12_rows_AXYP_SP_and_map_returns_preserved=True,
        single_immediate_only=at+14,source_page1020_last_copied_offset=767,
        source_page1020_remaining_offset768_to1023_untouched=True,rows=rows,
        no_pose_or_options_overlap=True,no_ROM_candidate=True)


def font_proof(raw,donor):
    seed,_=B.cold(raw,Refactor.OLD_COOKIE)
    native=B.M.NesMPU;seen={pc:set()for pc in(0xdd3f,0xcdc0,0xcdc5,0xcd97)};glyphs=set()
    class Probe(native):
        def step(self):
            if self.memory.rawtags[2]==2 and self.pc in seen:
                seen[self.pc].add(self.x if self.pc==0xdd3f else self.y)
            return native.step(self)
    for cursor in range(256):
        for owned in(0,255):
            m=B.M.fork(seed)
            B.M.put(m,DisableScreenFlag=0,Mirror_PPUMASK=24,NmiDisable=255,
                VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,InvHudActive=0)
            m[B.M.address(m.bundle,'VRAM_Buffer1')]=0
            m.ram[2][0x8e]=cursor;m.ram[2][0x8f]=owned;m.ram[2][0xe8]=128
            for offset in(0xbd,0xbb,0xbe,0xbf):m.ram[2][offset]=0x11
            m.ram[2][0x87a:0x880]=b'\xff'*6
            with patch.object(B.M,'NesMPU',Probe):B.M.invoke(m,'HuUi')
            start=B.M.address(m.bundle,'VRAM_Buffer1');offset=0
            while m[start+offset]:
                size=m[start+offset+2];n=size&0x3f
                assert n and not size&0x40
                glyphs.update(m[start+offset+3:start+offset+3+n]);offset+=3+n
                assert offset<=83
            assert offset==35
    assert not glyphs&{0x2c,0x2d}
    bounds={0xdd3f:(0,35),0xcdc0:(36,44),0xcdc5:(0,35),0xcd97:(0,6)}
    assert all(seen[pc]and min(values)==bounds[pc][0]and max(values)==bounds[pc][1]for pc,values in seen.items())
    render=Audit.renderer_plan(raw,donor)
    original=Audit.Bomb.R/'build/karnov-palette-native-1101-v1/controls.json'
    receipt=json.loads(original.read_text())
    assert receipt['passed']and receipt['donor_sha256']==Audit.EXPECTED
    palette=receipt['hardware']['palette']
    donor_attribute=donor[16+0x1ac8+0xcf]
    assert donor_attribute==0x25 and palette[4:8]==[0x0f,0x12,0x22,0x02]
    at=Audit.Bomb.CHR+1023*1024+0x2c*16
    lifetime=font_lifetime(raw,seed)
    return dict(actual_current_HuUi_cursor_ownership_fixtures=512,all_emitted_glyphs=sorted(glyphs),
        exact_index_observations={hex(pc):[min(v),max(v)]for pc,v in seen.items()},
        original_Ladder_patterns_SHA256=render['donor_pattern_SHA256'],
        donor_class_attribute=donor_attribute,donor_palette_index=1,donor_pattern_colors={2:0x22,3:0x02},
        proposed_native_palette_index=2,proposed_native_pattern_colors={2:0x21,3:0x0f},
        exact_donor_color_parity=False,pattern_bytes_and_alpha_unchanged=True,
        private_CHR_page=1023,glyphs=[0x2c,0x2d],pattern_bytes=32,file_offset=at,
        current_preimage_SHA256=sha256(raw[at:at+32]).hexdigest(),
        native_all256_metatile_quad_glyph_references=render['all_256_native_metatile_glyph_refs'],
        no_pattern_or_palette_mutation=True,lifetime=lifetime,
        future_native_Ladder_art_qualification_pending=True)


def font_lifetime(raw,seed):
    b=seed.bundle;m=B.M.fork(seed)
    B.M.put(m,DisableScreenFlag=0,Mirror_PPUMASK=24,NmiDisable=255,
        VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,InvHudActive=0)
    m[B.M.address(b,'VRAM_Buffer1')]=0;m.ram[2][0x87a:0x880]=b'\xff'*6
    B.M.invoke(m,'X5BounceUiDispatch');B.M.invoke(m,'X5PublishChr')
    assert B.M.get(m,'InvHudActive')==0xe9 and m.chr_latches[8]==1023
    cases=[]
    for context in(dict(OperMode=0),dict(OperMode=2),dict(OperMode_Task=2),
            dict(GameEngineSubroutine=5),dict(GameEngineSubroutine=9)):
        trial=B.M.fork(m);B.M.put(trial,**context)
        B.M.invoke(trial,'X5BounceUiDispatch');B.M.invoke(trial,'X5PublishChr')
        active=B.M.get(trial,'InvHudActive')
        assert active!=0xe9 and trial.chr_latches[8]!=1023,(context,active,trial.chr_latches[8])
        cases.append(dict(context=context,active=active,physical_BG_font=trial.chr_latches[8]))
    B.M.invoke(m,'KrRetire');B.M.invoke(m,'X5PublishChr')
    assert B.M.get(m,'InvHudActive')!=0xe9 and m.chr_latches[8]!=1023
    loop=B.M.location(b,'GameLoop');ui=B.M.address(b,'X5BounceUiDispatch')
    bank=((B.M.location(b,'X5BounceUiDispatch')-16)//8192)|128
    actual_call=(bytes((0xa9,ui&255,0x8d,0x6c,1,0xa9,ui>>8,0x8d,0x6d,1,0xa9,bank,0x20,0x5a,1)))
    assert raw[loop:loop+96].count(actual_call)==1
    with zipfile.ZipFile(Audit.PACKET)as z:text=z.read('host/screen_render.s').decode()
    common=text[text.index('GameText:\n'):text.index('GameTextOffsets:\n')]
    strings=re.findall(r'"([^"\n]*)"',common)
    assert strings and not any('.'in s or'/'in s for s in strings)
    return dict(current_real_UI_and_CHR_publication=True,private_font_page1023_published=True,
        mode_context_fixtures=cases,actual_KrRetire_restores_native_font=True,
        actual_GameLoop_UI_call_prefix_bound=True,GameLoop_call_file_offset=loop+raw[loop:loop+96].index(actual_call),
        ordinary_game_text_source_strings=strings,ordinary_text_has_no_dot_or_chain=True,
        scope='Current actual UI/mapper calls in explicit contexts, source-bound unconditional Main UI call; not a native transition replay')


def world_snap(raw):
    from verify_native_relocation import NesMPU
    code,labels,_=measure(raw);base,info=Refactor.trial(raw)
    b=B.Cpu.Flower.Host.C.Start.W.bundle(raw)
    pc=info['code']['symbols']['Kr_F62B'];continuation=info['code']['symbols']['Kr_F633']
    actor=base[Refactor.Scene.ACTOR:Refactor.Scene.ACTOR+8192]
    assert actor[pc-0xa000:continuation-0xa000]==bytes.fromhex('ad63c029f009088d63c0')
    m=bytearray(65536);m[0xa000:0xc000]=actor
    m[0xcdd4:0xcdd4+len(code['LADDER_TAIL'])]=code['LADDER_TAIL']
    m[pc:continuation]=(b'\x20'+labels['KrLadderWorldSnap'].to_bytes(2,'little')).ljust(10,b'\xea')
    c=NesMPU(memory=m);camera=B.M.address(b,'ScreenLeft_X_Pos');cases=0
    # Every native fine-camera/source-X pair and both incoming carries.
    for flags in(0x20,0x21):
        for cam in range(256):
            m[camera]=cam
            for x in range(256):
                m[0xc063]=x;m[0xc062]=10
                c.pc,c.a,c.x,c.y,c.p,c.sp=pc,85,7,91,flags,224
                for _ in range(25):
                    if c.pc==continuation:break
                    c.step()
                else:raise AssertionError(('World snap bound',cam,x,hex(c.pc)))
                expected=((((x+cam)&255)&0xf0)|8)-cam&255
                assert(m[0xc063],c.a,c.x,c.y,c.p&0x4d,c.sp)==(expected,expected,7,91,flags&0x4d,224)
                assert c.p&0x82==(128 if expected&128 else 0)|(2 if not expected else 0)
                # The actual next source instruction overwrites A/N/Z from62.
                assert m[c.pc:c.pc+3]==bytes.fromhex('ad62c0');c.step()
                assert c.a==10 and c.p&0x82==0
                if cam&15==0:assert expected==(x&0xf0)|8
                cases+=1
    # Exercise all status values on representative carry/zero/page boundaries.
    for flags in range(256):
        for cam,x in((0,0),(1,255),(8,8),(15,241),(255,1)):
            m[camera]=cam;m[0xc063]=x;c.pc,c.a,c.x,c.y,c.p,c.sp=labels['KrLadderWorldSnap'],85,7,91,flags,224
            c.stPushWord(0x5aff)
            for _ in range(20):
                if c.pc==0x5b00:break
                c.step()
            else:raise AssertionError('Leaf snap bound')
            expected=((((x+cam)&255)&0xf0)|8)-cam&255
            assert(c.a,c.x,c.y,c.p&0x4d,c.sp)==(expected,7,91,flags&0x4d,224)
            cases+=1
    return dict(standalone_CPU_cases=cases,all65536_camera_source_X_pairs_both_carries=True,
        all256_status_values_boundary_cases=True,old_grid_exact_when_camera_aligned=True,
        source16_pixel_grid_and8_pixel_center_retained=True,AXY_CVID_SP_and_actual_F633_continuation=True,
        source_PC=pc,source_continuation=continuation,hook_bytes=10,new_helper_bytes=24,no_ROM_candidate=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--part',choices=('measure','storage-plan','loader-geometry','font','world-snap'),default='measure')
    args=p.parse_args();raw,donor=Audit.inputs()
    report={'storage-plan':lambda:storage_plan(raw),'loader-geometry':lambda:loader_geometry(raw),
        'font':lambda:font_proof(raw,donor),'world-snap':lambda:world_snap(raw),
        'measure':lambda:measure(raw)[2]}[args.part]()
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
