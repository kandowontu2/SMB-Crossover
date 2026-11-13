"""Source-bound private Karnov Ladder CPU qualification; no output files."""

import argparse
import ast
from collections import Counter
from hashlib import sha256
import json
import inspect
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


def original_bomb_code():
    owner=Audit.Bomb;constants=dict(owner.SYMBOLS)
    def packet_offset(hit):
        name='KrShotPacket'+hit[1]
        constants[name]=owner.SYMBOLS['KrShotPacket']+int(hit[1])
        return name
    constants['KrHudHintCell']=owner.SYMBOLS['VRAM_Buffer1']+18
    text=re.sub(r'\bKrShotPacket\+(\d+)',packet_offset,owner.SOURCE.read_text())
    text=text.replace('VRAM_Buffer1+18','KrHudHintCell')
    return owner.assemble_segments(text,owner.ORIGINS,constants)


def current_bomb(raw):
    """Authenticate every existing Bomb loan against its actual owning source."""
    owner=Audit.Bomb;code,labels=original_bomb_code()
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
    # Current native manual-platform control bridge then tail-calls options.
    # The retained older host text alone does not describe this installed seam.
    assert raw[Refactor.Scene.ACTOR+0x1fcb:Refactor.Scene.ACTOR+0x1fdd]==bytes.fromhex('a9788d6c01a9b38d6d01a98b205a014cf8db')
    constants['KrExistingControls']=0xbfcb
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


def candidate_cold(image,cookie,**kwargs):
    """Reuse actual cold fixture with only the two expanded expectations."""
    tree=ast.parse(inspect.getsource(B.cold));changed={23064:0,1280:0}
    class Expectations(ast.NodeTransformer):
        def visit_Constant(self,node):
            if type(node.value)is int and node.value in changed:
                old=node.value;changed[old]+=1
                return ast.copy_location(ast.Constant(value={23064:24088,1280:1792}[old]),node)
            return node
    tree=Expectations().visit(tree);assert changed=={23064:1,1280:1},changed
    namespace=dict(vars(B));exec(compile(ast.fix_missing_locations(tree),B.__file__+':extended_Ladder_expectations','exec'),namespace)
    return namespace['cold'](image,cookie,**kwargs)


def candidate_cold_proof(raw):
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);assert C.inverse(image)==raw
    model,report=candidate_cold(image,info['cookie'])
    reads=model.ppu_reads;warm=B.M.invoke(model,'KrCheckCode',a=85,x=7,y=91,p=0x21)
    assert warm['P']&1 and model.ppu_reads==reads
    assert all(model.ram[2][i]==0 for i in range(0x624,0x63f))
    assert bytes(model.ram[2][0xe00:0x1000])==image[2093328:2093328+512]
    return dict(private_candidate_SHA256=C.digest(image),cookie=info['cookie'].hex(),
        exact_inverse=True,actual_extended_cold=report,warm_extra_PPU_reads=0,
        original27_byte_object_zero=True,all512_extended_runtime_bytes_loaded_and_verified=True,
        feature_lifecycle_and_native_pending=True,output_files=0)


def earned_ladder(seed):
    """Five explicit prepared mature actors; no direct source gear grant."""
    m=B.M.fork(seed);rows=[]
    for index,kind in enumerate((0,1,1,1,1)):
        B.M.put(m,ObjectOffset=5)
        for name,value in dict(Enemy_Flag=1,Enemy_State=128,Enemy_ID=46,PowerUpType=kind,
                Enemy_X_Position=B.M.get(m,'Player_X_Position'),Enemy_PageLoc=B.M.get(m,'Player_PageLoc'),
                Enemy_Y_Position=B.M.get(m,'Player_Y_Position'),Enemy_Y_HighPos=1).items():
            m[B.M.address(m.bundle,name)+5]=value
        B.M.invoke(m,'NrPrepare',a=kind,x=5,p=0x21)
        result=B.M.invoke(m,'HandlePowerUpCollision',x=5,p=0x21)
        assert B.M.get(m,'Enemy_Flag',5)==0
        rows.append(dict(pickup=index+1,kind=kind,cycle=m.ram[2][0x860],shot=m.ram[2][0x65]&3,
            selected=m.ram[2][0x8e],owned=m.ram[2][0x8f],boots=m.ram[2][0xbd],bomb=m.ram[2][0xbb],
            native_erasure=True,return_C=result['P']&1))
    assert(m.ram[2][0x8e],m.ram[2][0x8f]&7,m.ram[2][0x860])==(2,7,3),rows
    return m,rows


def another_flower(m):
    """One explicit mature native actor through the real collector, not a grant."""
    B.M.put(m,ObjectOffset=5)
    for name,value in dict(Enemy_Flag=1,Enemy_State=128,Enemy_ID=46,PowerUpType=1,
            Enemy_X_Position=B.M.get(m,'Player_X_Position'),Enemy_PageLoc=B.M.get(m,'Player_PageLoc'),
            Enemy_Y_Position=B.M.get(m,'Player_Y_Position'),Enemy_Y_HighPos=1).items():
        m[B.M.address(m.bundle,name)+5]=value
    B.M.invoke(m,'NrPrepare',a=1,x=5,p=0x21)
    B.M.invoke(m,'HandlePowerUpCollision',x=5,p=0x21)
    assert B.M.get(m,'Enemy_Flag',5)==0
    return(m.ram[2][0x860],m.ram[2][0x8e],m.ram[2][0x8f])


def public_update(m,pad,epoch):
    """Actual NMI/UI/movement calls, not an entire Main or native replay."""
    m.controller_pad=pad;B.M.consume(m)
    B.M.put(m,NmiDisable=255)
    B.M.invoke(m,'HuUi',p=0x21)
    return B.input_step(m,pad,epoch)


def lifecycle_basic(raw):
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);seed,cold=candidate_cold(image,info['cookie'])
    m,pickups=earned_ladder(seed);epoch=1;trace=[]
    def step(pad):
        nonlocal epoch
        public_update(m,pad,epoch)
        trace.append(dict(epoch=epoch,pad=pad,scene=m.ram[2][0x5e],count=m.ram[2][0x624]&15,
            tip=m.ram[2][0x627],x=B.M.get(m,'Player_X_Position'),y=B.M.get(m,'Player_Y_Position'),
            selector=m.ram[2][0x62]&31,owned=m.ram[2][0x8f],queue=B.M.get(m,'VRAM_Buffer1_Offset')))
        epoch+=1
    step(0);step(68)
    assert m.ram[2][0x5e]==1 and not m.ram[2][0x8f]&4,trace[-3:]
    for _ in range(24):
        step(0)
        if m.ram[2][0x5e]!=1:break
    assert m.ram[2][0x624]&15==8 and m.ram[2][0x5e]==0,trace[-12:]
    start=B.M.get(m,'Player_Y_Position')
    for _ in range(20):step(8)
    high=B.M.get(m,'Player_Y_Position')
    assert high<start and m.ram[2][0x62]&31 in(10,11),trace[-22:]
    for _ in range(48):
        step(4)
        if m.ram[2][0x5e]==2:break
    assert m.ram[2][0x5e]==2,trace[-50:]
    for _ in range(24):
        step(0)
        if m.ram[2][0x5e]!=2:break
    assert m.ram[2][0x5e]==0 and not m.ram[2][0x624] and not m.ram[2][0x627],trace[-12:]
    assert m.ram[2][0x8f]&7==7 and m.ram[2][0x8e]==2
    assert m.ram[2][0xbd]==m.ram[2][0xbb]==1
    return dict(private_candidate_SHA256=C.digest(image),cold=cold,synthetic_prepared_mature_pickups=pickups,
        source_player_Y_before_and_after_Up=(start,high),trace=trace,
        actual_NMI_UI_and_public_movement=True,complete_Main_or_native_claim=False,
        original_ownership_return_and_existing_stock_preserved=True,output_files=0)


