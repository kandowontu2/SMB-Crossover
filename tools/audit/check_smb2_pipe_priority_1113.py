"""Measure exact current Doki source priority repair; no candidate publication."""
from hashlib import sha256
import argparse
import json
import re
import zipfile
from itertools import product
from collections import Counter
from unittest.mock import patch

import check_smb2_flag_handoff_1113 as F
from compose_metal_head_bridge_1112 import assemble_segments

R=F.R
ARCHIVE=R/'docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1/source.zip'
RENDER='build/doki-current-component-1101-v1/src/smb2_roster_render.s'
DOKI='build/doki-current-component-1101-v1/src/doki_current_draw.s'
SOURCE=R/'tools/reference/smb2_pipe_priority_1113.s'


def sources():
    with zipfile.ZipFile(ARCHIVE)as z:
        return z.read(RENDER).decode(),z.read(DOKI).decode()


def normalized(text):
    text=re.sub(r'\.repeat ([0-9]+)\s*\n(.*?)\.endrepeat',lambda m:m[2]*int(m[1]),text,flags=re.S)
    lines=[]
    for line in text.splitlines():
        line=line.split(';',1)[0].strip()
        if not line:continue
        label=re.match(r'^(\w+):(.*)$',line)
        if label:lines.append(label[1]+':');line=label[2].strip()
        if not line:continue
        if line.startswith('.byte'):
            line='.byte '+','.join('$%02x'%int(v.strip().replace('$','0x'),0)for v in line[5:].split(','))
        lines.append(line)
    return '\n'.join(lines)


