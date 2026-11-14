"""Exact Prepare source compaction and fitted two-span research layout.

No placement grant, packet mutation, NesBus overlay or ROM reconstruction.
"""
from hashlib import sha256
import json,re
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
from verify_native_relocation import NesMPU
import build_prince_worldmaterial_research_1114 as Build

PREPARE=0xc552
FIRST_FOOT=''' ldx PpQueryX
 ldy PpQueryX+1
 lda $c60f
 ; The higher-top comparison supplied C0: SBC5 subtracts6.
 sbc #5
 sta PpQueryX
 lda $c610
 sbc #0
 sta PpQueryX+1
 lda Top
 sta PpQueryY'''


def plan(raw):
    raw=Build.parent(raw);inspection=Build.Old.inspect(raw)
    assert inspection['rebuild_exact']
    packet=Build.Old.Packet.extract(raw);chunks=packet[1]
    mem=[0]*65536
    # The authenticated third stream is staged at C100 then copied80 decimal
    # bytes lower by cold finalization. These are LIVE CPU addresses.
    for origin,c in zip((0xa000,0xc800,0xc0b0),chunks):mem[origin:origin+len(c)]=c
    assert mem[PREPARE]==0x20 and mem[PREPARE+3]==0x20
    cell=int.from_bytes(bytes(mem[PREPARE+1:PREPARE+3]),'little')
    physical=int.from_bytes(bytes(mem[PREPARE+4:PREPARE+6]),'little')
    whole=Build.Old.SOURCE.read_text()
    old=whole.split('.segment "WORLD_GEOMETRY"',1)[1].split('.segment "WORLD_MATERIAL"',1)[0]
    old='Prepare:'+old.split('Prepare:',1)[1]
    _,symbols=Build.Old.source();symbols.update(Cell=cell,PpWorldPhysicalFoot=physical)
    rebuilt,old_labels,_=Build.assemble(old,symbols,origin=PREPARE,check_entries=False)
    end=PREPARE+len(rebuilt)
    assert bytes(mem[PREPARE:end])==rebuilt,('Prepare source mismatch',hex(end))
    # Shift A in place after signed subtraction; the old memory low field
    # is committed after the loop. X still finishes zero; Y is unchanged.
    before=''' lda Row
 sec
 sbc CurrentRow
 sta Offset
 ldx #0
 lda Offset
 bpl :+
 dex
:
 stx Offset+1
 ldx #6
ShiftRow:
 asl Offset
 rol Offset+1
 dex
 bne ShiftRow'''
    after=''' ldx #0
 lda Row
 sec
 sbc CurrentRow
 bpl :+
 dex
:
 stx Offset+1
 ldx #6
ShiftRow:
 asl a
 rol Offset+1
 dex
 bne ShiftRow
 sta Offset'''
    assert old.count(before)==1;new=old.replace(before,after)
    lo=new.index(' lda $c611\n clc\n adc Origin\n sta Baseline')
    hi=new.index(' lda CellX\n clc\n adc #24',lo)
    baseline=''' ; QueryFoot already includes signedDelta and the room offset.
 ; Actual signed7 projection gives Delta=-64..63, hence 3-Delta=-60..67.
 ldx #0
 lda #3
 sec
 sbc Delta
 bpl PositiveBaselineStep
 dex
PositiveBaselineStep:
 clc
 adc QueryFoot
 sta Baseline
 txa
 adc QueryFoot+1
 sta Baseline+1
 ; Preserve original Prepare X=0, before the unchanged final flag setter.
 ldx #0
'''
    new=new[:lo]+baseline+new[hi:]
    compact,_,_=Build.assemble(new,symbols,origin=PREPARE,check_entries=False)
    helper_PC=PREPARE+len(compact)
    helper=FIRST_FOOT+'\n rts\n'
    helper_code,_,_=Build.assemble(helper,symbols,origin=helper_PC,check_entries=False)
    text=Build.SOURCE.read_text();assert text.count(FIRST_FOOT)==1
    outlined=text.replace(FIRST_FOOT,' jsr FirstFoot')
    symbols.update(FirstFoot=helper_PC)
    world,world_labels,_=Build.assemble(outlined,symbols)
    # Literal external address candidates are reported, not silently treated
    # as instruction operands. Classification remains a placement gate.
    refs=[]
    for k,c in enumerate(chunks):
        origin=(0xa000,0xc800,0xc0b0)[k]
        for i in range(len(c)-1):
            target=int.from_bytes(c[i:i+2],'little');at=origin+i
            if PREPARE<=target<end and not(k==2 and PREPARE<=at<end):
                row=dict(stream=k,at=hex(at),target=hex(target),preceding_hex=c[max(0,i-1):i+2].hex())
                if at in(0xa318,0xa5e8):
                    assert bytes(mem[at:at+3])==bytes.fromhex('8dc5c6')
                    row['classification']='Opcode/operand overlap in STA C6C5'
                elif at==0xbdee:
                    assert bytes(mem[at-1:at+2])==bytes.fromhex('2052c5')
                    row['classification']='Only JSR public Prepare entry'
                elif at in(0xbfba,0xbfbd):
                    assert bytes(mem[at-1:at+2])==bytes.fromhex('b900c6'if at==0xbfba else'99b0c5')
                    row['classification']='Cold staging copy data operand, not a code ingress'
                elif 0xc800<=at<0xc800+478:
                    row['classification']='Immutable packed grid tag bytes: high format bits and metadata-relative low14 offset'
                elif 0xc800+478<=at<0xd46e:
                    row['classification']='Immutable packed pose record bytes; bounded metadata data consumer'
                elif at==0xd9c3:
                    assert bytes(mem[at:at+2])==bytes.fromhex('f0c5')
                    row['classification']='BEQ D98A opcode/relative offset overlap'
                else:raise AssertionError(('Unclassified Prepare reference',row))
                refs.append(row)
    tags=[int.from_bytes(chunks[1][i:i+2],'little')for i in range(0,478,2)]
    offsets=[t&0x3fff for t in tags if t!=65535]
    assert all(478<=i<0xd46e-0xc800 for i in offsets)
    # Rebuild the complete immediately preceding executable Cell, proving
    # its linear/relative fallthrough domain stops at public Prepare.
    cell_text=whole.split('.segment "WORLD_GEOMETRY"',1)[1].split('Prepare:',1)[0]
    cell_code,_,_=Build.assemble(cell_text,symbols,origin=cell,check_entries=False)
    assert cell+len(cell_code)==PREPARE and bytes(mem[cell:PREPARE])==cell_code
    d=Disassembler(MPU(memory=mem));pc=cell;cell_branches=[]
    while pc<PREPARE:
        size,instruction=d.instruction_at(pc)
        if mem[pc]&31==16:
            offset=mem[pc+1];target=pc+2+offset-(256 if offset&128 else 0)
            assert cell<=target<PREPARE
            cell_branches.append([hex(pc),hex(target)])
        pc+=size
    assert mem[PREPARE-1]==0x60
    # Cold executes the upper staging copy, not the later live code map.
    staged=[0]*65536;staged[0xc100:0xc100+len(chunks[2])]=chunks[2]
    cold_decoder=Disassembler(MPU(memory=staged));pc=0xc65f;cold=[]
    for _ in range(24):
        size,instruction=cold_decoder.instruction_at(pc)
        assert instruction!='???'
        cold.append([hex(pc),instruction])
        if staged[pc]&31==16:
            offset=staged[pc+1];target=pc+2+offset-(256 if offset&128 else 0)
            assert not PREPARE+80<=target<end+80
        if instruction.startswith('JMP'):
            assert not PREPARE+80<=int(instruction.split('$')[1],16)<end+80
            break
        pc+=size
    else:raise AssertionError('Cold prefix did not exit')
    # Direct writer census is coupled to the inherited full original-source
    # indexed/indirect exclusion of the exclusive C078..C0B0 fields.
    delta_writers=[]
    private_refs=[]
    retired={0xc08d,0xc093,0xc094,0xc096,0xc098,0xc09d,0xc09e,0xc0a0}
    for k,c in enumerate(chunks):
        origin=(0xa000,0xc800,0xc0b0)[k]
        for i in range(len(c)-2):
            if c[i:i+3]==bytes.fromhex('8d88c0'):
                pc=origin+i;delta_writers.append(dict(PC=hex(pc),previous_hex=c[max(0,i-6):i].hex()))
        for i in range(len(c)-1):
            target=int.from_bytes(c[i:i+2],'little');at=origin+i
            if target not in retired or(k==0 and Build.Old.START<=at<Build.Old.END):continue
            if k==1 and 0xc800<=at<0xd46e:kind='Immutable grid data; not CPU scratch operands'
            elif k==0 and 0xb400<=at<0xbae5:kind='Immutable source script data; inherited finite reader/command closure'
            elif k==0 and target==0xc08d and mem[at]==0x8d and mem[at+1]==0xc0 and mem[at+2]in(0xc4,0xc6):
                kind=f'Opcode/operand overlap in STA {mem[at+2]:02X}C0, not retired Floor'
            else:raise AssertionError(('Unclassified retired-field reference',hex(at),hex(target)))
            private_refs.append(dict(PC=hex(at),target=hex(target),classification=kind,nearby_hex=c[max(0,i-2):i+4].hex()))
    assert len(delta_writers)==2,delta_writers
    assert any(mem[int(r['PC'],16)-2:int(r['PC'],16)]==[0xa9,3]for r in delta_writers)
    return dict(raw=raw,symbols=symbols,original=rebuilt,original_text=old,
        prepare=compact,prepare_text=new,helper=helper_code,helper_text=helper,
        world=world,world_text=outlined,world_labels=world_labels,
        info=dict(parent_SHA256=sha256(raw).hexdigest(),
            source_SHA256=sha256(Build.SOURCE.read_bytes()).hexdigest(),
            Prepare_half_open=[hex(PREPARE),hex(end)],
            Prepare_decoded_stream=2,Prepare_decoded_half_open=[PREPARE-0xc0b0,end-0xc0b0],
            Prepare_preimage_SHA256=sha256(rebuilt).hexdigest(),
            Prepare_original_bytes=len(rebuilt),Prepare_compacted_bytes=len(compact),
            Prepare_compacted_SHA256=sha256(compact).hexdigest(),
            Prepare_new_envelope_SHA256=sha256(compact+helper_code).hexdigest(),
            FirstFoot_half_open=[hex(helper_PC),hex(helper_PC+len(helper_code))],
            FirstFoot_bytes=len(helper_code),FirstFoot_SHA256=sha256(helper_code).hexdigest(),
            tail_spare_bytes=len(rebuilt)-len(compact)-len(helper_code),
            WorldMaterial_bytes=len(world),WorldMaterial_SHA256=sha256(world).hexdigest(),
            WorldMaterial_half_open=[hex(Build.Old.START),hex(Build.Old.START+len(world))],
            World_envelope_bytes=449,World_envelope_SHA256=sha256(world+b'\xea'*(449-len(world))).hexdigest(),
            declared_World_entries=[hex(world_labels[q])for q in('PpWorldTile','PpWorldTileY')],
            initial_fit=len(world)<=449 and len(compact)+len(helper_code)<=len(rebuilt),
            Prepare_external_literal_candidates=refs,
            previous_Cell_half_open=[hex(cell),hex(PREPARE)],previous_Cell_rebuild_exact=True,
            previous_Cell_relative_branches=cell_branches,
            following_live_C606_to_C800='Original source state/data, outside executable slot; unchanged',
            cold_staging_Prepare_half_open=[hex(PREPARE+80),hex(end+80)],
            unchanged_cold_prefix=cold,
            immutable_grid_tag_count=len(tags),grid_absolute_data_range=[hex(0xc800+min(offsets)),hex(0xd46e)],
            direct_Delta_writers=delta_writers,
            retired_private_field_outside_literal_candidates=private_refs,
            inherited_original_source_exclusion='prince-executable-state-1102-v15.json: all original direct/indexed domains and finite indirect scripts exclude C078..C0B0; cold zero0 and constructor3 remain in signed7 domain',
            exact_old_Prepare_reconstruction=True,placement_granted=False,
            primitive_semantics_complete=False,outputs=0,Mesen=False))