def buffer_at(m,world_x,y):
    assert 32<=y<240
    base=B.M.address(m.bundle,'Block_Buffer_1'if(world_x//256)&1==0 else'Block_Buffer_2')
    return base+((y-32)//16)*16+(world_x%256)//16


def restore_matrix(raw):
    """Explicit one-cell metadata fixtures; full actual native quad/attribute path."""
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);seed,_=candidate_cold(image,info['cookie'])
    b=seed.bundle;attrs=raw[B.M.location(b,'MTileAttribute'):B.M.location(b,'MTileAttribute')+256]
    quads=[raw[B.M.location(b,n):B.M.location(b,n)+256]for n in(
        'MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight')]
    output=sha256();cases=0
    for page,camera in((0,0),(1,7),(255,127)):
        world=page*256+128
        for tile in range(256):
            m=B.M.fork(seed)
            B.M.put(m,Player_PageLoc=page,ScreenLeft_PageLoc=page,ScreenLeft_X_Pos=camera,
                VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,NmiDisable=255)
            start=B.M.address(b,'VRAM_Buffer1');m[start]=0
            state=m.ram[2];state[0x5e]=2;state[0x71f]=0;state[0x624]=1
            state[0x625]=((page<<4)|8)&255;state[0x626]=(page&0xf0)|12
            state[0x627]=184;state[0x629]=tile
            at=buffer_at(m,world,192);m[at]=0
            block1=B.M.address(b,'Block_Buffer_1');block2=B.M.address(b,'Block_Buffer_2')
            before=bytes(m[block1:block1+208]),bytes(m[block2:block2+208])
            B.input_step(m,0,1)
            assert m[at]==tile and not state[0x624]and not state[0x627]
            for origin,old in zip((block1,block2),before):
                changed=[i for i,(x,y)in enumerate(zip(old,m[origin:origin+208]))if x!=y]
                assert changed==([at-origin]if origin<=at<origin+208 and tile else[])
            assert B.M.get(m,'VRAM_Buffer1_Offset')==14
            packet=bytes(m[start:start+15]);assert packet[2]==packet[7]==2 and packet[12]==1 and packet[14]==0
            assert(packet[3],packet[4],packet[8],packet[9])==tuple(q[tile]for q in quads)
            expected_quad=0x2000+((page&1)*0x400)+24*32+16
            assert(packet[0]*256+packet[1],packet[5]*256+packet[6])==(expected_quad,expected_quad+32)
            expected_attr=0x23c0+((page&1)*0x400)+6*8+4
            assert packet[10]*256+packet[11]==expected_attr
            # Neighbors are current synthetic sky/right and ground/below.
            neighbors=[m[buffer_at(m,world+dx,192+dy)]for dx,dy in((0,0),(16,0),(0,16),(16,16))]
            expected=sum(((attrs[t]>>6)&3)<<(2*i)for i,t in enumerate(neighbors))
            assert packet[13]==expected,(page,camera,tile,packet.hex(),neighbors,expected)
            B.M.consume(m)
            assert tuple(m.vram[expected_quad:expected_quad+2])==tuple(q[tile]for q in quads[:2])
            assert tuple(m.vram[expected_quad+32:expected_quad+34])==tuple(q[tile]for q in quads[2:])
            assert m.vram[expected_attr]==expected
            output.update(packet);cases+=1
    return dict(private_candidate_SHA256=C.digest(image),synthetic_single_cell_saved_tile_fixtures=cases,
        all256_actual_native_metatile_quads=True,native_world_pages=[0,1,255],camera_fines=[0,7,127],
        both_native_name_tables_and_attribute_addresses=True,only_exact_owned_native_cell_changed=True,
        all_neighbor_palettes_preserved_and_saved_palette_restored=True,
        actual_NMI_consumes_exact14_byte_commands=True,aggregate_queue_SHA256=output.hexdigest(),
        natural_growth_claim=False,output_files=0)


def lifecycle_extended(raw):
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);seed,_=candidate_cold(image,info['cookie'])
    m,_=earned_ladder(seed);epoch=0;trace=[]
    def step(pad=0):
        nonlocal epoch
        epoch+=1;public_update(m,pad,epoch)
        trace.append((epoch,pad,m.ram[2][0x5e],m.ram[2][0x624]&15,m.ram[2][0x627],
            B.M.get(m,'Player_X_Position'),B.M.get(m,'Player_Y_Position')))
    step();step(68)
    for _ in range(24):
        step()
        if m.ram[2][0x5e]!=1:break
    assert m.ram[2][0x624]&15==8 and m.ram[2][0x5e]==0,trace
    first=bytes(m.ram[2][0x625:0x627]);original=[m[buffer_at(m,128,192-16*i)]for i in range(8)]
    assert original==[0]*8
    # The unchanged ten-step cycle reaches Ladder again through real prepared
    # flower collectors. The live first object remains deployed.
    flowers=[another_flower(m)for _ in range(10)]
    assert m.ram[2][0x8e]==2 and m.ram[2][0x8f]&4,flowers
    for _ in range(32):step(1)
    step();step(68)
    assert m.ram[2][0x5e]==11,trace[-5:]
    phases=[]
    for _ in range(32):
        step();now=(m.ram[2][0x5e],m.ram[2][0x624]&15)
        if not phases or phases[-1]!=now:phases.append(now)
        if m.ram[2][0x5e]==0:break
    assert [n for scene,n in phases if scene==11]in(list(range(7,0,-1)),list(range(8,0,-1)))and(1,0)in phases,phases
    assert m.ram[2][0x624]&15==8 and m.ram[2][0x627]and not m.ram[2][0x8f]&4,phases
    second=bytes(m.ram[2][0x625:0x627]);assert first!=second,(first.hex(),second.hex(),trace[-35:])
    assert all(m[buffer_at(m,128,192-16*i)]==0 for i in range(8))
    # Same-life area constructor must retire ownership without any stale
    # metatile restoration. Deliberately different native scene cells witness
    # that cleanup does not use old saved world coordinates in a new scene.
    for base in(B.M.address(m.bundle,'Block_Buffer_1'),B.M.address(m.bundle,'Block_Buffer_2')):
        for i in range(208):m[base+i]=(i*13+7)&255
    before=tuple(bytes(m[base:base+208])for base in(
        B.M.address(m.bundle,'Block_Buffer_1'),B.M.address(m.bundle,'Block_Buffer_2')))
    stocks=(m.ram[2][0xbd],m.ram[2][0xbb]);cycle=m.ram[2][0x860]
    B.M.put(m,AreaAddrsLOffset=B.M.get(m,'AreaAddrsLOffset')^1,
        DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,FamilyMainCommit=1)
    B.M.invoke(m,'InitScreen',p=0x21)
    assert m.ram[2][0x8f]&4 and not m.ram[2][0x624]and not m.ram[2][0x627],(
        bytes(m.ram[2][0x624:0x629]).hex(),m.ram[2][0x8f])
    after=tuple(bytes(m[base:base+208])for base in(
        B.M.address(m.bundle,'Block_Buffer_1'),B.M.address(m.bundle,'Block_Buffer_2')))
    assert before==after and stocks==(m.ram[2][0xbd],m.ram[2][0xbb])and cycle==m.ram[2][0x860]
    # Actual fresh-life discriminator is NumberofLives, retained by the source
    # constructor in KrStateLastLife. A changed native life executes its clear.
    B.M.put(m,NumberofLives=B.M.get(m,'NumberofLives')-1)
    B.M.invoke(m,'InitScreen',p=0x21)
    assert not any(m.ram[2][0x624:0x63f])
    assert not m.ram[2][0x8f]and m.ram[2][0x8e]==255 and not m.ram[2][0xbd]and not m.ram[2][0xbb]
    return dict(private_candidate_SHA256=C.digest(image),synthetic_prepared_collectors=15,
        actual_source_rebuild_0B_phases=phases,first_anchor=first.hex(),rebuilt_anchor=second.hex(),
        original_rebuild_restores_then_grows=True,same_life_actual_InitScreen_keeps_stock_and_cycle=True,
        changed_life_actual_InitScreen_clears_original27_and_all_gear=True,
        no_stale_scene_metatile_writes=True,actual_public_updates=epoch,native_replay=False,output_files=0)


def main_lifecycle(raw):
    """Prepared earned Ladder in actual authored 1-1 Main/NMI, not Mesen."""
    import compose_karnov_ladder_native_1113 as C
    import check_karnov_natural_bomb_1113 as Natural
    image,info=C.proposal(raw)
    opening,base=Natural.C.cold(dict(Natural.W.Symbols.bundle(),raw=image),
        dict(name='KARNOV',slot=7,cycle=1,raw=34))
    m,pickups=earned_ladder(base);epoch=0;trace=[];redraws=[];maximum=0
    offset=B.M.address(m.bundle,'VRAM_Buffer1_Offset');labels=info['symbols']
    static=(bytes(m.ram[3]),bytes(m.ram[2][0x900:0x1000]),bytes(m.ram[2][0x1600:0x1e00]))
    def step(pad=0):
        nonlocal epoch,maximum
        pending=None
        def observe(memory,c):
            nonlocal pending,maximum
            maximum=max(maximum,m[offset]);assert m[offset]<=83,('Actual Main VRAM overflow',epoch,c.pc,m[offset])
            if c.pc==labels['KrLadderFullRedraw']and m.rawtags[1]==3:
                pending=(m[0x100+c.sp+1]+256*m[0x100+c.sp+2]+1,c.sp+2)
            if pending==(c.pc,c.sp):
                redraws.append((epoch,m[offset]));pending=None
        m.controller_pad=pad;Natural.Frames.frame(m,observe=observe);epoch+=1
        assert static==(bytes(m.ram[3]),bytes(m.ram[2][0x900:0x1000]),bytes(m.ram[2][0x1600:0x1e00]))
        trace.append((epoch,pad,m.ram[2][0x5e],m.ram[2][0x624]&15,m.ram[2][0x627],
            B.M.get(m,'Player_X_Position'),B.M.get(m,'Player_Y_Position'),m[offset]))
        assert B.M.get(m,'NumberofLives')==2,trace[-10:]
    for _ in range(120):
        step()
        if B.M.get(m,'Player_State')==0 and m.ram[2][0x62]&31<7:break
    else:raise AssertionError(('Authored grounded Main readiness',trace[-8:]))
    step(68)
    assert m.ram[2][0x5e]==1,trace[-5:]
    for _ in range(30):
        step()
        if m.ram[2][0x5e]!=1:break
    assert m.ram[2][0x624]&15==8 and m.ram[2][0x5e]==0,trace
    # Explicit native camera fixture crosses the redraw epoch without moving
    # the source object or injecting a scene, actor or equipment state.
    B.M.put(m,ScreenLeft_X_Pos=16,ScreenRight_X_Pos=15,ScreenRight_PageLoc=1)
    step()
    assert redraws and redraws[-1][1]==58,(redraws,trace[-5:])
    start=B.M.get(m,'Player_Y_Position')
    for _ in range(24):step(8)
    high=B.M.get(m,'Player_Y_Position');assert high<start,trace[-26:]
    for _ in range(64):
        step(4)
        if m.ram[2][0x5e]==2:break
    assert m.ram[2][0x5e]==2,trace[-65:]
    for _ in range(30):
        step()
        if m.ram[2][0x5e]!=2:break
    assert m.ram[2][0x5e]==0 and not m.ram[2][0x624]and not m.ram[2][0x627],trace[-32:]
    assert m.ram[2][0x8f]&4 and m.ram[2][0xbb]==m.ram[2][0xbd]==1
    return dict(private_candidate_SHA256=C.digest(image),actual_menu_authored_opening=opening,
        prepared_earned_pickups=pickups,actual_Main_NMI_updates=epoch,
        source_native_Y_Up=(start,high),explicit_camera_crossing=True,full_redraws=redraws,
        complete_Main_maximum_VRAM1_offset=maximum,VRAM1_84B_including_terminator=True,
        source_code_all_banks_immutable=True,actual_Main_full_grow_climb_retract=True,
        native_emulator_or_whole_stage_claim=False,trace=trace,output_files=0)


def regressions(raw):
    import compose_karnov_ladder_native_1113 as C
    import check_karnov_equipment_1113 as E
    import check_karnov_scene_motor_1113 as Scene
    image,info=C.proposal(raw)
    parent,_=B.cold(raw,Refactor.OLD_COOKIE);candidate,_=candidate_cold(image,info['cookie'])
    # Only authenticated changed executable bytes and complete identities are
    # omitted. All original mutable source/native data remains compared.
    def observable(m,live_sp=224):
        state=bytearray(m.ram[2]);state[0x900:0x1000]=bytes(0x700)
        state[0x1600:0x1e00]=bytes(0x800);state[0x1fe0:0x1ff0]=bytes(16)
        return(bytes(m[:256]),bytes(m[0x200:0x800]),bytes(m[0x101+live_sp:0x200]),
            bytes(m[0x4000:0x8000]),bytes(m.ram[0]),bytes(m.ram[1]),bytes(state),
            tuple(m.rawtags),bytes(m[0x15a:0x17b]),m.vram,m.chr_latches)
    with patch.object(E,'observable',observable):
        movements=E.movements(parent,candidate)
        main=E.menu_main(raw,image)
    return dict(private_candidate_SHA256=C.digest(image),existing_movement_pairs=movements,
        actual_menu_Main_pair=main,foreign=Scene.foreign(parent,candidate),
        all37_entry_ingress=E.entries(parent,candidate),output_files=0)


def auth_guards(raw):
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);seed,_=candidate_cold(image,info['cookie'])
    headers=0
    for bank in(2,3):
        for index in range(16):
            m=B.M.fork(seed);m.ram[bank][0x1fe0+index]^=1;reads=m.ppu_reads
            result=B.M.invoke(m,'KrCheckCode',a=85,x=7,y=91,p=0x21)
            assert(result['A'],result['X'],result['Y'],result['P']&1)==(85,7,91,0)
            assert reads==m.ppu_reads;headers+=1
    old_headers=[]
    for cookie in(Refactor.OLD_COOKIE,C.TRIAL_COOKIE):
        m=B.M.fork(seed)
        for bank in(2,3):m.ram[bank][0x1fe0:0x1ff0]=cookie
        result=B.M.invoke(m,'KrCheckCode',p=0x21);assert not result['P']&1
        old_headers.append(cookie.hex())
    faults=[]
    for bank,offset in((3,0xa1a),(3,0xf20),(2,0xdd4),(2,0xe00),(2,0xfff)):
        role='actor'if bank==3 else'combat'
        pc=(0xa000 if bank==3 else 0xc000)+offset
        expected=image[C.role_at(role,pc)]
        faults.append(candidate_cold(image,info['cookie'],readback=(bank,offset,expected)))
    rejected=[]
    for name,at in(('extended_code',2093328+511),('art',2096848),('loader',244491),
            ('foreign_byte',16+120*8192+100)):
        mutant=bytearray(image);mutant[at]^=1
        try:C.inverse(bytes(mutant))
        except AssertionError:rejected.append(name)
        else:raise AssertionError(('Unauthenticated inverse accepted',name))
    try:C.proposal(image)
    except AssertionError:pass
    else:raise AssertionError('Strict AA proposal admitted a successor')
    return dict(private_candidate_SHA256=C.digest(image),all_complete_header_byte_rejections=headers,
        old_parent_and_relink_headers_reject=old_headers,actual_extended_loader_readback_faults=faults,
        exact_inverse_rejects_changed_regions=rejected,strict_parent_only=True,
        no_header_publication_on_failed_readback=True,output_files=0)