def measure(raw,*,components=False,_original=True):
    if _original:assert sha256(raw).hexdigest()==F.PIN
    W=F.W;b=dict(W.Symbols.bundle(),raw=raw);render,doki=sources()
    names=('SelectedCharacter','S2Ensure','S2Hurt','S2Clock','S2GraphicsBank','S2Variant',
        'S2Animation','DdqBuildPose','S2NativeCharacter','S2Size','S2Holding','S2Face',
        'S2BodyRecord','S2SetRecord','S2_FIRST_CHR','SmChrBank','METASPRITE_SAMUS_BODY',
        'ObjectMetasprite','Player_SprAttrib','Player_Rel_XPos','Player_Pos_ForScroll',
        'R0','R1','R2','R3','R4','R5','SmPosePtr','S2DokiDrawPacket','DdqFrames','DdqTemplate','DdqPalettes',
        'S2Graphics','S2PublishBody','S2Publish','S2Render','Player_Y_Position','Player_Y_HighPos','R6','R7')
    constants={n:W.address(b,n)for n in names}
    constants.update(CHARACTER_SMB2_ROSTER=25,S2Palettes=W.address(b,'S2PalettePointer::Palettes'),
        S2Role1=W.address(b,'S2PalettePointer::S2OriginalRole1'))
    assert constants['S2Palettes']==0xb82e and constants['S2Role1']==0xb83e
    assert all((constants[n]&255)+12<256 and constants[n]>>8 for n in('S2Palettes','DdqPalettes'))
    graphics=render.split('.proc S2Graphics\n',1)[1].split('.endproc',1)[0]
    graphics=graphics.replace('bne :+','bne GraphicsClass').replace('\n:\n','\nGraphicsClass:\n')
    palette=render.split('.proc S2PalettePointer\n',1)[1].split('Palettes:.byte',1)[0]
    palette=palette.replace('S2OriginalRole1','S2Role1').replace('#<Palettes','#<S2Palettes').replace('#>Palettes','#>S2Palettes')
    old={};proof={}
    for name,text,begin,end in(('graphics',graphics,'S2Graphics','S2SetRecord'),
        ('palette',palette,'S2PalettePointer','S2PalettePointer::Palettes')):
        pc=W.address(b,begin);at=W.location(b,begin);size=W.location(b,end)-at
        body=assemble_segments('.segment "OLD"\n'+normalized(text),{'OLD':pc},constants)[0]['OLD']
        assert len(body)==size
        if _original:assert raw[at:at+size]==body,('Entire current Ready85 source mismatch',name)
        assert sha256(body).hexdigest()=={'graphics':'608cbaff10ef768615097577f71ad5cf1d384ad19ec8f4898dd2e49860b67df7',
            'palette':'e0b026cefbcfa9c55d0525a048874e5c3ec8487c20442dd12d6c8ca6231a1df1'}[name]
        old[name]=body;proof[name]=dict(origin=pc,file=at,bytes=size,SHA256=sha256(body).hexdigest())
    ddq=doki.split('DdqBuildPose:\n',1)[1].split('.segment "PARODIUS_BELLS"',1)[0]
    ddq=ddq.replace('bcs :+','bcs DdqCellReady').replace('\n:\n','\nDdqCellReady:\n')
    ddq=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\+([0-9]+)\b',
        lambda m:'$%04x'%(constants[m[1]]+int(m[2])),ddq)
    ddqbody=assemble_segments('.segment "OLD"\n'+normalized(ddq),{'OLD':constants['DdqBuildPose']},constants)[0]['OLD']
    at=W.location(b,'DdqBuildPose');assert raw[at:at+len(ddqbody)]==ddqbody
    tail=bytes.fromhex('ad')+constants['S2Variant'].to_bytes(2,'little')+bytes.fromhex('1869208d')+constants['SmChrBank'].to_bytes(2,'little')+b'\x60'
    assert ddqbody.endswith(tail)
    old_body=bytes.fromhex('a900')+bytes((0x85,constants['R3'],0x85,constants['R5']))
    body_start=W.location(b,'S2DrawBody');body_end=W.location(b,'S2DrawObjects')
    body_at=body_start+18
    if _original:assert raw[body_at:body_at+6]==old_body and raw.find(old_body,body_at+1,body_end)<0
    body_pc=0xa000+(body_at-16)%8192
    origins=dict(S2_PRIORITY_GRAPHICS=proof['graphics']['origin'],S2_PRIORITY_PALETTE=proof['palette']['origin'],S2_PRIORITY_BODY=body_pc)
    new,labels=assemble_segments(SOURCE.read_text(),origins,constants)
    assert len(new['S2_PRIORITY_GRAPHICS'])==proof['graphics']['bytes']==144
    assert len(new['S2_PRIORITY_PALETTE'])==proof['palette']['bytes']==63
    assert labels['S2PriorityValue']==constants['S2Palettes']-8
    assert len(new['S2_PRIORITY_BODY'])==6
    refs={}
    for old_name,new_name in(('S2Graphics::DokiMeta','G_Meta'),('S2Graphics::SetBody','G_SetBody')):
        oldpc=W.address(b,old_name);newpc=labels[new_name]
        hits=[i for i in range(16,16+128*8192-2)if raw[i]in(0x20,0x4c)and raw[i+1:i+3]==oldpc.to_bytes(2,'little')]
        refs[old_name]=dict(old=oldpc,new=newpc,JSR_JMP_file_offsets=hits)
    result=dict(parent_SHA256=F.PIN,source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        exact_Ready85_member_SHA256=sha256(render.encode()).hexdigest(),exact_Doki_member_SHA256=sha256(doki.encode()).hexdigest(),
        original_complete_source=proof,new_lengths={n:len(v)for n,v in new.items()},
        helper=[labels['S2PriorityValue'],8],palette_code_bytes=55,Palettes_anchor=constants['S2Palettes'],
        OriginalRole1_anchor=constants['S2Role1'],DdqPalette=constants['DdqPalettes'],
        unchanged_Ddq_builder_source_bytes=len(ddqbody),body_site=[body_at,6,old_body.hex()],
        moved_internal_references=refs,new_ROM_RAM_CHR_bytes=0,candidate_prepared=False,outputs=0,Mesen_run=False)
    return(result,old,new,labels,constants,b)if components else result


