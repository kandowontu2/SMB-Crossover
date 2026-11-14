"""Granted source-only hidden-head composition/probe/caller/ISR gates."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from py65.disassembler import Disassembler
from unittest.mock import patch

import compose_smb2_hidden_head_1114 as C
import check_smb2_flag_handoff_1113 as Family
import check_smb2_postbg_irq_1113 as ISR
import check_bub_current_budget_1113 as Frames

W,N=C.W,C.N


def inputs():
    raw=C.parent_image();image,info=C.proposal(raw)
    assert C.inverse(image)==raw
    return raw,image,info


def source():
    raw,image,info=inputs();public=C.public_image(raw)
    q=C.Measure.readers(public)
    _,_,_,_,old,new=C.Measure.recipe(public)
    bank=public[16+118*8192:16+119*8192]
    moved=set(info['relocated_internal_labels'])
    # Every literal JSR/JMP candidate in this component is conservatively
    # included, even data. Only source-owned probe branches enter its internals.
    internal=[]
    for i in range(8190):
        if bank[i]in(0x20,0x4c):
            target=int.from_bytes(bank[i+1:i+3],'little')
            if any(target==old[n]for n in moved):internal.append((0xa000+i,target))
    assert not internal,internal
    # Source symbol names occur only in the original probe or its measuring
    # recipes, never an exported alias in the actual global symbol table.
    bundle=dict(W.Symbols.bundle(),raw=public)
    assert all(n not in bundle['syms']for n in moved)
    for anchor in('S2FlagProbe','S2FlagSharedReturn'):
        assert old[anchor]==new[anchor]
    return dict(**info,passed=True,strict_inverse=True,
        moved_internal_label_external_literal_JSR_JMP=internal,
        moved_labels_not_exported=True,padding_source_and_readers=q,
        synthetic_units=C.Measure.units(public))


def trajectory():
    """Observe the unedited immediate chase through the first actual head."""
    import replay_smb2_hidden_oneup_1113 as Frozen
    raw,image,_=inputs();public=C.public_image(raw)
    text=Frozen.controller(public,0).replace(Frozen.PIN,C.CANDIDATE)
    assert sha256(text.encode()).hexdigest()=='44ec80022b626f10b1e5feff1e6cf3ca2bf2adef959fbd2b12013d064bc7692a'
    b=dict(W.Symbols.bundle(),raw=image)
    points={(W.address(b,n),((W.location(b,n)-16)//8192)|128):n for n in
            ('S2MainVelocity','S2MainWorld','NativeRarePlayerHeadCollisionCore','S2N8F7A')}
    rows=[];pending=[];active=False;post=0;iterations=0
    fields=('S2VY','S2AY','S2Air','S2Collision','Player_Y_Speed','Player_Y_Position','S2Y',
            'S2HeadY','S2Math0','BlockBounceTimer','S2Clock','FrameCounter')
    def record(m,c,event):
        if len(rows)<128:
            rows.append(dict(event=event,iteration=iterations,PC=c.pc,SP=c.sp,
                A=c.a,**{n:N.get(m,n)for n in fields}))
    def observe(m,c):
        nonlocal active
        for q in list(pending):
            if(c.pc,c.sp)==q[:2]:
                record(m,c,q[2]+' return');pending.remove(q)
        if c.pc<0x8000:return
        name=points.get((c.pc,m.rawtags[(c.pc-0x8000)//8192]))
        if name=='NativeRarePlayerHeadCollisionCore'and c.a==96:active=True
        if not active or not name:return
        record(m,c,name+' entry')
        if name!='S2N8F7A':
            sp=c.sp;pc=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
            pending.append((pc,(sp+2)&255,name))
    original=Frames.frame
    def frame(m,observe_unused=None,**kwargs):
        nonlocal iterations,post,active
        iterations+=1
        q=original(m,observe=observe,**kwargs)
        if active:
            record(m,type('AtReturn',(),dict(pc=0,sp=0,a=0))(),'Main return')
            post+=1
            if post>=18:active=False
        return q
    with patch.object(Frozen.OldReplay,'controller',lambda image,v,mode:text),patch.object(Frames,'frame',frame):
        q=Frozen.Runner.run_controller(image,0,'natural-hidden-oneup',1100)
    receipt=q.pop('receipt')or{}
    heads=[r for r in rows if r['event']=='NativeRarePlayerHeadCollisionCore entry']
    returns=[r for r in rows if r['event']=='NativeRarePlayerHeadCollisionCore return']
    velocities=[r for r in rows if r['event']=='S2MainVelocity return']
    assert len(heads)==len(returns)==1 and heads[0]['S2VY']==returns[0]['S2VY']==180
    assert returns[0]['Player_Y_Speed']==0
    assert velocities[0]['Player_Y_Speed']==251 and velocities[0]['S2VY']==180
    assert not any(r['event']=='S2N8F7A entry'for r in rows)
    return dict(passed=True,diagnostic_only=True,ROM_SHA256=C.CANDIDATE,
        controller_SHA256=sha256(text.encode()).hexdigest(),natural_scope_passed=q['passed'],
        retained_scope_failure=receipt.get('reason'),oneup=receipt.get('oneup'),trajectory=rows,
        source_VY_not_stopped_by_hidden_head=True,original_native_bump_zero_overwritten=True,
        original_source_ceiling_zero_path_not_entered=True,outputs=0,Mesen_run=False)


def probe():
    raw,image,info=inputs();seed=Family.cold(raw,0)
    seed.raw_page(1,246)
    memories=[]
    for rom in(raw,image):
        m=bytearray(list.__iter__(seed));m[0xa000:0xc000]=rom[16+118*8192:16+119*8192]
        # Fixed code/data used by real GetBlockBufferAddr are copied from the
        # genuine current fixed map. No callback or addressing stub is used.
        m[0xe000:]=rom[16+(seed.rawtags[3]&127)*8192:16+((seed.rawtags[3]&127)+1)*8192]
        memories.append(m)
    b=seed.bundle;addr={n:W.address(b,n)for n in('S2X','S2Y','S2Page','S2YPage','S2VY',
        'S2ProbeDirection','S2Math0','S2HeadX','S2HeadPage','S2HeadY','Block_Buffer_1')}
    cache=[addr[n]for n in('S2HeadX','S2HeadPage','S2HeadY')]
    base=addr['Block_Buffer_1'];counts=Counter();minimum=255
    def run(m,tile,owner,p,direction,vy,offset=6,x=112,y=112,page=0,ypage=0):
        m[base:base+416]=bytes([tile])*416
        for name,val in(('S2X',x),('S2Y',y),('S2Page',page),('S2YPage',ypage)):
            m[addr[name]+owner]=val
        for name,val in(('S2VY',vy),('S2ProbeDirection',direction),('S2Math0',77),
                         ('S2HeadX',11),('S2HeadPage',22),('S2HeadY',33)):
            m[addr[name]]=val
        m[0x100:0x200]=bytes(range(256))
        cpu=N.NesMPU(memory=m,pc=0xb128);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=37,owner,offset,p,224
        cpu.stPushWord(0xbeee);low=cpu.sp
        for _ in range(160):
            if(cpu.pc,cpu.sp)==(0xbeef,224):break
            low=min(low,cpu.sp);cpu.step()
        else:raise AssertionError(('Whole probe bound',tile,owner,p,direction,vy,hex(cpu.pc)))
        result=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc)
        # Snapshot every foreground/native RAM byte and the complete live
        # caller stack. Temporary stack cells below returned SP are dead.
        final=bytes(m[:0x100])+bytes(m[0x1e1:0x8000])
        return result,final,tuple(m[i]for i in cache),low
    def pair(tile,owner,p,direction,vy,**kw):
        nonlocal minimum
        a=run(memories[0],tile,owner,p,direction,vy,**kw)
        z=run(memories[1],tile,owner,p,direction,vy,**kw)
        assert a[0]==z[0],('Whole probe AXYP/SP/PC',tile,owner,p,direction,vy,a[0],z[0])
        minimum=min(minimum,a[3],z[3])
        eligible=tile==96 and owner==0 and vy>=128 and direction<2 and not kw
        if eligible:
            assert z[2]!=(11,22,33)and z[2][1]==0
            # Only these predeclared cache bytes may differ; no blanket mask
            # for source scratch, registers, peripheral or other RAM.
            aa=bytearray(a[1]);zz=bytearray(z[1])
            for at in cache:aa[at-225 if at>=0x1e1 else at]=zz[at-225 if at>=0x1e1 else at]
            assert aa==zz
            counts['intended_upward_player_hidden']+=1
        else:
            assert a[1]==z[1],('Whole probe RAM',tile,owner,p,direction,vy,kw)
            counts['exact_full_probe_pairs']+=1
        assert z[0][4]==224
    for tile in range(256):
        for owner in range(4):
            for direction in range(8):
                for vy in(0,128):
                    for p in(0,65,255):pair(tile,owner,p,direction,vy)
    print(json.dumps(dict(progress_full_probe=dict(counts))),flush=True)
    for tile in range(256):
        for p in range(256):pair(tile,p%4,p,(p//4)%8,128 if p&32 else 0)
    for tile in(0,0x23,0x24,0x25,0x26,0x54,0x60,0xc2,0xc3,0xff):
        for x,y,page,ypage in((0,0,0,0),(248,239,255,0),(255,32,1,0),(0,112,0,1),(248,16,255,255)):
            for offset in range(16):
                for p in(0,1,64,255):pair(tile,3,p,6,128,offset=offset,x=x,y=y,page=page,ypage=ypage)
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],counts=dict(counts),minimum_SP=minimum,
        all256_raw_tiles_all256_initial_P_values_covered=True,
        full_cartesian_tiles_owners0to3_directions0to7_VY0and128_P0_65_255=True,
        all_RAM_and_live_caller_stack_exact_except_declared_hidden_cache=True,
        source_GetBlockBufferAddr_executed_without_stub=True,
        synthetic_directed_probe_fixtures=True,gameplay_claim=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=('source','probe','trajectory'),default='source')
    args=p.parse_args();q=dict(source=source,probe=probe,trajectory=trajectory)[args.mode]()
    print(json.dumps(q,separators=(',',':')),flush=True)
