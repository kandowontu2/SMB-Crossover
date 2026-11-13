"""Read-only original/current equipment and owned-space audit; no outputs."""

import argparse
from hashlib import sha256
import json
import re
import zipfile

import compose_karnov_bomb_1112 as Bomb
import compose_karnov_scene_motor_1113 as Scene
from recover_karnov_actor_1101_v1 import ROM,EXPECTED,graph,emit

PACKET=Scene.PACKET
SOURCE=Bomb.R/'tools/reference/karnov_equipment_1113.s'
FROZEN_PARENT='aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1'
STEVE_CURRENT='62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639'


def digest(data):return sha256(data).hexdigest()


def inputs():
    raw=Bomb.NIGHTLY.read_bytes();donor=ROM.read_bytes()
    if digest(raw)==STEVE_CURRENT:
        import steve_armor_idle_1113 as Steve
        raw=Steve.reverse(raw)
    assert digest(raw)==FROZEN_PARENT,'Use explicit authenticated normalization to frozen aa501'
    assert digest(donor)==EXPECTED
    previous=Scene.inverse(raw)
    assert Scene.transform(previous)[0]==raw
    assert digest(PACKET.read_bytes())==Scene.PACKET_SHA
    return raw,donor


def members():
    with zipfile.ZipFile(PACKET)as z:
        return [(n,z.getinfo(n).file_size)for n in z.namelist()
                if any(s in n.lower()for s in('kernel','lbl','assembly','config','grant','layout','resource'))]


def donor_ladder(donor):
    rows=[]
    for name,lo,hi,bank,data in(
        ('grow',0xa4b6,0xa5bd,12,(0x9b97,0xc264)),
        ('restore',0xa5bd,0xa693,12,(0x9ac8,0xc264)),
        ('overlay',0xb46f,0xb49c,12,()),
        ('retract',0xd700,0xd73c,None,()),
        ('rebuild',0xdb00,0xdb26,None,())):
        m,code,tables,external,ram,reads=graph(donor,lo,hi,{},(1,bank)if bank else None,data)
        rows.append(dict(name=name,start=lo,end=hi,original_bytes=hi-lo,instructions=len(code),
            external={hex(k):list(map(hex,v))for k,v in external.items()},
            RAM_fields=list(map(hex,sorted(ram))),ROM_reads=list(map(hex,sorted(reads)))))
    return rows


def footprint(raw):
    import check_karnov_bomb_1112 as Cpu
    from check_jay_silius_cold_resident_1110 import pack
    b=Cpu.Cpu.Flower.Host.C.Start.W.bundle(raw)
    inverse={'cc':0xb0,'cs':0x90,'eq':0xd0,'ne':0xf0,'mi':0x10,'pl':0x30,'vc':0x70,'vs':0x50}
    counts={};examples=[];mismatches=[];excluded_loans=0
    files=('host/kr-host-actor.inc','original-source/portable_weapon.inc','original-source/portable_clear.inc',
           'host/karnov-options-portable-v7.inc')
    with zipfile.ZipFile(PACKET)as z:
        for filename in files:
            text=z.read(filename).decode()
            for name,cond,target in re.findall(r'^(Kr_[A-F0-9]+):\s*j(cc|cs|eq|ne|mi|pl|vc|vs)\s+(Kr_[A-F0-9]+)',text,re.M):
                if name not in b['syms']or target not in b['syms']:continue
                pc=Cpu.M.address(b,name);dest=Cpu.M.address(b,target)
                role='actor'if 0xa000<=pc<0xc000 else'options'if 0xd600<=pc<0xde00 else None
                if role is None:continue
                if role=='options'and any(lo<=pc<hi for lo,hi in Bomb.LOANS):
                    excluded_loans+=1;continue
                page,count,origin=Bomb.OWNED[role];at=Bomb.CHR+page*1024+pc-origin
                want=bytes((inverse[cond],3,0x4c,dest&255,dest>>8))
                if raw[at:at+5]!=want:
                    mismatches.append((name,pc,raw[at:at+5].hex()))
                    continue
                delta=dest-pc-2
                if -128<=delta<=127:
                    counts[role]=counts.get(role,0)+1
                    if len(examples)<6:examples.append(dict(source=name,PC=pc,target=dest,delta=delta))
    sizes={}
    for role,(page,count,_)in Bomb.OWNED.items():
        body=raw[Bomb.CHR+page*1024:Bomb.CHR+(page+count)*1024]
        sizes[role]=dict(carrier_bytes=len(body),packed_bytes=len(pack(body)),
            conservative_near_branches=counts.get(role,0),possible_relink_savings=3*counts.get(role,0))
    return dict(current_owned=sizes,source_longbranch_examples=examples,
        explicitly_excluded_Bomb_loan_source_rows=excluded_loans,
        nonmatching_source_rows=len(mismatches),nonmatching_examples=mismatches[:8],
        kernel_end=Cpu.M.address(b,'KrKernelEnd'),hud_end=Cpu.M.address(b,'KrHudEnd'),
        actor_unmodified_padding=((0xbfc5,0xbfcb),(0xbfdd,0xbfe0),(0xbff0,0xc000)),
        new_runtime_memory_granted=False,ROM_mutation=False)