def pointer_matrix(raw):
    """Compressed-pointer math prototype only, not an integrated candidate."""
    q,old,new,labels,constants,b=measure(raw,components=True)
    palette=q['original_complete_source']['palette'];at=palette['file']
    prototype=bytearray(raw);prototype[at:at+63]=new['S2_PRIORITY_PALETTE'];prototype=bytes(prototype)
    N=F.W.N;seed=F.cold(raw,4);cases=0;foreign=0
    for variant in range(256):
        for native in range(4):
            for flags in(0x31,0xf0):
                a=F.view(seed,raw);b=F.view(seed,prototype)
                for m in(a,b):N.put(m,S2Variant=variant,S2NativeCharacter=native)
                ra=N.invoke(a,'S2PalettePointer',p=flags);rb=N.invoke(b,'S2PalettePointer',p=flags)
                assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P')),(variant,native,flags,ra,rb)
                assert bytes(a[:0x8000])==bytes(b[:0x8000])and a.ram==b.ram and a.rawtags==b.rawtags
                cases+=1
    for owner in range(256):
        if owner==25:continue
        for flags in(0x31,0xf0):
            a=F.view(seed,raw);b=F.view(seed,prototype)
            for m in(a,b):N.put(m,SelectedCharacter=owner)
            ra=N.invoke(a,'S2PalettePointer',p=flags);rb=N.invoke(b,'S2PalettePointer',p=flags)
            assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P'))
            assert bytes(a[:0x8000])==bytes(b[:0x8000])and a.ram==b.ram and a.rawtags==b.rawtags
            foreign+=1
    return dict(passed=True,prototype_scope='compressed palette math only; no integrated candidate',
        pointer_AXYP_all_RAM_cases=cases,foreign_owner_AXYP_all_RAM_cases=foreign,
        source_native_classes=[0,1,2,3],all_variant_byte_values=True,Palettes_anchor=constants['S2Palettes'],
        OriginalRole1_anchor=constants['S2Role1'],source_SHA256=q['source_SHA256'],outputs=0,Mesen_run=False)


