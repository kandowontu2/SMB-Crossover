"""Zero-output exact-current Quick material/cold and source ABI qualification."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from py65.devices.mpu6502 import MPU

import check_quick_powerups_current_1113 as Q
import compose_quick_climb_material_1113 as T

N,W,L=Q.N,Q.W,Q.L


def cold(raw,cookie):
    bundle=W.Symbols.bundle();bundle['raw']=raw
    opening,m=Q.C.cold(bundle,Q.ROW)
    stream=raw[T.STREAM:T.STREAM+T.COPY_CODE+T.COPY_DATA]
    assert bytes(m.ram[1][:T.COPY_CODE])==stream[:T.COPY_CODE]
    assert bytes(m.ram[2][:T.COPY_DATA])==stream[T.COPY_CODE:]
    assert bytes(m.ram[2][0x1fe0:0x1ff0])==cookie
    assert all(N.get(m,name)==40 for name in ('QmField_06C0','QmField_0099'))
    return opening,m


def mask_matrix():
    mem=bytearray(65536);body=T.code()['CLIMB_MASK'];mem[T.HELPER:T.HELPER+len(body)]=body
    count=0
    for attr in range(256):
        for flags in range(256):
            c=MPU(memory=mem,pc=T.HELPER);c.a,c.x,c.y,c.p,c.sp=attr,71,83,flags|0x30,253
            mem[0x1fe:0x200]=b'\xfe\x7f'
            while c.pc!=0x7fff:c.step()
            assert c.a==int(attr&3==1) and (c.x,c.y,c.sp)==(71,83,255)
            assert c.p==flags|0x30,(attr,flags,c.p)
            count+=1
    return dict(all_attribute_flag_cases=count,AXYP_except_declared_material_A_exact=True,
        B_U_normalization='Actual PHP/PLP hardware representation; input P normalized with30hex.',bytes=body.hex())


def flat_world(raw):
    mem=bytearray(65536)
    mem[0x8000:0xa000]=raw[16+126*8192:16+127*8192]
    mem[0xe000:]=raw[16+127*8192:16+128*8192]
    mem[0xa000:0xbc00]=raw[T.STREAM:T.STREAM+T.COPY_CODE]
    return mem


def world_matrix(parent,candidate):
    b=W.Symbols.bundle();field={n:W.address(b,n)for n in ('R0','R1','R6','R7','QuickManWork_00','QuickManWork_0A','QuickManWork_0B','QuickManWork_0C')}
    table=parent[W.location(b,'BlockBufferAddr'):W.location(b,'BlockBufferAddr')+4]
    attrs=parent[W.location(b,'MTileAttribute'):W.location(b,'MTileAttribute')+256]
    old,new=flat_world(parent),flat_world(candidate);pc=W.address(b,'QuickManWorldProbe')
    def one(mem,tile,y,high,flags):
        # Source worldX3169 selects even page, column6 in the real block buffer.
        for n,v in dict(R0=97,R1=12,R6=0x5d,R7=0xd5,QuickManWork_00=0xa5,
            QuickManWork_0A=y,QuickManWork_0B=high,QuickManWork_0C=0x69).items():mem[field[n]]=v
        effective=y if high==0 else 0 if high&128 else 240
        if 32<=effective<240:
            base=table[0]+256*table[2];mem[base+6+(effective&240)-32]=tile
        mem[0x1fe:0x200]=b'\xfe\x7f'
        c=MPU(memory=mem,pc=pc);c.a,c.x,c.y,c.p,c.sp=0x53,71,83,flags,253
        steps=0
        while c.pc!=0x7fff:c.step();steps+=1;assert steps<150
        result=(c.a,c.x,c.y,c.p,c.sp,*(mem[field[n]]for n in ('R0','R1','R6','R7','QuickManWork_0A','QuickManWork_0B','QuickManWork_0C')))
        return mem[field['QuickManWork_00']],result,c.processorCycles,effective
    count=changed=0;delta=set()
    selected_y=(0,31,32,33,127,128,159,160,187,204,239,240,255)
    for tile in range(256):
        for high in (0,1,255):
            for y in selected_y:
                for flags in (0x30,0x31,0xf0,0xf1):
                    a=one(old,tile,y,high,flags);z=one(new,tile,y,high,flags)
                    valid=32<=a[3]<240
                    assert a[0]==int(valid and attrs[tile]&1)
                    assert z[0]==int(valid and attrs[tile]&3==1)
                    assert a[1]==z[1],(tile,y,high,flags,a,z)
                    if a[0]!=z[0]:assert attrs[tile]&2;changed+=1
                    delta.add(z[2]-a[2]);count+=1
    # Every signed source-Y combination, including both overflow directions.
    signed=0
    for y in range(256):
        for high in (0,1,127,128,255):
            for tile in (0,0x24,0x25,0x26,0x51,0x61):
                a=one(old,tile,y,high,0x71);z=one(new,tile,y,high,0x71)
                assert a[1]==z[1]
                assert z[0]==int(32<=z[3]<240 and attrs[tile]&3==1)
                signed+=1
    code=parent[T.STREAM:T.STREAM+T.CODE_SIZE]
    call=b'\x20'+pc.to_bytes(2,'little')
    callers=[0xa000+i for i in range(len(code)-2)if code[i:i+3]==call]
    assert callers and all(at<T.HELPER for at in callers)
    tail_symbols=[]
    for name in b['syms']:
        if name.startswith(('Qh','Qm','QuickMan','CX_')):
            at=W.address(b,name)
            if T.HELPER<=at<0xbc00:tail_symbols.append((name,at))
    assert not tail_symbols,tail_symbols
    return dict(actual_native_tile_flag_cases=count,signed_Y_cases=signed,
        declared_climb_material_changes=changed,all_other_fields_and_AXYP_SP_exact=True,
        CPU_cycle_deltas=sorted(delta),direct_source_callers=[f'{at:04X}'for at in callers],
        old_tail_has_no_source_symbols=True,old_tail_fill_bytes=T.COPY_CODE-T.CODE_SIZE,
        growth_within_existing_copy=11,allocation_growth=0)


def foreign(parent,candidate):
    rows=[];names=('HuMovement','HuHead','HuSide','HuFresh','HuPickup')
    for owner in range(44):
        # All foreign identity selector paths, plus both non-Quick raw9 forms.
        for alt in ((0,16)if owner==9 else(0,)):
            for name in names:
                pair=[]
                for seed in (parent,candidate):
                    m=L.clone(seed);N.put(m,SelectedCharacter=owner,FmAlts=alt)
                    before=tuple(bytes(bank)for bank in m.ram)
                    result=N.invoke(m,name,a=2,x=5,y=3,p=0x61)
                    delta=[(bank,i,a,z)for bank,(old,new)in enumerate(zip(before,m.ram))
                        for i,(a,z)in enumerate(zip(old,new))if a!=z]
                    pair.append((tuple(result[k]for k in ('A','X','Y','P')),delta,tuple(m.rawtags),
                        bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000])))
                assert pair[0]==pair[1],(owner,alt,name)
                rows.append((owner,alt,name))
    return dict(public_foreign_callback_pairs=len(rows),owners=44,raw9_Bass_Roll_included=True,
        actual_AXYP_native_fields_WRAM_write_deltas_maps_exact=True,
        scope='Foreign public identity selectors on declared warm Quick cache clones; foreign cold owner gameplay is separate.')


def interrupts(seed):
    import check_metal_head_bridge_1112 as Async
    samples=[];points=set()
    m=L.clone(seed);N.put(m,NmiDisable=255,FamilyMainCommit=1,GamePauseStatus=0,
        Player_Y_Position=176,Player_Y_HighPos=1,SavedJoypadBits=1,SavedJoypad1Bits=1)
    def observe(memory,cpu):
        own=memory.rawtags[1]==1 and (0xb165<=cpu.pc<0xb1c0 or T.HELPER<=cpu.pc<T.HELPER+11)
        if own and (cpu.pc,cpu.sp,cpu.p&4)not in points:
            points.add((cpu.pc,cpu.sp,cpu.p&4));q,c=L.clone(memory,cpu);samples.append((q,c))
    L.call(m,'HuMovement',a=0x53,x=7,y=91,p=0x21,observe=observe)
    assert any(T.HELPER<=c.pc<T.HELPER+11 for _,c in samples)
    counts=Counter();minimum=255
    for state,c in samples:
        for kind in ('IRQ','lagNMI'):
            if kind=='IRQ'and c.p&4:continue
            q,d=L.clone(state,c)
            minimum=min(minimum,Async.inject(d,N.NesMPU,kind));counts[kind]+=1
            # Complete the interrupted real public call, not only the ISR.
            L.finish(q,d,(0x5b00,224))
            assert q.rawtags==m.rawtags and Q.player(q)==Q.player(m)
            assert bytes(q.ram[1])==bytes(m.ram[1]) and bytes(q.ram[2])==bytes(m.ram[2])
    assert counts['IRQ']and counts['lagNMI']and minimum>=128
    return dict(cuts=dict(counts),unique_instruction_SP_points=len(samples),minimum_SP=minimum,
        actual_native_vectors=True,full_HuMovement_return_matches_uninterrupted=True,
        code_and_data_readonly=True)


def reload(seed,fault=False,cuts=False):
    import check_metal_head_bridge_1112 as Async
    m=L.clone(seed);N.put(m,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255,FamilyMainCommit=1)
    m.ram[2][0x1fe0]=0;m.ram[1][:]=bytes([0x69])*8192;m.ram[2][:2048]=bytes([0x96])*2048
    before=m.ppu_reads;samples=[];seen=set();entered=[]
    if fault:
        original=type(m)
        class Fault(original):
            def __getitem__(self,at):
                value=original.__getitem__(self,at)
                if isinstance(at,int)and at==T.HELPER and self.rawtags[1]==1 and value==8 and not self.failed:
                    self.failed=True;return value^1
                return value
        m.__class__=Fault;m.failed=False
    def observe(memory,cpu):
        if cpu.pc>=0x8000 and memory.rawtags[(cpu.pc-0x8000)//8192]==1:
            assert bytes(memory.ram[2][0x1fe0:0x1ff0])==memory.bundle['raw'][T.COOKIE_SITES[0]:T.COOKIE_SITES[0]+16]
            entered.append(cpu.pc)
        if cuts:
            ptr=N.get(memory,'R0')+256*N.get(memory,'R1')+cpu.y
            op=bytes(memory[cpu.pc:cpu.pc+3])
            kind='copy_helper'if ptr==T.HELPER and op[:2]==b'\x91\x03'else \
                'verify_helper'if ptr==T.HELPER and op[:2]==b'\xd1\x03'else \
                'publish_ready'if op==b'\x8d\xe0\xbf'and cpu.a==0xa7 else None
            if kind and kind not in seen:
                seen.add(kind);q,c=L.clone(memory,cpu);samples.append((kind,q,c))
    c=L.call(m,'QwConstruct',a=0x53,x=7,y=91,p=0x21,observe=observe)
    if fault:
        assert m.failed and not c.p&1 and not entered and not m.ram[2][0x1fe0]
        return dict(new_helper_readback_fault_detected=True,ready_unpublished=True,
            source_execution_before_verify=False,PPU_reads=m.ppu_reads-before)
    stream=m.bundle['raw'][T.STREAM:T.STREAM+9216]
    assert bytes(m.ram[1][:7168])==stream[:7168]and bytes(m.ram[2][:2048])==stream[7168:]
    assert m.ppu_reads-before==18450
    proof=[];minimum=255
    for name,state,cpu in samples:
        assert cpu.p&4,('Cold IRQ must remain masked',name)
        q,d=L.clone(state,cpu);minimum=min(minimum,Async.inject(d,N.NesMPU,'lagNMI'))
        L.finish(q,d,(0x5b00,224))
        assert q.rawtags==m.rawtags and Q.player(q)==Q.player(m)
        assert bytes(q.ram[1])==bytes(m.ram[1])and bytes(q.ram[2])==bytes(m.ram[2])
        proof.append(name)
    if cuts:assert set(proof)=={'copy_helper','verify_helper','publish_ready'},proof
    return dict(PPU_reads=m.ppu_reads-before,complete_code_data_readback=True,
        lag_NMI_cuts=proof,cold_IRQ_masked_points=len(samples),minimum_ISR_SP=minimum,
        verify_before_source_execution=bool(entered))


def gates(seed):
    rows=[]
    for mask,screen,lag in ((24,1,255),(0,0,255),(0,1,0)):
        m=L.clone(seed);N.put(m,Mirror_PPUMASK=mask,DisableScreenFlag=screen,NmiDisable=lag)
        m.ram[2][0x1fe0]=0;before=m.ppu_reads;seen=[]
        def watch(memory,cpu):
            if cpu.pc>=32768 and memory.rawtags[(cpu.pc-32768)//8192]==1:seen.append(cpu.pc)
        c=L.call(m,'QwConstruct',p=0x21,observe=watch)
        assert not c.p&1 and m.ppu_reads==before and not seen and not m.ram[2][0x1fe0]
        rows.append(dict(mask=mask,screen_disabled=screen,lag_disabled=lag,rejected=True))
    m=L.clone(seed);m.ram[2][0x1fe0:0x1ff0]=T.OLD_COOKIE
    before=m.ppu_reads;seen=[]
    def watch(memory,cpu):
        if cpu.pc>=32768 and memory.rawtags[(cpu.pc-32768)//8192]==1:seen.append(cpu.pc)
    L.call(m,'HuMovement',p=0x21,observe=watch)
    assert m.ppu_reads==before and not seen
    return dict(cold_wrong_phase=rows,previous_version_rejected_before_RAM_execution=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--basic',action='store_true')
    ap.add_argument('--route',action='store_true');args=ap.parse_args()
    parent=Q.C.ROM.read_bytes();assert sha256(parent).hexdigest()==Q.PIN
    candidate,info=T.transform(parent);assert T.inverse(candidate)==parent
    print('QUICK_CLIMB_COMPOSITION '+json.dumps(info,separators=(',',':')),flush=True)
    print('QUICK_CLIMB_MASK '+json.dumps(mask_matrix(),separators=(',',':')),flush=True)
    print('QUICK_CLIMB_WORLD '+json.dumps(world_matrix(parent,candidate),separators=(',',':')),flush=True)
    opening,m=cold(candidate,bytes.fromhex(info['cookie']))
    print('QUICK_CLIMB_COLD '+json.dumps(dict(opening=opening,readback_code=7168,readback_data=2048,
        final=Q.player(m),cookie=info['cookie']),separators=(',',':')),flush=True)
    if not args.basic:
        _,old=cold(parent,T.OLD_COOKIE)
        print('QUICK_CLIMB_FOREIGN '+json.dumps(foreign(old,m),separators=(',',':')),flush=True)
        print('QUICK_CLIMB_INTERRUPTS '+json.dumps(interrupts(m),separators=(',',':')),flush=True)
        print('QUICK_CLIMB_COLD_FAULT '+json.dumps(reload(m,fault=True),separators=(',',':')),flush=True)
        print('QUICK_CLIMB_COLD_CUTS '+json.dumps(reload(m,cuts=True),separators=(',',':')),flush=True)
        print('QUICK_CLIMB_AUTH_GATES '+json.dumps(gates(m),separators=(',',':')),flush=True)
    if args.route:
        result=Q.route(m,candidate,4000,'full')
        print('QUICK_CLIMB_FULL_ROUTE '+json.dumps(result,separators=(',',':')),flush=True)
        assert result['passed']


if __name__=='__main__':main()