def renderer_plan(raw,donor):
    import check_karnov_bomb_1112 as Cpu
    b=Cpu.Cpu.Flower.Host.C.Start.W.bundle(raw)
    address=lambda n:Cpu.M.address(b,n)
    location=lambda n:Cpu.M.location(b,n)
    names=('MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight')
    assert all((location(n)-16)//8192==3 and 0xa000<=address(n)<0xc000 for n in names)
    fields={short:address(name)+0x2000 for short,name in zip(
        ('NativeTopLeft','NativeTopRight','NativeBotLeft','NativeBotRight'),names)}
    fields.update(CurrentBankC=address('CurrentBankC'),NativeVRAM=address('VRAM_Buffer1'))
    # Prototype origin is a standalone assembly coordinate, not a live lease.
    prepared=re.sub(r'NativeVRAM\+(\d+)',lambda m:'NativeVRAM'+m[1],SOURCE.read_text())
    for n in(3,4,8,9):fields['NativeVRAM'+str(n)]=fields['NativeVRAM']+n
    code,labels=Bomb.assemble_segments(prepared,{'NATIVE_QUAD':0x9000},fields)
    assert len(code['NATIVE_QUAD'])==44
    glyphs=(0x2c,0x2d)
    refs={tile:{name:[i for i,value in enumerate(raw[location(name):location(name)+256])if value==tile]
                for name in names}for tile in glyphs}
    assert not any(values for group in refs.values()for values in group.values())
    with zipfile.ZipFile(PACKET)as z:
        scratch_refs={n:[line for line in z.read(n).decode().splitlines()
            if re.search(r'KrState\+\$00(?:a[b-f]|b[0-3])',line,re.I)]for n in(
                'host/kr-host-actor.inc','original-source/portable_weapon.inc','host/karnov-options-portable-v7.inc')}
    assert not any(scratch_refs.values())
    patterns=b''.join(donor[16+131072+38*1024+(tile&63)*16:
                           16+131072+38*1024+(tile&63)*16+16]for tile in(0xbe,0xbf))
    return dict(unallocated_prototype=True,native_quad_bytes=len(code['NATIVE_QUAD']),
        pattern_bytes=len(patterns),donor_pattern_SHA256=digest(patterns),
        donor_tiles=(0xbe,0xbf),proposed_private_HUD_tiles=glyphs,
        all_256_native_metatile_glyph_refs=refs,
        native_pattern_table_bank=3,native_C_alias_addresses=fields,
        current_core_AB_to_B3_source_references=scratch_refs,
        loader_and_IRQ_qualified=False,full_Ladder_fit_proved=False,
        source_SHA256=digest(SOURCE.read_bytes()))


def renderer_proof(raw,donor):
    """Standalone cartridge-read model; no live-code overlay or ISR claim."""
    from verify_native_relocation import NesMPU
    plan=renderer_plan(raw,donor);fields=plan['native_C_alias_addresses']
    prepared=re.sub(r'NativeVRAM\+(\d+)',lambda m:'NativeVRAM'+m[1],SOURCE.read_text())
    parts,_=Bomb.assemble_segments(prepared,{'NATIVE_QUAD':0x9000},fields)
    class Memory(list):
        def __getitem__(self,a):
            if isinstance(a,int)and 0xc000<=a<0xe000:
                if self.bank&128:return raw[16+(self.bank&127)*8192+a-0xc000]
                return self.private[a-0xc000]
            return super().__getitem__(a)
        def __setitem__(self,a,v):
            if a==0x5116:self.bank=v;self.maps.append(v)
            if isinstance(a,int)and 0xc000<=a<0xe000:
                assert not self.bank&128,('Unexpected native table ROM write',a,v)
                self.private[a-0xc000]=v;return
            super().__setitem__(a,v)
    m=Memory([0]*65536);m.private=bytearray((i*17+9)&255 for i in range(8192));m.maps=[];m.bank=2
    m[0x9000:0x9000+44]=parts['NATIVE_QUAD']
    rows=0;minimum=224
    for bank in(2,3,215):
        for offset in(0,10,50):
            for tile in range(256):
                m.bank=bank;m.maps=[];m[fields['CurrentBankC']]=bank
                m[fields['NativeVRAM']:fields['NativeVRAM']+80]=[0]*80
                c=NesMPU(memory=m,pc=0x9000);c.a,c.x,c.y,c.p,c.sp=85,offset,tile,0x31,224
                c.stPushWord(0x5aff)
                for step in range(30):
                    if c.pc==0x5b00:break
                    minimum=min(minimum,c.sp);c.step()
                else:raise AssertionError(('Native quad component bound',c.pc,c.sp))
                assert(c.x,c.y,c.sp,c.a,c.p&0x4d)==(offset,tile,224,bank,0x01)
                assert m.maps==[131,bank]and m.bank==bank and m[fields['CurrentBankC']]==bank
                for name,delta in(('NativeTopLeft',3),('NativeTopRight',4),('NativeBotLeft',8),('NativeBotRight',9)):
                    want=raw[16+3*8192+fields[name]-0xc000+tile]
                    assert m[fields['NativeVRAM']+offset+delta]==want
                assert m.private==bytes((i*17+9)&255 for i in range(8192))
                rows+=1
    return dict(standalone_component=True,actual_native_ROM_quads=True,cases=rows,
        code_bytes=44,minimum_SP=minimum,source_state_unchanged=True,live_IRQ_or_cold_proved=False)


def relink_plan(raw):
    """Source islands retain every original entry named by the host wrappers."""
    import check_karnov_bomb_1112 as Cpu
    b=Cpu.Cpu.Flower.Host.C.Start.W.bundle(raw)
    address=lambda n:Cpu.M.address(b,n)
    core=('host/kr-host-actor.inc','original-source/portable_weapon.inc','original-source/portable_clear.inc')
    with zipfile.ZipFile(PACKET)as z:
        source={n:z.read(n).decode()for n in z.namelist()if n.startswith('host/')and n.endswith(('.inc','.s'))}
        for name in core:source[name]=z.read(name).decode()
    # This conservative set includes every direct symbolic core entry/data
    # name in any retained owning host fragment, including dormant references.
    references=set()
    for name,text in source.items():
        if name not in core:references.update(re.findall(r'\bKr_[A-F0-9]{4}\b',text))
    anchors={n:address(n)for n in references if n in b['syms']and 0xa087<=address(n)<0xafbb}
    assert {'Kr_F28D','Kr_AAB2','Kr_C2B7'}<=anchors.keys()
    starts=sorted(set(anchors.values())|{0xa087,0xafbb})
    inverse={'cc':0xb0,'cs':0x90,'eq':0xd0,'ne':0xf0,'mi':0x10,'pl':0x30,'vc':0x70,'vs':0x50}
    selected={pc:[]for pc in starts[:-1]};cross=[]
    for filename in core:
        for name,cond,target in re.findall(r'^(Kr_[A-F0-9]+):\s*j(cc|cs|eq|ne|mi|pl|vc|vs)\s+(Kr_[A-F0-9]+)',source[filename],re.M):
            if name not in b['syms']or target not in b['syms']:continue
            pc,dest=address(name),address(target)
            at=Bomb.CHR+399*1024+pc-0xa000
            if raw[at:at+5]!=bytes((inverse[cond],3,0x4c,dest&255,dest>>8)):continue
            if not -128<=dest-pc-2<=127:continue
            found=next(((lo,hi)for lo,hi in zip(starts,starts[1:])if lo<=pc<hi),None)
            if found and found[0]<=dest<found[1]:selected[found[0]].append(pc)
            else:cross.append(pc)
    islands=[dict(begin=lo,end=hi,branch_sites=len(selected[lo]),potential_tail=3*len(selected[lo]))
             for lo,hi in zip(starts,starts[1:])]
    return dict(unallocated=True,external_symbolic_anchors={n:hex(v)for n,v in sorted(anchors.items(),key=lambda p:p[1])},
        islands=islands,total_same_island_savings=sum(v['potential_tail']for v in islands),
        excluded_cross_island_near_branches=len(cross),all37_service_entries_unchanged=True,
        current_handwritten_host_and_Bomb_positions_unchanged_by_plan=True,
        full_source_relink_proved=False,live_cold_IRQ_and_abilities_proved=False)


def relink_core(raw,*,compact=False,verify_baseline=True):
    """Reassemble three exact current source islands; no candidate mutation."""
    import check_karnov_bomb_1112 as Cpu
    from check_steve_shatterhand_upgrade_transport_1111 import H
    b=Cpu.Cpu.Flower.Host.C.Start.W.bundle(raw)
    address=lambda n:Cpu.M.address(b,n)
    files={'ACTOR_CORE':('host/kr-host-actor.inc',0xa087,0xac06),
           'WEAPON_CORE':('original-source/portable_weapon.inc',0xac06,0xafa4),
           'CLEAR_CORE':('original-source/portable_clear.inc',0xafa4,0xafbb)}
    branches={'cc':(0x90,0xb0,'bcc','bcs'),'cs':(0xb0,0x90,'bcs','bcc'),
        'eq':(0xf0,0xd0,'beq','bne'),'ne':(0xd0,0xf0,'bne','beq'),
        'mi':(0x30,0x10,'bmi','bpl'),'pl':(0x10,0x30,'bpl','bmi'),
        'vc':(0x50,0x70,'bvc','bvs'),'vs':(0x70,0x50,'bvs','bvc')}
    texts=[];selected=[]
    with zipfile.ZipFile(PACKET)as z:
        for segment,(name,lo,hi)in files.items():
            text=z.read(name).decode()
            lines=[f'.segment "{segment}"']
            for line in text.splitlines():
                found=re.match(r'^(Kr_[A-F0-9]+):\s*j(cc|cs|eq|ne|mi|pl|vc|vs)\s+(Kr_[A-F0-9]+)',line)
                if not found:lines.append(line);continue
                label,cond,target=found.groups();pc,dest=address(label),address(target)
                short,inverse,op,opposite=branches[cond]
                # ca65's retained macro can shorten an already-defined
                # backward label; forward targets remain its five-byte form.
                # Derive that source policy rather than reading new code as
                # if it were the old instruction stream during an inverse.
                if dest<pc and -128<=dest-pc-2<=127:
                    lines.append(f'{label}: {op} {target}')
                else:
                    if compact and lo<=dest<hi and -128<=dest-pc-2<=127:
                        lines.append(f'{label}: {op} {target}');selected.append(pc)
                    else:
                        skip='KrFarSkip_'+label
                        lines.extend((f'{label}: {opposite} {skip}',f'jmp {target}',skip+':'))
            texts.extend(lines)
    body='\n'.join(texts)
    labels=set(re.findall(r'^(\w+):',body,re.M))
    external={n for n in re.findall(r'\bKr\w+\b',body)if n not in labels}
    constants=dict(KrState=0xc000,KrPointer=3,KrDispatch=address('KrInlineDispatch'),
        KrExternal_C1C7=address('KrSceneCallback'),KrExternal_C81D=address('KrSoundCallback'),
        KrExternal_C3D8=address('KrTerrainCallback'),KrExternal_C2B7=0xafa4)
    for name in external-set(constants):constants[name]=address(name)
    definitions=''.join(f'{name}=${value:04x}\n'for name,value in constants.items())
    linked=H.assemble(definitions+body,{segment:(lo,hi-lo)for segment,(_,lo,hi)in files.items()})
    linked['shortened']=tuple(selected)
    preserved={};tails={}
    for segment,(_,lo,hi)in files.items():
        old=raw[Bomb.CHR+399*1024+lo-0xa000:Bomb.CHR+399*1024+hi-0xa000]
        image=linked['images'][segment]
        if not compact and verify_baseline:assert image==old,(segment,len(image),len(old),next((i for i,p in enumerate(zip(image,old))if p[0]!=p[1]),None))
        tails[segment]=(lo+len(image),hi)
    for name,want in(('Kr_F28D',0xa087),('Kr_AAB2',0xac06),('Kr_C2B7',0xafa4)):
        assert linked['symbols'][name]==want;preserved[name]=want
    return linked,dict(compacted=compact,baseline_source_exact=not compact and verify_baseline,source_islands=linked['used'],
        selected_branches=len(selected),potential_tail_ranges=tails,external_anchors=preserved,
        source_SHA256=digest((definitions+body).encode()),ROM_mutation=False,
        live_abilities_IRQ_and_cold_proved=False)


def branch_proof(raw):
    """Every shortened branch, all incoming flags, actual continuation PCs."""
    from verify_native_relocation import NesMPU
    old,_=relink_core(raw);new,report=relink_core(raw,compact=True)
    mapping={value:new['symbols'][name]for name,value in old['symbols'].items()
             if name in new['symbols']and(name.startswith('KrFarSkip_')or re.fullmatch(r'Kr_[A-F0-9]+',name))}
    memories=[]
    for compiled in(old,new):
        m=bytearray(65536)
        for segment,(lo,hi)in dict(ACTOR_CORE=(0xa087,0xac06),WEAPON_CORE=(0xac06,0xafa4),CLEAR_CORE=(0xafa4,0xafbb)).items():
            body=compiled['images'][segment]
            m[lo:hi]=body.ljust(hi-lo,b'\xea')
        memories.append(m)
    cpus=[NesMPU(memory=m)for m in memories]
    cases=0;minimum_saving=100;maximum_saving=-100
    for pc in new['shortened']:
        destination=memories[0][pc+3]+256*memories[0][pc+4]
        assert pc in mapping and pc+5 in mapping and destination in mapping
        for flags in range(256):
            for c,start in zip(cpus,(pc,mapping[pc])):
                c.pc,c.a,c.x,c.y,c.p,c.sp=start,flags^85,(flags*3)&255,255-flags,flags,224
                c.processorCycles=0
            cpus[0].step()
            if cpus[0].pc==pc+2:cpus[0].step()
            cpus[1].step()
            assert cpus[0].pc in(pc+5,destination)
            assert cpus[1].pc==mapping[cpus[0].pc],(pc,flags,cpus[0].pc,cpus[1].pc)
            assert all(getattr(cpus[0],n)==getattr(cpus[1],n)for n in('a','x','y','p','sp'))
            saving=cpus[0].processorCycles-cpus[1].processorCycles
            minimum_saving=min(minimum_saving,saving);maximum_saving=max(maximum_saving,saving)
            cases+=1
    return dict(standalone=True,current_source_baseline_exact=True,branches=len(new['shortened']),
        incoming_status_values=256,cases=cases,AXYP_SP_and_taken_or_fallthrough_continuations_exact=True,
        cycle_saving_range=(minimum_saving,maximum_saving),compiled=report,
        full_host_abilities_IRQ_and_cold_proved=False)


def reference_proof(raw,*,include_code=False):
    """Reach actual owning code from all services, respecting inline tables."""
    import check_karnov_bomb_1112 as Cpu
    from verify_native_relocation import NesMPU
    b=Cpu.Cpu.Flower.Host.C.Start.W.bundle(raw)
    address=lambda n:Cpu.M.address(b,n)
    spans=((0xa000,0xbfe0,'actor'),(0xc900,0xce00,'combat'),(0xd600,0xde00,'options'))
    def owned(pc):return next((role for lo,hi,role in spans if lo<=pc<hi),None)
    def read(pc):
        role=owned(pc);assert role is not None,hex(pc)
        page,_,origin=Bomb.OWNED[role]
        return raw[Bomb.CHR+page*1024+pc-origin]
    tables={address(name):count for name,count in dict(Kr_F29B=32,Kr_F326=8,Kr_F723=16,Kr_F7DD=16,
        Kr_AAB6=9,Kr_AC0F=4,Kr_AC48=8,Kr_EAD5=9,Kr_ADCB=8).items()}
    sizes=dict(imp=1,acc=1,imm=2,zpg=2,zpx=2,zpy=2,inx=2,iny=2,rel=2,abs=3,abx=3,aby=3,ind=3)
    todo=[0xa000+3*i for i in range(37)];seen=set();inbound=[];data_refs=[];indirect=[];dispatches=[]
    decode=NesMPU().disassemble;decoded=[]
    while todo:
        pc=todo.pop()
        if pc in seen or owned(pc)is None:continue
        seen.add(pc);op,mode=decode[read(pc)]
        assert op!='BRK',(hex(pc),owned(pc))
        size=sizes[mode]
        operand=read(pc+1)+(256*read(pc+2)if size==3 else 0)if size>1 else None
        decoded.append((pc,owned(pc),op,mode,operand))
        core=0xa087<=pc<0xafbb
        if op in('JSR','JMP')and mode=='abs':
            if not core and 0xa087<=operand<0xafbb:inbound.append((pc,operand))
            if op=='JSR'and operand==address('KrInlineDispatch'):
                assert pc in tables,('Unbound inline dispatcher',hex(pc))
                count=tables[pc];dispatches.append((pc,count))
                for i in range(count):
                    at=pc+3+2*i;todo.append(read(at)+256*read(at+1))
                continue
            todo.append(operand)
            if op=='JMP':continue
        elif mode=='rel':todo.append((pc+2+(operand if operand<128 else operand-256))&65535)
        elif op=='JMP'and mode=='ind':
            indirect.append(pc);continue
        elif size==3 and not core and 0xa087<=operand<0xafbb:data_refs.append((pc,op,operand))
        if op not in('RTS','RTI'):todo.append(pc+size)
    anchors={address(n)for n in('Kr_F28D','Kr_AAB2','Kr_C2B7')}
    assert all(dest in anchors for _,dest in inbound),inbound
    assert not data_refs and not indirect,(data_refs,indirect)
    report=dict(actual_reached_instructions=len(seen),all37_service_roots=True,
        inline_dispatches=dispatches,external_core_calls=inbound,no_external_core_absolute_data_refs=True,
        no_unbound_indirect_control=True,immediate_SMC_scope='--part smc',
        actual_native_ingress_scope='check_karnov_equipment_1113.py --part entries')
    return(report,decoded)if include_code else report


def smc_proof(raw):
    """Bound the direct immediate far-call form; classify foreign owners."""
    import check_karnov_bomb_1112 as Cpu
    b=Cpu.Cpu.Flower.Host.C.Start.W.bundle(raw)
    # Actual fixed ABI: two immediate target bytes, bank3, FarCallCommon.
    pattern=rb'\xa9(.)\x8d\x6c\x01\xa9(.)\x8d\x6d\x01\xa9\x03[\x20\x4c]\x5a\x01'
    found=[]
    for hit in re.finditer(pattern,raw[16:Bomb.CHR],re.S):
        pc=hit[1][0]+256*hit[2][0]
        if not 0xa087<=pc<0xafbb:continue
        at=16+hit.start();owners=[]
        for segment in b['segs'].values():
            lo=int(segment.get('ooffs','0'),0);size=int(segment.get('size','0'),0)
            if lo<=at<lo+size:owners.append(segment['name'].strip('"'))
        found.append(dict(file_offset=at,target=pc,segments=sorted(set(owners))))
    assert len(found)==2,found
    assert found[0]['file_offset']==696154 and found[0]['target']==0xa200
    assert 'ROGUE_RELOC_PAGE_3'in found[0]['segments']
    assert found[1]['file_offset']==765847 and found[1]['target']==0xae06
    # The second literal is in the exact native Battletoads acquisition stub.
    lo=Cpu.M.location(b,'BtAcquire');hi=Cpu.M.location(b,'BtAcquireDone')
    assert lo<=found[1]['file_offset']<hi
    found[1]['symbol_owner']='BtAcquire'
    with zipfile.ZipFile(PACKET)as z:
        resident=z.read('host/kr-resident.inc').decode()
        route=z.read('host/kr-pickup-rom-route-v4.inc').decode()
        assert 'cmp #111'in resident and 'sbc #<KrServiceVeneers'in resident
        assert 'adc #<KrCacheServices'in route and 'lda #>KrCacheServices'in route
        assert 'KrPickupPrepareDirect:'in route
    return dict(conventional_immediate_bank3_farcall_matches=found,
        both_matches_are_foreign_owners=True,own_native_dispatch_is_typed_A000_plus_row=True,
        all37_dynamic_ingress_checked_separately=True,
        scope='Exact conventional immediate SMC form plus owning source/typed ingress; not arbitrary-byte disassembly')


def ladder_scene_proof(donor):
    """Original dispatcher/ownership only; background worker explicitly stubbed."""
    from verify_native_relocation import NesMPU
    def memory():
        m=bytearray(65536)
        m[0xc000:]=donor[16+14*8192:]
        m[0xa000:0xc000]=donor[16+12*8192:16+13*8192]
        return m
    original=memory()
    targets={i:int.from_bytes(original[0xd5f5+2*i:0xd5f7+2*i],'little')for i in(1,2,11)}
    assert targets=={1:0xd6ea,2:0xd6f8,11:0xdaf8}
    rows=[]
    for scene in(1,2,11):
        m=memory()
        for at,value in{0x5e:scene,0x624:1,0x625:128,0x626:32,0x8e:255,0x8f:0,
                0x71f:3,0x63:160,0x64:144,0x6b0:0}.items():m[at]=value
        # Stage restoration/VRAM is not part of this dispatch/owner check.
        for pc in(0xa003,0xa006,0xdf61,0xc534):m[pc]=0x60
        c=NesMPU(memory=m,pc=0xd5f0);c.sp=224;c.p=0x21
        path=[]
        for _ in range(200):
            if c.pc==0xc046:break
            if c.pc in(targets[scene],0xa003,0xa006,0xd700,0xdb00):path.append(c.pc)
            assert m[c.pc]!=0,('Donor dispatch BRK',scene,hex(c.pc))
            c.step()
        else:raise AssertionError(('Donor dispatch bound',scene,hex(c.pc)))
        assert c.sp==224
        if scene==1:assert path==[0xd6ea,0xa003]and m[0x5e]==1
        elif scene==2:
            assert path==[0xd6f8,0xa006,0xd700]
            assert(m[0x624],m[0x625],m[0x626],m[0x8f]&4,m[0x8e],m[0x5e])==(0,0,0,4,2,3)
        else:
            assert path==[0xdaf8,0xa006,0xdb00]
            assert(m[0x624],m[0x625],m[0x626],m[0x8f]&4,m[0x5e])==(0,160,136,0,1)
        rows.append(dict(scene=scene,actual_dispatch_target=targets[scene],path=path,
            returned_scene=m[0x5e],owned=m[0x8f],anchor=(m[0x625],m[0x626])))
    m=memory()
    for at,value in{0x62:10,0x63:128,0x64:200,0x1b:32,0x89:9,0x8b:2,
            0x6b0:0,0x5e:3,0x71f:0,0xc4:0}.items():m[at]=value
    c=NesMPU(memory=m,pc=0xf623);c.p=0x21;c.sp=224
    for _ in range(100):
        if c.pc==0xf6a0:break
        assert m[c.pc]!=0,('Donor bottom-climb BRK',hex(c.pc));c.step()
    else:raise AssertionError(('Donor bottom-climb bound',hex(c.pc)))
    assert(m[0x5e],m[0x71f])==(2,3)
    return dict(actual_fixed_dispatch_and_owner_paths=rows,original_held_Down_at_bottom_sets_scene2=True,
        source_actor_entry=0xf623,source_scene_writer=0xf69e,declared_collision_fields={0x89:9,0x8b:2},
        background_workers_stubbed=True,native_SMB_Ladder_claim=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--part',choices=('members','donor','footprint','renderer-plan','renderer-proof','relink-plan','relink','branches','references','smc','ladder-scenes'),default='members')
    args=p.parse_args()
    raw,donor=inputs()
    result={'members':members,'footprint':lambda:footprint(raw),'donor':lambda:donor_ladder(donor),
            'renderer-plan':lambda:renderer_plan(raw,donor),'renderer-proof':lambda:renderer_proof(raw,donor),
            'relink-plan':lambda:relink_plan(raw),
            'relink':lambda:{'baseline':relink_core(raw)[1],'compact':relink_core(raw,compact=True)[1]},
            'branches':lambda:branch_proof(raw),'references':lambda:reference_proof(raw),'smc':lambda:smc_proof(raw),
            'ladder-scenes':lambda:ladder_scene_proof(donor)}[args.part]()
    print(json.dumps(dict(ROM_SHA256=digest(raw),donor_SHA256=digest(donor),part=args.part,
        output_files=0,ROM_modified=False,result=result)),flush=True)