def primitive(image,proposal):
    """Full Prepare ABI/field comparison, actual signed7 decoder primitives."""
    pattern=bytes.fromhex('0ac9806a8d88c0');hits=[]
    for first,last in((0xa000,0xbfdf),(0xc0b0,0xc606),(0xc800,0xdfcf)):
        data=bytes(image[first:last]);start=0
        while True:
            at=data.find(pattern,start)
            if at<0:break
            hits.append(first+at);start=at+1
    assert len(hits)==1,hits
    projected=[]
    for value in range(256):
        m=image.copy();c=NesMPU(memory=m,pc=hits[0]);c.a=value
        for _ in range(4):c.step()
        projected.append(m[0xc088]-256 if m[0xc088]&128 else m[0xc088])
    assert set(projected)==set(range(-64,64))
    mismatches=[];vectors=0;cost=[]
    def call(m,index,flags):
        c=NesMPU(memory=m,pc=PREPARE);c.a,c.x,c.y,c.p,c.sp=index,71,109,flags,224
        c.stPushWord(0x5ffe)
        for _ in range(3000):
            if(c.pc,c.sp)==(0x5fff,224):return [c.a,c.x,c.y,c.p,c.sp],c.processorCycles
            assert m[c.pc],('Prepare primitive BRK',hex(c.pc))
            c.step()
        raise AssertionError('Prepare primitive bound')
    for delta in range(-64,64):
     for j,index in enumerate((0,9,10,19,20,29,109,255)):
        seed=image.copy();seed[0xc088]=delta&255
        seed[0xc611]=(0,1,28,29,127,128,250,255)[j]
        seed[0xc08b]=(seed[0xc611]+(-17 if j&1 else 13))&255
        seed[0xc089]=(0,77,255)[j%3];seed[0xc08a]=(0,1,255)[(j+delta)%3]
        seed[0xc082]=(-3,-1,0,1,3)[(j+delta)%5];seed[0xc616]=(1,3,4,14)[j%4]
        seed[0xc07a]=(0,9)[j&1]
        query=(0,8,240,255,256,511,65528,65535)[j]
        seed[0xc078:0xc07a]=query.to_bytes(2,'little')
        old=seed.copy();new=seed.copy()
        replacement=proposal['prepare']+proposal['helper']
        new[PREPARE:PREPARE+len(replacement)]=replacement
        flags=(0x20,0x21,0x60,0x61,0x28,0x29,0x68,0x69)[(j+delta)%8]
        a,ca=call(old,index,flags);b,cb=call(new,index,flags)
        same=a==b and old[0xc078:0xc0a6]==new[0xc078:0xc0a6]and old[0xb369:0xb36d]==new[0xb369:0xb36d]
        if not same and len(mismatches)<4:mismatches.append(dict(delta=delta,index=index,old=a,new=b,
            changed_fields=[hex(k)for k in range(0xc078,0xc0a6)if old[k]!=new[k]]))
        vectors+=1;cost.append(cb-ca)
    return dict(actual_signed7_decoder_PC=hex(hits[0]),actual_decoder_cases=256,
        complete_Delta_domain=[min(projected),max(projected)],Prepare_ABI_vectors=vectors,
        Prepare_mismatch_examples=mismatches,Prepare_equivalence_passed=not mismatches,
        compared_fields=['all C078..C0A6','QueryX/QueryY','A/X/Y/P/SP'],
        cycles_delta=dict(minimum=min(cost),maximum=max(cost),total=sum(cost)))