def render_matrix(raw,*,full=False):
    """Directed rendering inputs; actual native renderer/CHR publication/OAM."""
    import compose_smb2_pipe_priority_1113 as C
    parent=C.Mirror.all_mirrors_proposal(C.Mirror.Flag.proposal(raw)[0])[0]
    image,info=C.proposal(parent);assert C.inverse(image)==parent
    N=F.W.N;graphics=0;body=0;priority=0
    variants=range(8)if full else(0,4)
    seeds={v:F.cold(parent,v)for v in variants}
    native_map=(0,3,2,1,0,1,2,3)
    assert all(N.get(m,'S2NativeCharacter')==native_map[v]for v,m in seeds.items())
    sizes=(0,1)if full else(0,)
    holding=(0,1)if full else(0,)
    animations=range(11)if full else(0,7)
    for variant,size,face,held,animation,attr in product(variants,sizes,(0,1),holding,animations,(0,32,255)):
        fixture=N.fork(seeds[variant])
        N.put(fixture,S2Size=size,S2Face=face,S2Holding=held,S2Animation=animation,S2Hurt=0,Player_SprAttrib=attr,
            CurrentOAMOffset=0,GuestOamRotationActive=0,R3=90,R5=37)
        a=F.view(fixture,parent);b=F.view(fixture,image)
        ra=N.invoke(a,'S2Graphics');rb=N.invoke(b,'S2Graphics')
        for m in(a,b):
            assert tuple(N.get(m,n)for n in('S2Variant','S2NativeCharacter','S2Size','S2Face','S2Holding','S2Animation'))==(
                variant,native_map[variant],size,face,held,animation),'Render fixture was reset instead of exercised'
        assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P')),(variant,size,face,held,animation,'Graphics ABI',ra,rb)
        active=bool(ra['P']&1)
        assert N.get(b,'Player_SprAttrib')==(attr&32 if active else attr)
        if active:assert N.get(b,'R3')==attr&32
        assert N.get(a,'SmPosePtr')==N.get(b,'SmPosePtr')and N.get(a,'SmPosePtr',1)==N.get(b,'SmPosePtr',1)
        assert N.get(a,'SmChrBank')==N.get(b,'SmChrBank')
        graphics+=1
        a=F.view(fixture,parent);b=F.view(fixture,image)
        ra=N.invoke(a,'S2DrawBody');rb=N.invoke(b,'S2DrawBody')
        assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P')),(variant,size,face,held,animation,'Draw ABI',ra,rb)
        used=N.get(a,'CurrentOAMOffset');assert used==N.get(b,'CurrentOAMOffset')
        old_oam=bytes(a[0x200:0x300]);expected=bytearray(old_oam)
        if active:
            assert N.get(b,'R5')==0 and N.get(b,'R3')==attr&32
            for at in range(2,used,4):expected[at]|=attr&32
            priority+=bool(attr&32)
        assert bytes(b[0x200:0x300])==bytes(expected),(variant,size,face,held,animation,attr,'actual native OAM')
        assert a.chr_latches==b.chr_latches and bytes(a[0x5c90:0x5ca1])==bytes(b[0x5c90:0x5ca1])
        body+=1
        if full and body%264==0:print(json.dumps(dict(priority_render_progress=body,completed_variant=variant)),flush=True)
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],exact_inverse=True,
        synthetic_pose_and_attribute_inputs=True,all8=full,graphics_AXYP_pose_CHR_pairs=graphics,
        real_native_body_renderer_OAM_pairs=body,priority_OAM_cases=priority,
        actual_cold_native_character_map={str(v):N.get(m,'S2NativeCharacter')for v,m in seeds.items()},
        source_pose_inputs_retained_after_Ensure=True,
        colors_facings_packets_geometry_other_OAM_bytes_exact=True,natural_pickup_or_route_claim=False,
        outputs=0,Mesen_run=False)


