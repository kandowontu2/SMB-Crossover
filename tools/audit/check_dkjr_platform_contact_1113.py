"""Private native contact ABI/gameplay/cost checks; stdout and memory only."""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from unittest.mock import patch

import compose_dkjr_platform_contact_1113 as T
import check_dkjr_descending_contact_1113 as C
import check_dkjr_platform_contact_caller_1113 as Caller
import audit_current_roster_powerups_1110 as Roster
import check_roster_powerup_continuation_1110 as Frames

P,H,N,W,L=C.P,C.H,C.N,C.W,C.L


def entry(raw):
    at=16+0x143f
    assert raw[at]==0x20
    target=raw[at+1]|raw[at+2]<<8
    assert target in(0xb98e,T.ENTRY)
    return target


def mounted(seed,raw):
    m=L.clone(seed);m.bundle=dict(seed.bundle,raw=raw)
    return m


def direct(m,pc,*,a=85,x=3,y=91,p=0x31,observe=None):
    m.raw_page(1,128);N.put(m,CurrentBank=128)
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224
    c.stPushWord(0x5aff);minimum=c.sp
    for i in range(300000):
        if(c.pc,c.sp)==(0x5b00,224):break
        if observe:observe(c)
        minimum=min(minimum,c.sp)
        assert m[c.pc],('BRK',hex(c.pc),tuple(m.rawtags))
        c.step()
    else:raise AssertionError(('native CPU bound',hex(c.pc),c.sp))
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,CPU=c.processorCycles,minimum_SP=minimum)


def observables(m):
    native=bytearray(m[:0x800]);native[0x100:0x1df]=bytes(223)
    return (bytes(native),tuple(bytes(r)for r in m.ram),tuple(m.rawtags),
        bytes(m.vram),tuple(m.chr_latches))


def cost(seed,parent,candidate):
    rows=[]
    for owner,timer in product((4,9,10,15,16,22,23,25,37,40,41),(0,1)):
        pair=[]
        for raw in(parent,candidate):
            m=C.setup(mounted(seed,raw))
            N.put(m,SelectedCharacter=owner,TimerControl=timer,ObjectOffset=C.SLOT,
                Z2Variant=int(owner==4),RyuSourceBodyProfile=25)
            r=direct(m,entry(raw))
            pair.append((m,r))
        a,b=[r for _,r in pair]
        if owner!=40:
            assert (a['X'],a['Y'],a['SP'])==(b['X'],b['Y'],b['SP']),(owner,timer,a,b)
        rows.append(dict(owner=owner,timer=timer,parent_cycles=a['CPU'],candidate_cycles=b['CPU'],
            additional_cycles=b['CPU']-a['CPU'],parent_min_SP=a['minimum_SP'],candidate_min_SP=b['minimum_SP']))
    return rows


def incoming(seed):
    cases=0
    for slot,timer,scene in product((0,3,5),(0,1),('near','distant','hidden')):
        C.SLOT=slot;base=C.setup(seed)
        N.put(base,TimerControl=timer,ObjectOffset=slot)
        if scene=='distant':C.field(base,'Enemy_X_Position',200)
        if scene=='hidden':N.put(base,Player_Y_HighPos=2,Player_OffscreenBits=255)
        pair=[]
        for a,flags,id_flags in product((0,1,40,255),range(16),(0,4,8,12)):
            p=0x30|(flags&3)|((flags&4)<<4)|((flags&8)<<4)|id_flags
            m=L.clone(base);result=direct(m,0xb453,a=a,x=slot,p=p)
            assert result['P']&12==id_flags,(slot,timer,scene,a,hex(p),'incoming I/D')
            value=(observables(m),tuple(result[k]for k in('X','Y','SP')))
            if pair:assert value==pair[0],(slot,timer,scene,a,hex(p))
            else:pair.append(value)
            cases+=1
    return dict(cases=cases,actual_LPC_incoming_A_NZCV_dead=True,
        hidden_offscreen_and_timer_paths=True,returned_XY_SP_native_fields_all_WRAM_maps_equal=True,
        incoming_I_D_unchanged=True)