if __name__=='__main__':
    import sys
    if '--inspect'in sys.argv or '--inspect-aliases'in sys.argv:
        raw=Build.Old.F.ROM.read_bytes()
        assert sha256(raw).hexdigest()in('82ec0446873b28af458e7686fec87938feaf798a0a893b44e4dccfd071ccfd63',Build.Old.F.PIN)
        cs=Build.Old.Packet.extract(raw)[1];m=[0]*65536
        for a,c in zip((0xa000,0xc800,0xc0b0),cs):m[a:a+len(c)]=c
        d=Disassembler(MPU(memory=m));pc=0xd98f if '--inspect-aliases'in sys.argv else PREPARE;out=[]
        for _ in range(80 if '--inspect-aliases'in sys.argv else 110):
            size,text=d.instruction_at(pc);out.append([hex(pc),text]);pc+=size
            if text=='RTS'and '--inspect-aliases'not in sys.argv:break
        print(json.dumps(dict(live_disassembly=out,mixed_words=[dict(PC=hex(a),hex=bytes(m[a:a+5]).hex())for a in(0xa318,0xa5e8,0xd9c1)],outputs=0)),flush=True)
    else:print(json.dumps(plan(Build.Old.F.ROM.read_bytes())['info'],separators=(',',':')),flush=True)