def domains(raw):
    import compose_smb2_pipe_priority_1113 as C
    import check_smb2_foot_mirror_1113 as Fixed
    parent=C.Mirror.all_mirrors_proposal(C.Mirror.Flag.proposal(raw)[0])[0]
    image,info=C.proposal(parent);N=F.W.N;b=dict(F.W.Symbols.bundle(),raw=raw)
    _,_,_,_,constants,_=measure(raw,components=True)
    with zipfile.ZipFile(ARCHIVE)as z:
        core=z.read('build/doki-current-component-1101-v1/src/smb2_roster_core.s').decode()
    reset=core.split('.proc S2ResetTransient\n',1)[1].split('.endproc',1)[0]
    reset=reset.replace('bne :+','bne ResetNoMama').replace('\n:\n','\nResetNoMama:\n')
    defs=dict(constants)
    for name in set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',reset)):
        key=name if name in b['syms']else'S2ResetTransient::'+name
        if key in b['syms']:defs[name]=F.W.address(b,key)
    reset=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\+([0-9]+)\b',lambda m:'$%04x'%(defs[m[1]]+int(m[2])),reset)
    body=assemble_segments('.segment "RESET"\n'+normalized(reset),
        {'RESET':F.W.address(b,'S2ResetTransient')},defs)[0]['RESET']
    at=F.W.location(b,'S2ResetTransient');assert raw[at:at+len(body)]==body
    assert len(re.findall(r'\bsta S2NativeCharacter\b',core))==1
    assert'cmp #8\n bcc Valid\n lda #0\nValid:tax\n lda VariantNative,x\n sta S2NativeCharacter'in core
    table=F.W.location(b,'S2ResetTransient::VariantNative')
    native_map=(0,3,2,1,0,1,2,3);assert tuple(raw[table:table+8])==native_map
    openings=[]
    for variant in range(8):
        m=F.cold(image,variant)
        assert N.get(m,'S2NativeCharacter')==native_map[variant]
        openings.append(dict(variant=variant,native=N.get(m,'S2NativeCharacter'),ready=N.get(m,'S2Ready')))
    seed=F.cold(image,4);builder=0;publish=0
    for variant,face,held,animation in product(range(8),(0,1),(0,1),range(11)):
        m=N.fork(seed);m.raw_page(1,246);m.raw_page(2,208)
        N.put(m,CurrentBank=246,CurrentBankC=208,S2Variant=variant,S2Face=face,
            S2Holding=held,S2Animation=animation)
        cpu,low=Fixed.invoke(m,constants['DdqBuildPose'])
        assert not cpu.p&1 and N.get(m,'SmChrBank')==32+variant
        builder+=1
    for lowchr in range(256):
        m=N.fork(seed)
        N.put(m,SmChrBank=lowchr,R3=90,R5=37)
        result=N.invoke(m,'S2PublishBody',y=91)
        assert result['Y']==0 and N.get(m,'R3')==90 and N.get(m,'R5')==37
        assert N.get(m,'CurrentCHRBank')==lowchr and N.get(m,'X5ChrMode')==131
        publish+=1
    # Real Select wraps exactly8 values; no direct variant-byte writes.
    with patch.object(N,'Bus',F.W.ControllerBus):menu=F.W.UI.seed(dict(b,raw=image),0)
    for key in(4,4,4):F.W.UI.key(menu,key)
    values=[]
    for _ in range(9):
        values.append(N.get(menu,'S2Variant'));F.W.UI.key(menu,32)
    assert values==list(range(8))+[0]
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],original_ResetTransient_source_bytes=len(body),
        sole_NativeCharacter_writer_and_bounded8_entry_table=True,actual_cold_native_map=openings,
        actual_Select_values=values,Ddq_C0_return_and_CHR_cases=builder,
        real_PublishBody_Y0_R3_R5_lifetime_cases=publish,actual_shared_CHR_callback=True,
        synthetic_builder_and_CHR_inputs=True,outputs=0,Mesen_run=False)