def compiled_contact(m,delta,_unused):
    box=bytes(m[0x658:0x65c]);N.put(m,ObjectOffset=C.SLOT)
    count=0;Base=N.NesMPU
    class Probe(Base):
        def step(self):
            nonlocal count
            if self.pc==0xac29 and self.memory.rawtags[1]==199:count+=1
            return Base.step(self)
    with patch.object(N,'NesMPU',Probe):
        direct(m,T.ENTRY,x=C.SLOT,a=0,y=0)
        flag=N.get(m,'PlatformCollisionFlag',C.SLOT)
        C.field(m,'Enemy_Y_Position',N.get(m,'Enemy_Y_Position',C.SLOT)+delta)
        if flag<128 and not count:N.invoke(m,'PositionPlayerOnVPlat',a=0,x=C.SLOT,y=0)
    assert bytes(m[0x658:0x65c])==box
    return dict(passenger=flag,native_position_calls=count)


def components(seed,candidate):
    compiled=mounted(seed,candidate);steps=0
    with patch.object(C,'native_contact',compiled_contact):
        for C.SLOT,deltas in product(range(6),((1,)*8,(0,)*8,(2,)*8,(-1,)*8,(-2,)*8,(1,2,0,-1,-2,0,2,1))):
            m,row=C.trajectory(compiled,True,deltas)
            assert len(row['steps'])==8
            for step in row['steps']:
                v=step['after_native']
                assert step['contact']==dict(passenger=C.SLOT,native_position_calls=1),(C.SLOT,deltas,step)
                assert (v['source'],v['prior'],v['fallStart'],v['fallLimit'])==(1,1,0,22)
                assert(v['nativeY'],v['sourceY'])==(v['top']-32,v['top']-17)
                steps+=1
        negatives=[]
        for C.SLOT in range(6):negatives+=C.negatives(compiled)
    clipping=0
    for C.SLOT,footer in product(range(6),range(256)):
        m=C.setup(compiled);m[0x65b]=footer
        event=compiled_contact(m,0,None)
        assert m[0x65b]==footer
        assert event['passenger']in(C.SLOT,255)
        clipping+=1
    return dict(compiled_positive_contact_updates=steps,compiled_jump_gap_highfall_negatives=len(negatives),
        exact_footer_restoration_all_bytes_slots=clipping,body_motor_donor_code_unchanged=True)


def native_ids(seed,parent,candidate):
    cases=0;new_contacts=0;existing_contacts=0;box_rows=set()
    for slot,kind,state,gap,side,dy in product((0,3,5),range(37,43),(0,1,64,128,255),
            (-32,-29,-27,-24,-10,-6,-5,-1,0,1,2,3,8),(-20,0,20),(0,255)):
        C.SLOT=slot;base=C.setup(seed);N.put(base,ObjectOffset=slot,Player_Y_Speed=dy)
        footer=base[0x65b];top=footer+gap
        C.field(base,'Enemy_ID',kind);C.field(base,'Enemy_State',state)
        C.field(base,'Enemy_Y_Position',top)
        C.field(base,'Enemy_X_Position',(944+side)&255)
        N.invoke(base,'GetEnemyOffscreenBits',x=slot)
        N.invoke(base,'RelativeEnemyPosition',x=slot)
        N.invoke(base,'LargePlatformBoundBox',x=slot)
        bbox=tuple(base[0x65c+4*slot:0x660+4*slot]);box_rows.add((kind,state,top,bbox[1]))
        if bbox[1]!=255:assert bbox[1]==top,(kind,state,top,bbox)
        outcomes=[]
        for raw in(parent,candidate):
            m=mounted(base,raw);m[0x16a]=85
            direct(m,entry(raw),x=slot)
            assert m[0x65b]==footer
            outcomes.append((N.get(m,'PlatformCollisionFlag',slot),bytes(m[0x200:0x800]),
                tuple(bytes(r)for r in m.ram),tuple(m.rawtags)))
        old,new=outcomes
        if old[0]==new[0]:
            assert new==old,(slot,kind,state,gap,side,dy,old[0],new[0])
            existing_contacts+=int(old[0]<128)
        if new[0]!=old[0]:
            assert old[0]==255 and new[0]==slot,(slot,kind,state,gap,side,dy,old[0],new[0])
            assert gap in(1,2)and dy==0 and state<128,(slot,kind,state,gap,side,dy)
            new_contacts+=1
        cases+=1
    balance=balance_pairs(seed,parent,candidate)
    return dict(actual_ID25_to2A_state_gap_side_jump_cases=cases,existing_contacts_preserved=existing_contacts,
        added_only_1_or2_pixel_downward_gap_contacts=new_contacts,
        actual_bbox_top_versus_EnemyY_cases=len(box_rows),paired_ID24_original_behavior_cases=balance,
        no_native_player_or_source_physics_geometry_change=True,
        scope='Directed native contact/actor fixtures. Complete-Main/SMC effects are checked separately.')


