"""Research-only measured DK component overlay; actual native ISR cuts.

Root authorized these1073 existing-span CPU overlays for component research.
No Main route, ROM, cookie update, cold admission or physical grant follows.
"""
from collections import Counter
import json

import measure_dkjr_floor_entry_fit_1114 as Fit
import check_dkjr_retire_lease_1113 as Lease

S,F,G=Fit.Indirect.S,Fit.Indirect.F,Fit.Indirect.G
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def run(*,inject=False):
    proposal,model=Fit.measure(include_model=True);symbols=model['proposed']['symbols']
    _,parent=F.load_inputs();raw,_=S.proposal(parent)
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    base=Q.mounted(seed,raw)
    base.raw_page(1,3);base.raw_page(2,2)
    N.put(base,CurrentBank=3,CurrentBankC=2)
    smc_operands={r['PC']-0xa000+off for r in model['original']['rows']if r['exact_current']for off in (23,24)}
    cold_smc_deltas=[]
    for row in proposal['fragments']:
        at=row['payload_offset'];size=row['bytes']
        before=bytes.fromhex(row['preimage_hex'])
        assert model['original']['body'][at:at+size]==before
        delta=[at+i for i,(a,b)in enumerate(zip(base.ram[3][at:at+size],before))if a!=b]
        assert set(delta)<=smc_operands,(row['role'],list(map(hex,delta)))
        cold_smc_deltas.extend(delta)
        base.ram[3][at:at+size]=bytes.fromhex(row['proposed_hex'])
    N.put(base,FamilyMainCommit=1,NmiDisable=255,OperMode=1,OperMode_Task=3,
        GameEngineSubroutine=8,TimerControl=0,DisableCollisionDet=0,JumpspringAnimCtrl=0,
        SwimmingFlag=0,PlayerEntranceCtrl=1,Player_State=0,Player_Y_HighPos=1,
        Player_Y_Position=176,Player_X_Position=9,Player_PageLoc=10,
        ScreenLeft_X_Pos=1,ScreenLeft_PageLoc=10,ScreenRight_X_Pos=0,ScreenRight_PageLoc=11,
        CurrentOAMOffset=32,GuestOamRotationActive=0)
    r=base.ram[2]
    for at,value in {0x4a:1,0x68:0,0x6b:4,0x6c:4,0x76:178,0x7b:24,0x8fe:2,
        0x434:0,0x435:1,0x436:10,0x437:0xd7,0x8f5:208,0x8db:4}.items():r[at]=value
    for i in range(4):
        at=0x210+8*i;y=194+8*(i//2);tile=2*i;x=8*(i&1)
        r[at:at+8]=bytes((y,tile,0x20,x,y+8,tile+1,0x20,x))
    for buffer in ('Block_Buffer_1','Block_Buffer_2'):
        at=W.address(base.bundle,buffer);base[at:at+208]=bytes(208)
    block1=W.address(base.bundle,'Block_Buffer_1');base[block1+176:block1+178]=bytes((0x54,0x54))
    emitted={i['pc']for i in model['proposed']['instructions']}
    fixtures=[]
    def add(name,entry,changes=(),a=85):fixtures.append((name,entry,list(changes),a))
    def addr(name):return W.address(base.bundle,name)
    add('context','MeasuredEndpointContext')
    for name,value in (('OperMode',0),('OperMode_Task',2),('GameEngineSubroutine',7),
        ('TimerControl',1),('DisableCollisionDet',1),('JumpspringAnimCtrl',1),
        ('SwimmingFlag',1),('Player_Y_HighPos',0)):
        add('context-'+name,'MeasuredEndpointContext',[(addr(name),value)])
    for at,value in ((0xc04a,2),(0xc068,1)):add('context-'+hex(at),'MeasuredEndpointContext',[(at,value)])
    for ready in (0,1,2):add('draw-admit'+str(ready),'MeasuredDrawAdmission',[(0xc8fe,ready)])
    add('draw-pending-air','MeasuredDrawAdmission',[(0xc8fe,1),(addr('Player_State'),2)])
    add('forced-drop','MeasuredForcedDrop',[(addr('Player_State'),2)])
    add('forced-other-entrance','MeasuredForcedDrop',[(addr('PlayerEntranceCtrl'),2)])
    pending_changes=[(0xc8fe,1),(addr('Player_State'),2),(addr('Player_Y_Position'),48),
        (0xc06b,1),(0xc06c,1),(0xc076,63)]
    add('entry-air','MeasuredAnchorReady',pending_changes)
    for ready in (0,2):add('entry'+str(ready),'MeasuredAnchorReady',[(0xc8fe,ready)])
    add('entry-normal','MeasuredAnchorReady',[(0xc8fe,1)])
    add('old-anchor-public',0xbfc1)
    add('entry-wrong-engine','MeasuredAnchorReady',[(0xc8fe,1),(addr('GameEngineSubroutine'),7)])
    add('entry-import-high-reject','MeasuredAnchorReady',[(0xc8fe,1),(addr('Player_Y_HighPos'),0)])
    add('floor','MeasuredAfterEffects')
    for at,value in ((0xc8fe,1),(0xc06b,1),(0x1e,2),(0xc437,0),(0xbd,224),(0xbd,175),(0x75,8),(0x75,233)):
        add('floor-'+hex(at)+'-'+str(value),'MeasuredAfterEffects',[(at,value)])
    add('floor-empty','MeasuredAfterEffects',[(block1+176,0),(block1+177,0)])
    add('floor-injury-limit','MeasuredAfterEffects',[(0xc076,160)])
    add('row34',0xa066)
    add('static','MeasuredStaticFloor')
    for at,value in ((0xbd,175),(0x75,8),(0x75,233),(0x5c,11)):
        add('static-'+hex(at)+'-'+str(value),'MeasuredStaticFloor',[(at,value)])
    add('static-empty','MeasuredStaticFloor',[(block1+176,0),(block1+177,0)])
    for ready in (0,1,2):add('body'+str(ready),0xbc74,[(0xc8fe,ready)])
    add('body-pending',0xbc74,pending_changes)
    for op in range(5):
        add('draw-op'+str(op),'D_ea08',[(0xc000,80),(0xc001,176),(0xc002,16),
            (0xc003,0x24),(0xc004,0x10),(0xc005,0x17)],op)
    add('fruit-empty','D_d955')
    add('fruit-guard','D_d955',[(0xc591,1)])
    add('fruit-hidden','D_d955',[(0xc08c,0),(0xc093,7),(0xc09a,0)])
    add('fruit-miss','D_d955',[(0xc08c,0),(0xc093,7),(0xc09a,1),
        (0xc091,0),(0xc092,4),(0xc401,200),(0xc402,40),
        (0xc03e,0),(0xc03f,180),(0xc040,31),(0xc041,207)])
    for count in (1,2,3,4):
        changes=[(0xc08c,0),(0xc093,7*count),(0xc091,0),(0xc092,4),
            (0xc03e,0),(0xc03f,180),(0xc040,31),(0xc041,207)]
        for slot in range(4):
            changes.extend(((0xc09a+slot,int(slot<count)),(0xc401+7*slot,8),
                (0xc402+7*slot,194),(0xc403+7*slot,0xa4)))
        add('fruit-count'+str(count),'D_d955',changes)
    # NMI can interrupt either incoming I state. IRQ is admitted only at
    # the hardware-enabled points; retain V1 in both caller status values.
    fixtures=[(*fixture,status)for status in (0x61,0x65)for fixture in fixtures]
    points={};references={};minimum=255;counts=Counter();changes_total=Counter()
    active=False;reads=set();writes=set();dead_stack=set()
    Base=type(base)
    class Tracked(Base):
        def __getitem__(self,at):
            if active and isinstance(at,int):
                if at in dead_stack:assert at in writes,('discarded ISR stack read before new writer',hex(at))
                reads.add(at)
            return super().__getitem__(at)
        def __setitem__(self,at,value):
            if active and isinstance(at,int):writes.add(at)
            return super().__setitem__(at,value)
    base.__class__=Tracked
    def execute(index,cut=None):
        nonlocal active,dead_stack
        active=False;dead_stack=set();reads.clear();writes.clear()
        name,entry,changes,a,incoming=fixtures[index];memory=L.clone(base)
        for at,value in changes:memory[at]=value
        if name=='body-pending':H.call(memory,symbols['MeasuredAnchorReady'],p=0x61)
        hit=False;low=255;changed=set()
        def observe(m,c):
            nonlocal hit,low,active,dead_stack,changed
            active=True
            if c.pc>=0x8000 and m.rawtags[(c.pc-0x8000)//8192]==3 and c.pc in emitted:
                token=(c.pc,c.p&4);points.setdefault(token,index)
                if cut and token==cut[1]and not hit:
                    active=False;before=bytes(m[:0x10000])
                    live=bytes(m[0x101+c.sp:0x200]);low,_=Lease.inject_checked(c,cut[0])
                    assert bytes(m[0x101+c.sp:0x200])==live,(name,cut,'live stack')
                    changed={at for at in range(0x10000)if m[at]!=before[at]}
                    dead_stack={at for at in changed if 0x100<=at<=0x100+c.sp}
                    reads.clear();writes.clear();active=True
                    hit=True
        c=H.call(memory,symbols[entry]if isinstance(entry,str)else entry,a=a,x=37,y=91,p=incoming,observe=observe)
        active=False
        assert hit==(cut is not None),(name,cut,hit)
        return memory,c,low,changed
    for i in range(len(fixtures)):references[i]=execute(i)[:2]
    def result(name):return references[next(i for i,f in enumerate(fixtures)if f[0]==name)][0]
    pending=result('body-pending');pending_y=[pending[0x200+i]for i in range(32,48,4)]
    assert all(32<=y<80 for y in pending_y),pending_y
    safe=result('floor');empty=result('floor-empty');injury=result('floor-injury-limit')
    assert(safe.ram[2][0x6b],safe.ram[2][0x210])==(1,191)
    assert(empty.ram[2][0x6b],empty.ram[2][0x210])==(4,194)
    assert(injury.ram[2][0x6b],injury.ram[2][0x210])==(5,194)
    air=result('entry-air')
    assert (air.ram[2][0x8fe],air.ram[2][0x6b],air.ram[2][0x6c],air.ram[2][0x76])==(1,1,1,63)
    assert air.ram[2][0x210]==N.get(air,'Player_Y_Position')+15
    expected_motion=bytearray(base.ram[2][0x6b:0x88])
    expected_motion[0]=expected_motion[1]=1;expected_motion[0x76-0x6b]=63
    assert bytes(air.ram[2][0x6b:0x88])==bytes(expected_motion)
    reached={pc for pc,_ in points};missing=sorted(emitted-reached)
    print('DKJR_FLOOR_ENTRY_VECTOR_COVERAGE '+json.dumps(dict(fixtures=len(fixtures),
        emitted=len(emitted),reached=len(reached),missing=[hex(pc)for pc in missing])),flush=True)
    if inject:
        for number,(point,index)in enumerate(list(points.items())):
            ref,rc=references[index]
            for kind in ('IRQ','lagNMI'):
                if kind=='IRQ'and point[1]:continue
                m,c,low,changed=execute(index,(kind,point));minimum=min(minimum,low)
                assert(c.a,c.x,c.y,c.p&0xef,c.sp,c.pc)==(rc.a,rc.x,rc.y,rc.p&0xef,rc.sp,rc.pc),(kind,point,'ABI')
                assert tuple(map(bytes,m.ram))==tuple(map(bytes,ref.ram)),(kind,point,'private RAM')
                assert m.rawtags==ref.rawtags and bytes(m[0x15a:0x17b])==bytes(ref[0x15a:0x17b]),(kind,point,'maps/SMC')
                assert bytes(m[0x200:0x300])==bytes(ref[0x200:0x300]),(kind,point,'OAM')
                assert bytes(m.vram)==bytes(ref.vram)and m.chr_latches==ref.chr_latches,(kind,point,'graphics')
                consumed={at for at in changed&reads if at<0x100 or 0x200<=at<0x800 or 0x5c00<=at<0x8000}
                assert not consumed,(kind,point,'foreground reads ISR-changed native data',sorted(consumed))
                changes_total.update(hex(at)for at in changed if not 0x100<=at<0x200)
                counts[kind]+=1
            if number%80==0:print('DKJR_FLOOR_ENTRY_VECTOR_PROGRESS '+json.dumps(dict(done=number+1,total=len(points))),flush=True)
    return dict(passed=not missing,all1073_serialized_preimages_authenticated=True,
        cold_constructor_live_deltas_only_original_SMC_operands=list(map(hex,cold_smc_deltas)),only_declared_CPU_overlay=True,
        ROM_composed=False,ordinary_Main_route=False,cookie_changed=False,cold_admission_claim=False,
        declared_fixtures=len(fixtures),emitted_instruction_PCs=len(emitted),reached=len(reached),missing=missing,
        cuts=dict(counts),minimum_ISR_SP=minimum if inject else None,
        actual_IRQ_busy_NMI_requested=inject,complete_live_stack_continuation_AXY_realP_SP_private_RAM_OAM_SMC_maps_graphics_equal=bool(inject),
        discarded_ISR_stack_reads_require_new_writer=bool(inject),
        ISR_native_changes_not_read_by_continuation=dict(changes_total),
        qualified_static_floor_safe_source_state_y=[1,191],no_static_floor_source_state_y=[4,194],
        ordinary_pre_snap_fall_damage_source_state_y=[5,194],pending_entry_OAM_Y=pending_y,
        pending_entry_ready_state_prior_origin_preserved=[1,1,1,63],pending_body_tracks_native_Y_plus15=True,
        pending_entry_all_original_state_fall_jump_fraction_impulse_fields_unchanged=True,
        both_incoming_interrupt_disable_states=True,incoming_V_set=True,
        outputs_written=0,physical_allocation_granted=False,native_claim=False)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--inject',action='store_true');args=p.parse_args()
    result=run(inject=args.inject)
    print('DKJR_FLOOR_ENTRY_VECTORS '+json.dumps(result,separators=(',',':')),flush=True)