def references(raw):
    q,old,new,labels,constants,b=measure(raw,components=True)
    _,doki=sources()
    text=doki.split('DdqS2Standing:\n',1)[1].split('DdqMenuName:\n',1)[0]
    text=text.replace('S2Graphics::DokiMeta','StandingMeta').replace('S2Graphics::SetBody','StandingBody')
    text=text.replace('bne :+','bne StandingClass').replace('\n:\n','\nStandingClass:\n')
    constants.update(DdqStanding=F.W.address(b,'DdqStanding'),
        StandingMeta=F.W.address(b,'S2Graphics::DokiMeta'),StandingBody=F.W.address(b,'S2Graphics::SetBody'))
    pc=F.W.address(b,'DdqS2Standing');at=F.W.location(b,'DdqS2Standing')
    body=assemble_segments('.segment "STANDING"\n'+normalized(text),{'STANDING':pc},constants)[0]['STANDING']
    assert len(body)==40 and raw[at:at+40]==body
    assert raw[974799:974802]==bytes.fromhex('4c9bb6')and raw[974826:974829]==bytes.fromhex('4c8bb6')
    current=raw[16:16+128*8192];proof={}
    for name in('S2Graphics::DokiMeta','S2Graphics::SetBody','S2Graphics::No',
        'S2Graphics::Foreign','S2PalettePointer::USAPalette','S2PalettePointer::PaletteHigh','S2PalettePointer::No'):
        value=F.W.address(b,name);word=value.to_bytes(2,'little')
        words=[i+16 for i in range(len(current)-1)if current[i:i+2]==word]
        own=[i for i in words if(i-16)//8192==118]
        direct=[i-1 for i in own if raw[i-1]in(0x20,0x4c)]
        pattern=bytes((0xa9,value&255,0x8d,0x6c,1,0xa9,value>>8,0x8d,0x6d,1))
        far=[i+16 for i in range(len(current)-len(pattern)+1)if current[i:i+len(pattern)]==pattern]
        typed=[]
        for item in far:
            tail=raw[item+len(pattern):item+len(pattern)+5]
            assert tail[0]==0xa9 and tail[2]in(0x20,0x4c)and tail[3:5]==bytes.fromhex('5a01')
            typed.append(dict(file=item,target_bank=tail[1]))
        assert not any(t['target_bank']==246 for t in typed),(name,'Unexpected actual S2 farcall producer',typed)
        if name.endswith('DokiMeta'):assert direct==[972388,974799]and own==[i+1 for i in direct]
        elif name.endswith('SetBody'):assert direct==[974826]and own==[974827]
        elif name.startswith('S2PalettePointer::'):
            outside=[i for i in own if not 972799<=i<972862]
            if name.endswith('PaletteHigh'):
                # Cross-instruction bytes20 B8 from JSR A9B8, not pointerB820.
                assert outside==[968289]and raw[968289:968292]==bytes.fromhex('20b8a9')
                assert F.W.location(b,'S2N8A52')==968289
            else:assert not outside,(name,'Unexpected moved own code/data inbound',outside)
        proof[name]=dict(word=value,own_word_references=own,own_direct_transfers=direct,
            literal_farcall_producers_with_actual_banks=typed,other_banks_unmodified=[i for i in words if i not in own])
    assert labels['G_No']==F.W.address(b,'S2Graphics::No')
    assert labels['G_Foreign']==F.W.address(b,'S2Graphics::Foreign')
    assert labels['G_AnimationIndex']==F.W.address(b,'S2Graphics::AnimationIndex')
    return dict(passed=True,standing_complete_current_source_bytes=40,source_inbound=proof,
        unchanged_Graphics_No_Foreign_Animation_anchors=True,unrelated_matches=[652957,32781],
        public_entries_and_palette_data_anchors_unchanged=True,outputs=0,Mesen_run=False)


def foreign(raw):
    import compose_smb2_pipe_priority_1113 as C
    parent=C.Mirror.all_mirrors_proposal(C.Mirror.Flag.proposal(raw)[0])[0]
    image,info=C.proposal(parent);N=F.W.N;seed=F.cold(parent,4);cases=0
    for owner in range(256):
        if owner==25:continue
        for flags in(0x31,0xf0):
            for name in('S2Graphics','S2DrawBody','S2PalettePointer'):
                a=F.view(seed,parent);b=F.view(seed,image)
                for m in(a,b):N.put(m,SelectedCharacter=owner,Player_SprAttrib=255,R3=90,R5=37)
                ra=N.invoke(a,name,p=flags);rb=N.invoke(b,name,p=flags)
                assert tuple(ra[k]for k in('A','X','Y','P'))==tuple(rb[k]for k in('A','X','Y','P'))
                assert bytes(a[:0x8000])==bytes(b[:0x8000])and a.ram==b.ram and a.rawtags==b.rawtags
                cases+=1
    pair=[]
    for rom in(parent,image):
        with patch.object(N,'Bus',F.W.ControllerBus):m=F.W.UI.seed(dict(seed.bundle,raw=rom),0)
        for key in(4,4,4):F.W.UI.key(m,key)
        frames=[]
        for cycle in range(8):
            frames.append((bytes(m[0x200:0x300]),bytes(m.vram),tuple(m.chr_latches)))
            F.W.UI.key(m,32)
        pair.append(frames)
    assert pair[0]==pair[1]
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],all_non25_guard_AXYP_all_RAM_cases=cases,
        uninitialized_foreign_physics_executed=False,actual8menu_preview_OAM_VRAM_CHR_pairs=8,
        outputs=0,Mesen_run=False)