def vectors(raw):
    """Reached new worker/changed-control cuts with real IRQ and lag-NMI."""
    import compose_karnov_ladder_native_1113 as C
    import check_karnov_natural_bomb_1113 as Natural
    image,info=C.proposal(raw);native=B.M.NesMPU;points=set();counts=Counter();minimum=255
    code,_,_=measure(raw);controls,_,_=equipment_controls(raw)
    spans=[(3,ORIGINS.get(n,0xcdd4),ORIGINS.get(n,0xcdd4)+len(body))for n,body in code.items()if n in('LADDER_MAIN','LADDER_AUX')]
    spans += [(2,ORIGINS.get(n,0xcdd4),ORIGINS.get(n,0xcdd4)+len(body))for n,body in code.items()if n in('LADDER_EXTRA','LADDER_TAIL')]
    spans += [(2,Audit.Bomb.ORIGINS[n],Audit.Bomb.ORIGINS[n]+len(body))for n,body in controls.items()]
    class Probe(native):
        def step(self):
            nonlocal minimum
            if self.pc>=0x8000:
                tag=self.memory.rawtags[(self.pc-0x8000)//8192]
                if any(tag==bank and lo<=self.pc<hi for bank,lo,hi in spans):
                    point=(tag,self.pc,self.sp,self.p&4)
                    if point not in points:
                        points.add(point)
                        for kind in('IRQ','lagNMI'):
                            if kind=='IRQ'and self.p&4:continue
                            m=B.M.fork(self.memory);c=native(memory=m,pc=self.pc)
                            for field in('a','x','y','p','sp'):setattr(c,field,getattr(self,field))
                            try:depth=B.Cpu.inject(c,native,kind)
                            except Exception as error:
                                raise AssertionError(dict(kind=kind,tag=tag,pc=hex(self.pc),sp=self.sp,
                                    completed=dict(counts),cause=repr(error)[:500]))from None
                            minimum=min(minimum,depth);counts[kind]+=1
            return native.step(self)
    # Cold is outside the active-worker matrix; code copy fault/identity checks
    # are separate. Each executed service uses the actual complete candidate.
    with patch.object(B.M,'NesMPU',Probe),patch.object(Natural.N,'NesMPU',Probe):
        basic=lifecycle_basic(raw);extended=lifecycle_extended(raw);main=main_lifecycle(raw)
    assert counts['IRQ']and counts['lagNMI']and minimum>=128
    return dict(private_candidate_SHA256=C.digest(image),new_or_relinked_worker_ranges=spans,
        reached_instruction_SP_points=len(points),real_vector_cuts=dict(counts),minimum_SP=minimum,
        includes_grow_restore_rebuild_probe_quad_attribute_and_actual_Main=True,
        exact_CPU_native_RAM_live_stack_and_mapping_restore=True,cold_cut_scope=False,
        basic_public_updates=len(basic['trace']),rebuild_public_updates=extended['actual_public_updates'],
        actual_Main_updates=main['actual_Main_NMI_updates'],output_files=0)


def main_pressure(raw):
    """Actual same-Main redraw/head/coin producers in a declared terrain fixture."""
    import compose_karnov_ladder_native_1113 as C
    import check_karnov_natural_bomb_1113 as Natural
    image,info=C.proposal(raw)
    _,base=Natural.C.cold(dict(Natural.W.Symbols.bundle(),raw=image),
        dict(name='KARNOV',slot=7,cycle=1,raw=34))
    m,_=earned_ladder(base);epoch=0
    def frame(pad):
        nonlocal epoch
        m.controller_pad=pad;Natural.Frames.frame(m);epoch+=1
    for _ in range(120):
        frame(0)
        if B.M.get(m,'Player_State')==0 and m.ram[2][0x62]&31<7:break
    else:raise AssertionError('Pressure fixture grounded readiness')
    frame(68)
    for _ in range(30):
        frame(0)
        if m.ram[2][0x5e]==0:break
    assert m.ram[2][0x624]&15==8
    for _ in range(36):frame(1)
    for _ in range(5):frame(0)
    # The only authored-scene mutation is a native coin question block with a
    # loose coin immediately above, under the player's ordinary fresh jump.
    # Motor, velocity, source actor/anchor/inventory are controller-derived.
    world=B.M.get(m,'Player_X_Position')+256*B.M.get(m,'Player_PageLoc')+8
    target=world&~15;cell=buffer_at(m,target,144);top=buffer_at(m,target,128)
    m[cell]=0xc0;m[top]=0xc2
    head=B.M.address(m.bundle,'PlayerHeadCollision')
    headtag=((B.M.location(m.bundle,'PlayerHeadCollision')-16)//8192)|128
    before=None;found=False;approach=[]
    for _ in range(30):
        before=B.M.fork(m)
        def observe(memory,c):
            nonlocal found
            if c.pc==head and m.rawtags[(c.pc-0x8000)//8192]==headtag:found=True
        m.controller_pad=128;Natural.Frames.frame(m,observe=observe)
        approach.append((B.M.get(m,'Player_X_Position'),B.M.get(m,'Player_Y_Position'),m[cell],m[top]))
        if found:break
    assert found,('Pressure actual fresh jump did not reach native head',target,approach)
    # Replay exactly the demonstrated pre-head boundary with a coarse native
    # camera crossing. Its stale Ladder camera cache schedules the redraw in
    # HuMovement, then the real BG/head and later native producers continue.
    m=before;B.M.put(m,ScreenLeft_X_Pos=16,ScreenRight_X_Pos=15,ScreenRight_PageLoc=1)
    # One additional explicit mature Star overlaps the ordinary native player
    # box in the later enemy loop. NrPrepare marks it; only Main can collect it.
    B.M.put(m,ObjectOffset=5)
    for name,value in dict(Enemy_Flag=1,Enemy_State=128,Enemy_ID=46,PowerUpType=2,
            Enemy_X_Position=B.M.get(m,'Player_X_Position'),Enemy_PageLoc=B.M.get(m,'Player_PageLoc'),
            Enemy_Y_Position=B.M.get(m,'Player_Y_Position'),Enemy_Y_HighPos=1).items():
        m[B.M.address(m.bundle,name)+5]=value
    B.M.invoke(m,'NrPrepare',a=2,x=5,p=0x21)
    offset=B.M.address(m.bundle,'VRAM_Buffer1_Offset');queue=B.M.address(m.bundle,'VRAM_Buffer1')
    targets={}
    for name in('PlayerHeadCollision','DestroyBlockMetatile','RemoveCoin_Axe','GiveOneCoin',
            'HudUpdateNumberLocal','X5NativeStatusReserve','BlockObjMT_Updater','ColorRotation',
            'RunGameTimer','GetPlayerColors','HandlePowerUpCollision'):
        targets[(((B.M.location(m.bundle,name)-16)//8192)|128,B.M.address(m.bundle,name))]=name
    events=[];pending=None;maximum=0
    def observe(memory,c):
        nonlocal maximum,pending
        maximum=max(maximum,m[offset]);assert m[offset]<=83,('Contended Main VRAM overflow',c.pc,m[offset],events)
        if c.pc<0x8000:return
        tag=m.rawtags[(c.pc-0x8000)//8192]
        name=targets.get((tag,c.pc))
        if tag==3 and c.pc==info['symbols']['KrLadderFullRedraw']:
            name='LadderFullRedraw'
            pending=(m[0x100+c.sp+1]+256*m[0x100+c.sp+2]+1,c.sp+2)
        if pending==(c.pc,c.sp):events.append(('LadderFullRedrawReturn',m[offset]));pending=None
        if name:events.append((name,m[offset]))
    m.controller_pad=128;Natural.Frames.frame(m,observe=observe)
    assert('LadderFullRedrawReturn',58)in events and any(n=='PlayerHeadCollision'for n,_ in events),events
    assert not m[top]and m[cell]==0x23,(m[cell],m[top],events)
    assert 82<=maximum<=83,(maximum,events)
    assert m[queue+maximum]==0
    assert not B.M.get(m,'Enemy_Flag',5)and B.M.get(m,'StarInvincibleTimer')!=0,events
    assert any(n=='HandlePowerUpCollision'for n,_ in events),events
    # Guarded existing color and numeric producers defer at the full queue;
    # pending native numeric fields are flushed on a later genuinely free UI.
    before_queue=bytes(m[queue:queue+84]);before_offset=m[offset]
    B.M.invoke(m,'GetPlayerColors',p=0x21)
    # A4 is the real game-timer request, which cannot reuse the existing
    # coin/score tail. A repeated coin pair legitimately coalesces in place.
    B.M.invoke(m,'HudUpdateNumberLocal',a=0xa4,p=0x21)
    assert m[offset]==before_offset and bytes(m[queue:queue+84])==before_queue
    assert B.M.get(m,'NativeStatusPending')!=0,dict(offset=m[offset],mode=B.M.get(m,'OperMode'),
        selected=B.M.get(m,'SelectedCharacter'),pending_address=B.M.address(m.bundle,'NativeStatusPending'),
        pending_writes=[(at,value)for at,value in m.writes if at==B.M.address(m.bundle,'NativeStatusPending')][-12:])
    controls=[]
    for deferred in range(12):
        controls.append((B.M.get(m,'VRAM_Buffer_AddrCtrl'),m[offset],B.M.get(m,'NativeStatusPending')))
        m.controller_pad=0;Natural.Frames.frame(m,observe=observe)
        if not B.M.get(m,'NativeStatusPending'):break
    else:raise AssertionError(('Pending numeric field did not flush',controls))
    assert m[offset]<=83 and m.vram[0x230c]==0x2c
    return dict(private_candidate_SHA256=C.digest(image),synthetic_native_terrain_cells={
        'coin_question':[target,144],'loose_coin':[target,128]},controller_derived_source_motor=True,
        prepared_earned_Ladder=True,actual_same_Main_events=events,maximum_VRAM1_offset=maximum,
        terminator_within84B=True,head_and_top_coin_native_erased=True,
        same_Main_prepared_Star_collected=True,numeric_updates_defer_then_flush=True,
        native_buffer_selection_and_pending_flush=controls,
        ordinary_BB_replacement_and_color_deferral=True,
        native_emulator_claim=False,output_files=0)


def direct(m,pc,*,a=85,x=7,y=91,p=0x61):
    """Real source leaf with declared RAM3/RAM2 mappings and caller stack."""
    m.raw_page(1,3);m.raw_page(2,2);B.M.put(m,CurrentBank=3,CurrentBankC=2)
    c=B.M.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5aff)
    for _ in range(10000):
        if c.pc==0x5b00:break
        assert m[c.pc],('Leaf BRK',pc,c.pc);c.step()
    else:raise AssertionError(('Leaf bound',pc,c.pc))
    assert c.sp==224
    return c


def finite(raw):
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);seed,_=candidate_cold(image,info['cookie']);labels=info['symbols']
    m=B.M.fork(seed);state=m.ram[2];state[0x624]=8;state[0x625]=8;state[0x626]=12;state[0x627]=72
    sky=buffer_at(m,128,112);m[sky]=0x61
    scratch=bytes((23,47,71,95,119,143,167,191));cases=0;hits=Counter()
    def query(x,y,p):
        nonlocal cases
        m[3:11]=scratch;c=direct(m,labels['KrLadderTerrain'],x=x,y=y,p=p)
        native=(x+B.M.get(m,'ScreenLeft_X_Pos'))//16
        expected=(1 if (y&0xf0)==112 else 9)if native==8 and 80<=y<208 else 0
        if y>=208:expected=0
        assert(c.a,c.x,c.y,c.p&0x4d)==(expected,x,y,p&0x4d),(x,y,p,c.a,c.p,expected)
        assert c.p&0x82==((128 if expected&128 else 0)|(2 if not expected else 0))
        assert bytes(m[3:11])==scratch and m.rawtags[1:3]==[3,2]
        hits[expected]+=1;cases+=1
    for cam in(0,7,127):
        B.M.put(m,ScreenLeft_X_Pos=cam,ScreenLeft_PageLoc=0)
        for x in range(256):
            for y in(31,32,79,80,111,112,127,128,191,192,207,208,239,255):query(x,y,0x61)
        for y in range(256):query((128-cam)&255,y,0x20)
    B.M.put(m,ScreenLeft_X_Pos=7,ScreenLeft_PageLoc=0)
    for p in range(256):
        for x,y in((120,80),(121,80),(136,80),(121,79),(121,112),(121,207),(121,208)):query(x,y,p)
    # Current native metatile attributes decide growth admission. This is a
    # synthetic first-cell fixture, not a new terrain policy or natural use.
    attrs=raw[B.M.location(seed.bundle,'MTileAttribute'):B.M.location(seed.bundle,'MTileAttribute')+256]
    growth=Counter()
    for tile in range(256):
        m=B.M.fork(seed);state=m.ram[2]
        state[0x5e]=1;state[0x624]=0;state[0x625]=8;state[0x626]=12;state[0x627]=200;state[0x71f]=0
        cell=buffer_at(m,128,192);m[cell]=tile
        B.M.put(m,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,NmiDisable=255)
        m[B.M.address(m.bundle,'VRAM_Buffer1')]=0
        direct(m,labels['KrLadderFrame'])
        admitted=not attrs[tile]&3
        assert(state[0x624]&15,m[cell],B.M.get(m,'VRAM_Buffer1_Offset'))==(
            (1,0,14)if admitted else(0,tile,0)),(tile,attrs[tile])
        assert state[0x629]==tile
        growth['admitted'if admitted else'solid_or_native_climb_blocked']+=1
    busy=0
    for offset in range(1,84):
        m=B.M.fork(seed);s=m.ram[2];s[0x5e]=1;s[0x625]=8;s[0x626]=12;s[0x627]=200
        B.M.put(m,VRAM_Buffer1_Offset=offset,NmiDisable=255)
        queue=B.M.address(m.bundle,'VRAM_Buffer1');m[queue:queue+84]=bytes((i*7+3)&255 for i in range(84))
        before=bytes(s[0x624:0x63f]),bytes(m[queue:queue+84])
        direct(m,labels['KrLadderFrame'])
        assert before==(bytes(s[0x624:0x63f]),bytes(m[queue:queue+84]))
        assert m[B.M.address(m.bundle,'VRAM_Buffer1_Offset')]==offset;busy+=1
    return dict(private_candidate_SHA256=C.digest(image),actual_source_callback_cases=cases,
        callback_result_counts=dict(hits),all256_X_and_Y_and_status_boundaries=True,
        callback_exact_XY_CVID_NZ_R0_R7_stack_maps=True,all256_native_growth_tiles=dict(growth),
        all83_nonempty_queue_offsets_defer_without_object_or_queue_changes=busy,
        synthetic_directed_leaf_fixtures=True,output_files=0)


def cold_vectors(raw):
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);b=B.Cpu.Flower.Host.C.Start.W.bundle(image)
    lo=B.M.address(b,'KrLoad');hi=B.M.address(b,'KrLoadReturn')+1
    native=B.M.NesMPU;points=set();counts=Counter();minimum=255;helper_rows=set();stx_cuts=0
    # The actual loader uses STX for its split shadow/hardware map write.
    # Keep the existing exact ISR+one-instruction continuation oracle, changing
    # only its authenticated opcode/register recognition from STA/A to STX/X.
    text=inspect.getsource(B.Cpu.inject)
    assert text.count('8da17d8d1651')==text.count('cpu.a == shadow')==1
    namespace=dict(vars(B.Cpu));exec(compile(text.replace('8da17d8d1651','8ea17d8e1651').replace(
        'cpu.a == shadow','cpu.x == shadow'),'<KrLoad exact STX split-map continuation>', 'exec'),namespace)
    stx_inject=namespace['inject']
    class Probe(native):
        def step(self):
            nonlocal minimum,stx_cuts
            if self.pc>=0x8000 and self.memory.rawtags[(self.pc-0x8000)//8192]==157 and(
                    lo<=self.pc<hi or 0xbaed<=self.pc<0xbb08):
                row=self.memory[5]if 0xbaed<=self.pc<0xbb08 else -1
                if row!=-1:helper_rows.add(row)
                point=(self.pc,self.sp,self.p&4,row)
                if point not in points:
                    points.add(point)
                    for kind in('IRQ','lagNMI'):
                        if kind=='IRQ'and self.p&4:continue
                        m=B.M.fork(self.memory);c=native(memory=m,pc=self.pc)
                        for key in('a','x','y','p','sp'):setattr(c,key,getattr(self,key))
                        split=bytes(m[c.pc-3:c.pc+3])==bytes.fromhex('8ea17d8e1651')
                        if split and kind=='lagNMI':stx_cuts+=1
                        try:minimum=min(minimum,(stx_inject if split else B.Cpu.inject)(c,native,kind))
                        except Exception as error:
                            raise AssertionError((kind,hex(self.pc),self.sp,row,repr(error)[:300]))from None
                        counts[kind]+=1
            return native.step(self)
    with patch.object(B.M,'NesMPU',Probe):_,cold=candidate_cold(image,info['cookie'])
    assert counts['lagNMI']and 9 in helper_rows and minimum>=128
    return dict(private_candidate_SHA256=C.digest(image),actual_complete_cold=cold,
        reached_load_copy_verify_publish_restore_instruction_SP_points=len(points),
        helper_rows=sorted(helper_rows),row9_three_page_helper_executed=True,
        real_interrupt_cuts=dict(counts),minimum_SP=minimum,
        exact_STX_shadow_hardware_one_instruction_continuation_cuts=stx_cuts,
        IRQ_disabled_cuts_skipped=True,exact_CPU_RAM_live_stack_and_maps_preserved=True,output_files=0)


def candidate_font(raw):
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);seed,_=candidate_cold(image,info['cookie']);glyphs=set();ladder=None;cases=0
    name=bytes((0x15,0x0a,0x0d,0x0d,0x0e,0x1b,0x24,0x24,0x24))
    for cursor in range(256):
        for owned in(0,255):
            m=B.M.fork(seed)
            B.M.put(m,DisableScreenFlag=0,Mirror_PPUMASK=24,NmiDisable=255,
                VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,InvHudActive=0)
            queue=B.M.address(m.bundle,'VRAM_Buffer1');m[queue]=0
            m.ram[2][0x8e]=cursor;m.ram[2][0x8f]=owned;m.ram[2][0xe8]=128
            for at in(0xbd,0xbb,0xbe,0xbf):m.ram[2][at]=0x11
            m.ram[2][0x87a:0x880]=b'\xff'*6
            B.M.invoke(m,'HuUi',p=0x21)
            assert B.M.get(m,'VRAM_Buffer1_Offset')==35
            packet=bytes(m[queue:queue+36]);assert packet[35]==0
            at=0
            while packet[at]:
                size=packet[at+2];assert size and not size&0xc0 and at+3+size<=35
                glyphs.update(packet[at+3:at+3+size]);at+=3+size
            assert at==35;cases+=1
            if cursor==2 and owned:
                assert name in packet;ladder=packet
    assert ladder is not None and not glyphs&{0x2c,0x2d}
    # Reusable Ladder has no stock or icon, including every original C000
    # value. This guards the actual HUD CPY-zero branch rather than X==NONE.
    for stage_byte in range(256):
        m=B.M.fork(seed);m.ram[2][0x8e]=2;m.ram[2][0x8f]=255;m.ram[2][0]=stage_byte
        for at in(0xbd,0xbb,0xbe,0xbf):m.ram[2][at]=0x11
        m.ram[2][0xe8]=128;m.ram[2][0x87a:0x880]=b'\xff'*6
        B.M.put(m,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,NmiDisable=255,InvHudActive=0)
        queue=B.M.address(m.bundle,'VRAM_Buffer1');m[queue]=0
        B.M.invoke(m,'HuUi',p=0x21)
        assert bytes(m[queue:queue+36])==ladder,stage_byte
    lifetime=font_lifetime(image,seed)
    patterns=image[2096848:2096848+32]
    assert sha256(patterns).hexdigest()=='a695f4fc2d1211572a01a2f65aa755c008f09da2d47d466010d4ddbb905e535e'
    return dict(private_candidate_SHA256=C.digest(image),actual_private_HUD_cursor_owner_cases=cases,
        reusable_no_stock_icon_all256_stage_bytes=True,LADDER_name_actual_native_glyphs=True,
        private_art_glyphs_never_emitted_by_HUD=True,exact_donor32B_patterns=True,
        explicit_host_palette2_adaptation=True,actual_candidate_font_contexts=lifetime,
        native_visual_or_transition_replay_claim=False,output_files=0)


def pause(raw):
    import compose_karnov_ladder_native_1113 as C
    import check_karnov_natural_bomb_1113 as Natural
    image,info=C.proposal(raw)
    _,base=Natural.C.cold(dict(Natural.W.Symbols.bundle(),raw=image),
        dict(name='KARNOV',slot=7,cycle=1,raw=34))
    m,_=earned_ladder(base)
    def step(pad=0):m.controller_pad=pad;Natural.Frames.frame(m)
    for _ in range(120):
        step()
        if B.M.get(m,'Player_State')==0 and m.ram[2][0x62]&31<7:break
    else:raise AssertionError('Pause fixture grounded readiness')
    step(68)
    for _ in range(10):
        step()
        if m.ram[2][0x624]&15==3:break
    assert m.ram[2][0x5e]==1 and m.ram[2][0x624]&15==3
    step(16);assert B.M.get(m,'GamePauseStatus')&1
    def frozen():return(bytes(m.ram[2][0x624:0x63f]),bytes(m.ram[2][0x62:0x6c]),
        bytes(m.ram[2][0xc0:0xc4]),m.ram[2][0x5e],m.ram[2][0xe8],
        B.M.get(m,'Player_X_Position'),B.M.get(m,'Player_Y_Position'))
    before=frozen()
    for paused in range(128):
        step(8);assert frozen()==before
        if paused>=23 and B.M.get(m,'GamePauseTimer')==0 and not B.M.get(m,'GamePauseStatus')&128:break
    else:raise AssertionError('Original pause debounce did not expire')
    step(16);assert not B.M.get(m,'GamePauseStatus')&1
    for _ in range(24):
        step()
        if m.ram[2][0x5e]==0:break
    assert m.ram[2][0x624]&15==8 and m.ram[2][0x5e]==0
    return dict(private_candidate_SHA256=C.digest(image),controller_Start_pause_and_resume=True,
        actual_Main_NMI_pause_updates=paused+1,growing_object_original_motor_Bomb_clock_and_position_frozen=True,
        held_Up_during_pause_does_not_climb=True,original_growth_resumes_to8=True,
        synthetic_prepared_earned_pickups=True,native_emulator_claim=False,output_files=0)


def redraw_matrix(raw):
    import compose_karnov_ladder_native_1113 as C
    image,info=C.proposal(raw);seed,_=candidate_cold(image,info['cookie'])
    attrs=raw[B.M.location(seed.bundle,'MTileAttribute'):B.M.location(seed.bundle,'MTileAttribute')+256]
    aggregate=sha256();cases=0;max_bytes=0
    for page,camera in((0,0),(1,7),(255,127)):
        world=page*256+128
        for count in range(1,9):
            for bottom in range(count+1,13):
                m=B.M.fork(seed);s=m.ram[2]
                B.M.put(m,ScreenLeft_PageLoc=page,ScreenLeft_X_Pos=camera,
                    VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,NmiDisable=255)
                queue=B.M.address(m.bundle,'VRAM_Buffer1');m[queue]=0
                s[0x624]=count;s[0x625]=((page<<4)|8)&255;s[0x626]=(page&0xf0)|bottom
                s[0x627]=(bottom-count)*16
                for origin in(B.M.address(m.bundle,'Block_Buffer_1'),B.M.address(m.bundle,'Block_Buffer_2')):
                    for i in range(208):m[origin+i]=(i*17+67)&255
                rows=[(bottom-i)*16 for i in range(count)]
                for y in rows:m[buffer_at(m,world,y)]=0
                before=tuple(bytes(m[base:base+208])for base in(
                    B.M.address(m.bundle,'Block_Buffer_1'),B.M.address(m.bundle,'Block_Buffer_2')))
                direct(m,info['symbols']['KrLadderFullRedraw'])
                size=B.M.get(m,'VRAM_Buffer1_Offset');groups=sorted({y//32 for y in rows})
                assert size==4*count+6+4*len(groups)<=58 and m[queue+size]==0
                max_bytes=max(max_bytes,size);aggregate.update(bytes(m[queue:queue+size+1]))
                assert before==tuple(bytes(m[base:base+208])for base in(
                    B.M.address(m.bundle,'Block_Buffer_1'),B.M.address(m.bundle,'Block_Buffer_2')))
                B.M.consume(m)
                for y in rows:
                    address=0x2000+(page&1)*0x400+(y//8)*32+16
                    assert bytes(m.vram[address:address+2])==b'\x2c\x2d'
                    assert bytes(m.vram[address+32:address+34])==b'\x2c\x2d'
                for group in groups:
                    expected=0
                    for i,(dx,dy)in enumerate(((0,0),(16,0),(0,16),(16,16))):
                        y=group*32+dy
                        palette=2 if dx==0 and y in rows else attrs[m[buffer_at(m,world+dx,y)]]>>6
                        expected|=palette<<(2*i)
                    address=0x23c0+(page&1)*0x400+group*8+4
                    assert m.vram[address]==expected,(page,camera,count,bottom,group,m.vram[address],expected)
                cases+=1
    invisible=0
    for cam_page,cam_x in((0,144),(1,0),(255,0)):
        m=B.M.fork(seed);s=m.ram[2]
        s[0x624]=8;s[0x625]=8;s[0x626]=12;s[0x627]=72
        B.M.put(m,ScreenLeft_PageLoc=cam_page,ScreenLeft_X_Pos=cam_x,
            VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,NmiDisable=255)
        m[B.M.address(m.bundle,'VRAM_Buffer1')]=0
        direct(m,info['symbols']['KrLadderFullRedraw'])
        assert B.M.get(m,'VRAM_Buffer1_Offset')==0 and s[0x624]&15==8 and s[0x627]==72
        invisible+=1
    return dict(private_candidate_SHA256=C.digest(image),synthetic_valid_count_bottom_camera_fixtures=cases,
        native_pages=[0,1,255],all1_to8_segments_all_valid_bottom_rows=True,
        actual_NMI_vertical_commands_and_each_owned_attribute_quadrant_exact=True,
        current_neighbor_palettes_and_native_BB_unchanged=True,maximum_queue_bytes=max_bytes,
        fully_offscreen_redraws_leave_no_commands=invisible,aggregate_queue_SHA256=aggregate.hexdigest(),
        native_visual_claim=False,output_files=0)


def composition(raw):
    import compose_karnov_ladder_native_1113 as C
    import steve_armor_idle_1113 as Steve
    import prince_draw_cache_1113 as Prince
    current=Audit.Bomb.NIGHTLY.read_bytes()
    if C.digest(current)==Audit.STEVE_CURRENT:steve=current
    elif C.digest(current)==Audit.PRINCE_CURRENT:steve=Prince.reverse(current)
    else:
        steve,_=Steve.proposal(raw);assert C.digest(steve)==Audit.STEVE_CURRENT
    prince,_=Prince.proposal(steve);assert C.digest(prince)==Audit.PRINCE_CURRENT
    strict,_=C.proposal(raw)
    # Independent complete-byte oracle: no reliance on feature changelists or
    # source-island descriptions. Rebase the entire strict AA->4b delta.
    delta={i:value for i,(old,value)in enumerate(zip(raw,strict))if old!=value}
    images=[];rows=[];reference=None
    for parent in(raw,steve,prince):
        image,info=C.proposal_current(parent)
        assert C.inverse_current(image)==parent
        expected=bytearray(parent)
        for at,value in delta.items():
            assert parent[at]==raw[at],('Full strict delta overlaps known parent',at)
            expected[at]=value
        assert image==bytes(expected)
        if parent==raw:assert image==strict
        owned=tuple(image[Audit.Bomb.CHR+page*1024:Audit.Bomb.CHR+(page+count)*1024]
            for page,count,_ in Audit.Bomb.OWNED.values())+(image[244477:244504],image[Refactor.Scene.RESIDENT:Refactor.Scene.RESIDENT+16])
        if reference is None:reference=owned
        assert owned==reference
        assert all(a==b or any(change['file_offset']<=i<change['file_offset']+change['bytes']
            for change in info['changes'])for i,(a,b)in enumerate(zip(parent,image)))
        seed,cold=candidate_cold(image,info['cookie'])
        rows.append(dict(parent_SHA256=C.digest(parent),candidate_SHA256=C.digest(image),cold=cold,
            exact_inverse_and_all_foreign_bytes_preserved=True))
        images.append((image,info))
    selected=2 if C.digest(current)==Audit.PRINCE_CURRENT else 1
    image,info=images[selected]
    # Execute complete native paths on the exact current known composition.
    # The strict recipe itself is not weakened; only this test's local image
    # provider selects the already authenticated, closed composition.
    def current_provider(supplied):
        assert supplied==raw,'Exact local fixture pin'
        return image,info
    with patch.object(C,'proposal',current_provider):
        main=main_lifecycle(raw);pressure=main_pressure(raw)
    return dict(known_compositions=rows,all_affected_source_loader_art_bytes_identical=True,
        independent_complete_strict_AA_delta_bytes=len(delta),AA_API_byte_equal_to_strict=True,
        every_foreign_byte_outside_strict_delta_equals_its_parent=True,
        exact_current_composition_Main=main['private_candidate_SHA256'],
        actual_current_Main_updates=main['actual_Main_NMI_updates'],
        actual_current_same_Main_pressure=pressure['maximum_VRAM1_offset'],
        strict_AA_APIs_unchanged=True,native_emulator_claim=False,output_files=0)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--part',choices=('measure','storage-plan','loader-geometry','font','world-snap','candidate-cold','lifecycle-basic','restore-matrix','lifecycle-extended','main-lifecycle','regressions','guards','vectors','main-pressure','finite','cold-vectors','candidate-font','pause','redraw-matrix','composition'),default='measure')
    args=p.parse_args();raw,donor=Audit.inputs()
    report={'storage-plan':lambda:storage_plan(raw),'loader-geometry':lambda:loader_geometry(raw),
        'font':lambda:font_proof(raw,donor),'world-snap':lambda:world_snap(raw),
        'candidate-cold':lambda:candidate_cold_proof(raw),
        'lifecycle-basic':lambda:lifecycle_basic(raw),
        'restore-matrix':lambda:restore_matrix(raw),
        'lifecycle-extended':lambda:lifecycle_extended(raw),
        'main-lifecycle':lambda:main_lifecycle(raw),
        'regressions':lambda:regressions(raw),
        'guards':lambda:auth_guards(raw),
        'vectors':lambda:vectors(raw),
        'main-pressure':lambda:main_pressure(raw),
        'finite':lambda:finite(raw),
        'cold-vectors':lambda:cold_vectors(raw),
        'candidate-font':lambda:candidate_font(raw),
        'pause':lambda:pause(raw),
        'redraw-matrix':lambda:redraw_matrix(raw),
        'composition':lambda:composition(raw),
        'measure':lambda:measure(raw)[2]}[args.part]()
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
