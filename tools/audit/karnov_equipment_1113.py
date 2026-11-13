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


def digest(data):return sha256(data).hexdigest()


def inputs():
    raw=Bomb.NIGHTLY.read_bytes();donor=ROM.read_bytes()
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


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--part',choices=('members','donor','footprint','renderer-plan','renderer-proof','relink-plan'),default='members')
    args=p.parse_args()
    raw,donor=inputs()
    result={'members':members,'footprint':lambda:footprint(raw),'donor':lambda:donor_ladder(donor),
            'renderer-plan':lambda:renderer_plan(raw,donor),'renderer-proof':lambda:renderer_proof(raw,donor),
            'relink-plan':lambda:relink_plan(raw)}[args.part]()
    print(json.dumps(dict(ROM_SHA256=digest(raw),donor_SHA256=digest(donor),part=args.part,
        output_files=0,ROM_modified=False,result=result)),flush=True)