def vectors(raw):
    import compose_smb2_pipe_priority_1113 as C
    import check_smb2_foot_mirror_1113 as Fixed
    import check_bub_current_budget_1113 as Frames
    parent=C.Mirror.all_mirrors_proposal(C.Mirror.Flag.proposal(raw)[0])[0]
    image,info=C.proposal(parent);N=F.W.N;seed=F.cold(image,4);busy=None
    for tick in range(240):
        seed.controller_pad=1;Frames.frame(seed)
        if N.get(seed,'S2AudioActiveBank')in(119,120)and seed[0x4015]&16 and not N.get(seed,'S2Clock')&8:
            busy=dict(Main=tick+1,x=N.get(seed,'Player_X_Position')+256*N.get(seed,'Player_PageLoc'),
                y=N.get(seed,'Player_Y_Position'),health=N.get(seed,'S2Health'),bank=N.get(seed,'S2AudioActiveBank'))
            break
    assert busy
    native=N.NesMPU;points=set();counts=Counter();minimum=255;music=0
    render=F.W.address(seed.bundle,'MetaspriteRenderLoop')
    def owned(m,pc):
        if pc<0x8000:return False
        tag=m.rawtags[(pc-0x8000)//8192]
        return tag==246 and(0xb62f<=pc<0xb6bf or 0xb7ef<=pc<0xb82e or 0xb762<=pc<0xb768 or pc in(0xbfbf,0xbfda))
    class Guarded(native):
        _irq_origin=None
        def irq(self):
            self._irq_origin=(self.pc,self.sp);return native.irq(self)
        def nmi(self):
            self._irq_origin=(self.pc,self.sp);return native.nmi(self)
        def step(self):
            if self._irq_origin:
                if(self.pc,self.sp)==self._irq_origin:self._irq_origin=None
                else:assert not owned(self.memory,self.pc),'ISR reached a modified Main-only worker'
            return native.step(self)
    def observe(m,c):
        nonlocal minimum,music
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if not owned(m,c.pc)and not(tag==132 and render<=c.pc<render+512):return
        key=(tag,c.pc,c.sp,c.p&4,N.get(m,'R3'))
        if key in points:return
        points.add(key)
        for kind in('IRQ','busy-lagNMI'):
            if kind=='IRQ'and c.p&4:continue
            low,advance=Fixed.paired_interrupt(m,c,parent,image,kind)
            minimum=min(minimum,low);counts[kind]+=1
            if kind=='busy-lagNMI':music+=advance
    with patch.object(N,'NesMPU',Guarded):
        for variant in(0,4):
            for attr in(0,32):
                m=N.fork(seed)
                N.put(m,S2Variant=variant,S2NativeCharacter=0,Player_SprAttrib=attr,
                    CurrentOAMOffset=0,GuestOamRotationActive=0,NmiDisable=255)
                for name in('S2Graphics','S2DrawBody','S2PalettePointer','DdqS2Standing'):
                    z=N.fork(m);pc=F.W.address(z.bundle,name);z.raw_page(1,246);N.put(z,CurrentBank=246)
                    Fixed.invoke(z,pc,observe=observe)
    assert counts['IRQ']and counts['busy-lagNMI']and music>0 and minimum>=128
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],reached_changed_or_R3_live_renderer_points=len(points),
        actual_paired_vectors=dict(counts),minimum_SP=minimum,genuine_busy_source_prefix=busy,
        exact_paired_music_advances=music,no_audio_or_clock_masking=True,
        whole_original_ISR_and_new_foreground_continuation_equal=True,
        private_RAM_SMC_scratch_AXYP_live_stack_maps_equal=True,synthetic_attribute_inputs=True,
        outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in('pointer','basics','render','domains','references','foreign','vectors'):p.add_argument('--'+n,action='store_true')
    args=p.parse_args();raw=F.load_input()
    q=vectors(raw)if args.vectors else foreign(raw)if args.foreign else references(raw)if args.references else domains(raw)if args.domains else render_matrix(raw,full=args.render)if args.basics or args.render else pointer_matrix(raw)if args.pointer else measure(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