def balance_pairs(seed,parent,candidate):
    balance=0
    for slot,child,parent_top,child_top in product((0,3,5),range(6),(128,137,150),(128,137,150)):
        if slot==child:continue
        C.SLOT=slot;base=C.setup(seed);N.put(base,ObjectOffset=slot)
        for actor,top,left,state in((slot,parent_top,880,child),(child,child_top,944,255)):
            for field,value in dict(Enemy_ID=36,Enemy_Flag=1,Enemy_State=state,
                Enemy_Y_Position=top,Enemy_Y_HighPos=1,Enemy_X_Position=left&255,
                Enemy_PageLoc=left>>8,Enemy_BoundBoxCtrl=5).items():
                base[W.address(base.bundle,field)+actor]=value
            N.invoke(base,'GetEnemyOffscreenBits',x=actor)
            N.invoke(base,'RelativeEnemyPosition',x=actor)
            N.invoke(base,'LargePlatformBoundBox',x=actor)
        N.put(base,ObjectOffset=slot)
        pair=[]
        for raw in(parent,candidate):
            m=mounted(base,raw);m[0x16a]=85;r=direct(m,entry(raw),x=slot)
            pair.append((bytes(m[0x200:0x800]),tuple(bytes(q)for q in m.ram),tuple(m.rawtags),r['X'],r['Y'],r['SP']))
        assert pair[0]==pair[1],(slot,child,parent_top,child_top)
        balance+=1
    return balance


def route(seed,candidate,full=False):
    text=T.controller(candidate,full=full)
    m=mounted(seed,candidate)
    result=P.B.route(m,candidate,12000 if full else 2000,controller_text=text)
    assert result['passed'],result
    return dict(candidate_ROM_SHA256=T.PIN,controller_SHA256=sha256(text.encode()).hexdigest(),
        full=full,result=result)


def frame(m,pad,observe=None):
    m.controller_pad=pad;idle=W.address(m.bundle,'IdleLoop')
    W.clear_logs(m);N.consume(m)
    c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
    L.finish(m,c,(idle+12,252),observe=observe)
    assert not m.blocked
    m.contact_frame_registers=(c.a,c.x,c.y,c.p,c.sp,c.pc)
    return c.processorCycles


def foreign(parent,candidate):
    inventory=Roster.Starts.C.inventory(parent)['rows']
    targets=('MINI MARIO','LINK','ZELDA II LINK','RYU HAYABUSA','THOMAS','JAY MCCRAY',
        'FF FIGHTER','FF WHITE MAGE','FF BLACK MAGE','FF THIEF',
        next(r['name']for r in inventory if 'HOGAN'in r['name']))
    rows=[]
    for name in targets:
        row=next(r for r in inventory if r['name']==name)
        b=W.Symbols.bundle();b['raw']=parent
        opening,seed=Roster.cold(b,row)
        models=[mounted(seed,raw)for raw in(parent,candidate)]
        counts=[0,0];costs=[[],[]];discarded=[set(),set()];reads=[0,0]
        for index,m in enumerate(models):
            Base=type(m)
            class Tracked(Base):
                def __getitem__(self,at):
                    if isinstance(at,int)and at in self.contact_discarded:
                        assert at in self.contact_written,('discarded stack read before write',name,hex(at))
                        self.contact_reads+=1
                    return super().__getitem__(at)
                def __setitem__(self,at,value):
                    if isinstance(at,int):self.contact_written.add(at)
                    return super().__setitem__(at,value)
            m.__class__=Tracked;m.contact_discarded=set();m.contact_written=set();m.contact_reads=0
            # Explicit platform component inside a genuinely cold-constructed
            # foreign scene. Its ordinary 1-1 route remains a separate check.
            slot=3
            for actor in range(6):N.invoke(m,'EraseEnemyObject',x=actor)
            for field,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_State=0,
                Enemy_X_Position=N.get(m,'Player_X_Position'),Enemy_PageLoc=N.get(m,'Player_PageLoc'),
                Enemy_Y_Position=(N.get(m,'Player_Y_Position')+32)&255,Enemy_Y_HighPos=1).items():
                m[W.address(m.bundle,field)+slot]=value
            N.invoke(m,'InitEnemyObject',x=slot)
            m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+slot]=5
        for age in range(16):
            for index,m in enumerate(models):
                def observe(memory,cpu):
                    if cpu.pc==(T.ENTRY if index else 0xb98e)and memory.rawtags[1]==128:counts[index]+=1
                m.contact_written=set();m.contact_reads=0
                costs[index].append(frame(m,0 if age<8 else 1,observe))
                reads[index]+=m.contact_reads
            left,right=models
            diffs={at for at in range(0x800)if left[at]!=right[at]}
            stack={at for at in diffs if 0x17b<=at<0x1fd}
            assert diffs==stack,(name,age,'native nonstack differences',
                [(hex(at),left[at],right[at])for at in sorted(diffs-stack)][:20])
            assert tuple(bytes(r)for r in left.ram)==tuple(bytes(r)for r in right.ram),(name,age,'WRAM')
            assert left.contact_frame_registers==right.contact_frame_registers,(name,age,'Main returned AXYP/SP')
            assert bytes(left[0x5c00:0x8000])==bytes(right[0x5c00:0x8000]),(name,age,'SRAM')
            assert tuple(left.rawtags)==tuple(right.rawtags)
            assert bytes(left.vram)==bytes(right.vram)and tuple(left.chr_latches)==tuple(right.chr_latches)
            for index,m in enumerate(models):
                m.contact_discarded|=stack;discarded[index]|=stack
        assert counts[0]==counts[1]and counts[1]>=8,(name,counts)
        rows.append(dict(name=name,raw=row['raw'],cycle=row['cycle'],actual_Main_updates=16,
            platform_dispatches=counts,cycles_parent=sum(costs[0]),cycles_candidate=sum(costs[1]),
            max_frame_cycles_parent=max(costs[0]),max_frame_cycles_candidate=max(costs[1]),
            additional_frame_cycles=sorted(set(b-a for a,b in zip(*costs))),
            stack_differences_proven_reader_after_writer=len(discarded[0]),
            subsequent_stack_reads_checked=reads,complete_WRAM_native_nonstack_SMC_maps_graphics_equal=True))
        print('DKJR_PLATFORM_FOREIGN_ROW '+json.dumps(rows[-1],separators=(',',':')),flush=True)
    return dict(rows=rows,scope='Actual foreign cold/menu/opening followed by declared native platform fixture and16 complete Main/NMI updates. No foreign natural route or physical cadence claim.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for option in('cost','incoming','components','foreign','native-ids','first','full'):ap.add_argument('--'+option,action='store_true')
    args=ap.parse_args()
    parent=T.load_parent()
    assert sha256(parent).hexdigest()==T.PARENT
    candidate,info=T.transform(parent)
    assert T.reverse(candidate)==parent
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    if args.cost:print('DKJR_PLATFORM_COST '+json.dumps(dict(candidate_SHA256=T.PIN,rows=cost(seed,parent,candidate),
        scope='Directed native platform dispatch cycles and stack. Not physical NES frame cadence or full-stage performance.'),separators=(',',':')),flush=True)
    if args.incoming:print('DKJR_PLATFORM_INCOMING '+json.dumps(incoming(seed),separators=(',',':')),flush=True)
    if args.components:print('DKJR_PLATFORM_COMPONENTS '+json.dumps(components(seed,candidate),separators=(',',':')),flush=True)
    if args.native_ids:print('DKJR_PLATFORM_NATIVE_IDS '+json.dumps(native_ids(seed,parent,candidate),separators=(',',':')),flush=True)
    if args.foreign:print('DKJR_PLATFORM_FOREIGN '+json.dumps(foreign(parent,candidate),separators=(',',':')),flush=True)
    if args.first:print('DKJR_PLATFORM_FIRST '+json.dumps(route(seed,candidate),separators=(',',':')),flush=True)
    if args.full:print('DKJR_PLATFORM_FULL '+json.dumps(route(seed,candidate,full=True),separators=(',',':')),flush=True)


if __name__=='__main__':main()
