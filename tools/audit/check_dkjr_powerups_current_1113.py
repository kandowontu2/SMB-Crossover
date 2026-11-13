"""Read-only current DK Jr cold/source and bounded powerup-reach study."""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re
from unittest.mock import patch

import audit_current_roster_powerups_1110 as C
import check_roster_powerup_continuation_1110 as Frames

N,W,L=C.N,C.W,C.L
R=Path(__file__).resolve().parents[2]
PIN='4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3'
CURRENT='aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1'
ROW=dict(name='DONKEY KONG JR',slot=27,cycle=1,raw=40)
PAGES=(817,833,847,856,867,881,882,883,959,960,961)
CHR=16+128*8192
COOKIE_AT=534485
COOKIE=bytes.fromhex('a7280130b1118ac41a70e81c2eda030f')
SOURCE=R/'tools/reference/dkjr_natural_powerups_1113.lua'


def cold(raw):
    digest=sha256(raw).hexdigest();previous=raw
    if digest==CURRENT:
        from deliver_jay_pickup_helper_1113 import inverse
        previous=inverse(raw);assert sha256(previous).hexdigest()==PIN
    else:assert digest==PIN
    payload=b''.join(raw[CHR+p*1024:CHR+(p+1)*1024]for p in PAGES)
    assert all(raw[CHR+p*1024:CHR+(p+1)*1024]==previous[CHR+p*1024:CHR+(p+1)*1024]for p in PAGES)
    assert raw[COOKIE_AT:COOKIE_AT+16]==COOKIE==bytes.fromhex('a72801')+sha256(payload).digest()[:13]
    bundle=W.Symbols.bundle();bundle['raw']=raw
    checked=[];pending=None;Base=N.NesMPU
    class Probe(Base):
        def step(self):
            nonlocal pending
            m=self.memory
            if self.pc==0xd25e and m.rawtags[2]==2:
                pending=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1,(self.sp+2)&255)
            if pending==(self.pc,self.sp):
                assert self.p&1
                assert bytes(m.ram[3][:0x1fe0])==payload[:0x1fe0]
                assert bytes(m.ram[2][0x1000:0x1800])==payload[9*1024:]
                checked.append(True);pending=None
            return Base.step(self)
    with patch.object(N,'NesMPU',Probe):opening,m=C.cold(bundle,ROW)
    assert checked
    deltas=[(i,a,z)for i,(a,z)in enumerate(zip(payload[:0x1fe0],m.ram[3][:0x1fe0]))if a!=z]
    assert all(bytes(m.ram[bank][0x1fe0:0x1ff0])==COOKIE for bank in (2,3))
    return opening,m,dict(cookie=COOKIE.hex(),source_and_art_pages=PAGES,
        carrier_SHA256=sha256(payload).hexdigest(),code_readback=0x1fe0,
        verified_previous_nightly_SHA256=sha256(previous).hexdigest(),execution_ROM_SHA256=digest,
        verified_before_original_constructor=True,observed_live_code_deltas=deltas,
        known_native_full_stage_report='docs/qa/dkjr-full-nightly-delivery-1111.md',
        scope='Current compiled menu/cold/opening plus unchanged authenticated full-stage DK carrier. Not a new full-stage replay.')


def state(m):
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),high=N.get(m,'Player_Y_HighPos'),
        state=N.get(m,'Player_State'),dy=N.get(m,'Player_Y_Speed'),
        status=N.get(m,'PlayerStatus'),size=N.get(m,'PlayerSize'),
        engine=N.get(m,'GameEngineSubroutine'),lives=N.get(m,'NumberofLives'),
        camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
        source_ready=m.ram[2][0x8fe],source_state=m.ram[2][0x6b],
        source_y=m.ram[2][0x210],source_x=m.ram[2][0x213],
        source_held=m.ram[2][0x14],source_sample=m.ram[2][0x15])


def jumps(seed):
    ground=L.clone(seed);ground.controller_pad=0
    for i in range(6):ground[W.address(ground.bundle,'Enemy_Flag')+i]=0
    for _ in range(60):Frames.frame(ground)
    assert state(ground)['y']==176 and state(ground)['source_state']==1
    rows=[]
    for hold,right in ((1,0),(8,0),(40,0),(40,1)):
        m=L.clone(ground);points=[];peak=256;landing=None
        start=state(m)
        for tick in range(75):
            m.controller_pad=right+(128 if tick<hold else 0);Frames.frame(m)
            s=state(m);peak=min(peak,s['y'])
            if tick<4 or tick in (7,8,15,16,23,24,39,40,74):points.append(dict(tick=tick,**s))
            if tick>0 and landing is None and s['source_state']==1 and s['state']==0:landing=dict(tick=tick,**s)
            assert s['engine']==8 and s['lives']==2 and s['source_state']!=5
        rows.append(dict(hold_A=hold,right=right,start=start,minimum_y=peak,rise=176-peak,
            landing=landing,samples=points,scope='Declared enemy-free clone, original parsed opening terrain and actual Main/NMI. No natural item or native cadence claim.'))
    return rows


def controller(raw):
    b=W.Symbols.bundle();b['raw']=raw;text=SOURCE.read_text()
    names=set(re.findall(r"\br\('([^']+)'",text))|set(re.findall(r'\bL\.(\w+)',text))
    labels={n:W.address(b,n)for n in sorted(names)}
    prefix='local L={'+','.join(f'{n}={v}'for n,v in labels.items())+'}\n'
    prefix+=f'local ROM_SHA="{sha256(raw).hexdigest()}"\n'
    for constant,name in (('HEAD_OFFSET','HuHead'),('EFFECT_OFFSET','NativeRarePlayerHeadCollisionCore'),('PICKUP_OFFSET','HandlePowerUpCollision')):
        prefix+=f'local {constant}={W.location(b,name)-16}\n'
    return prefix+text


def fixtures(seed):
    rows=[];grown=None
    for kind in (0,1,2,3):
        m=L.clone(grown if kind==1 else seed);m.controller_pad=0
        before=state(m);assert before['status']==(1 if kind==1 else 0)
        N.put(m,ObjectOffset=5)
        for name,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,
            Enemy_X_Position=N.get(m,'Player_X_Position'),Enemy_PageLoc=N.get(m,'Player_PageLoc'),
            Enemy_Y_Position=N.get(m,'Player_Y_Position'),Enemy_Y_HighPos=1).items():m[W.address(m.bundle,name)+5]=value
        N.invoke(m,'NrPrepare',a=kind,x=5,y=0)
        assert N.get(m,'PowerUpType',5)==kind and N.get(m,'InvPickupOwner',5)==40 and N.get(m,'InvPickup',5)==252
        result=N.invoke(m,'HandlePowerUpCollision',a=kind,x=5,y=0,p=0x31)
        collected=state(m);assert not N.get(m,'Enemy_Flag',5)
        if kind==2:assert N.get(m,'StarInvincibleTimer')==35 and N.get(m,'AreaMusicQueue')==64
        if kind==3:assert N.get(m,'FloateyNum_Control',5)==11
        frozen=[];timeline=[]
        for tick in range(90):
            if N.get(m,'GameEngineSubroutine')==9 or N.get(m,'GuestPowerupActive'):
                frozen.append(bytes(m.ram[2][:0x800]))
            Frames.frame(m);s=state(m)
            assert s['lives']>=before['lives'] and s['engine']!=11 and s['source_state']!=5
            if tick<3 or tick in (58,59,60,61,89):timeline.append(dict(tick=tick,guest=N.get(m,'GuestPowerupActive'),age=N.get(m,'GuestPowerupAge'),**s))
        after=state(m)
        assert after['engine']==8 and after['status']==(1 if kind==0 else 2 if kind==1 else 0)
        assert after['lives']==before['lives']+int(kind==3)
        difference=[]
        if frozen:
            difference=[i for i in range(2048)if any(s[i]!=frozen[0][i]for s in frozen)]
        assert len(frozen)==(60 if kind<2 else 0) and not difference,(kind,len(frozen),difference)
        rows.append(dict(kind=kind,before=before,collected=collected,after=after,
            return_AXYP={n:result[n]for n in ('A','X','Y','P')},timeline=timeline,
            captured_freeze_frames=len(frozen),freeze_source_changed_offsets=difference,
            scope='Explicit mature native actor fixture. Flower starts from real preceding mushroom grant/continuation. No natural emergence or collision claim.'))
        if kind==0:grown=m
    return rows


def helper_fixture(seed):
    """Seed one declared stock actor offscreen, then use normal controllers."""
    m=L.clone(seed);slot=None;setup=None;events=[];phase='approach';hold=0;rearm=0;released=0
    pickup=None;head_count=0;minimum=255;head_return=None;best_head=None;jump_tick=None;curve=[];solid_heads=[];source_writes=[]
    query_point=W.address(m.bundle,'HuHead')
    query_bank=((W.location(m.bundle,'HuHead')-16)//8192)|128
    pickup_point=W.address(m.bundle,'HandlePowerUpCollision')
    pickup_bank=((W.location(m.bundle,'HandlePowerUpCollision')-16)//8192)|128
    head_point=W.address(m.bundle,'NativeRarePlayerHeadCollisionCore')
    head_bank=((W.location(m.bundle,'NativeRarePlayerHeadCollisionCore')-16)//8192)|128
    def actor(i):return dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),
        state=N.get(m,'Enemy_State',i),kind=N.get(m,'PowerUpType',i),
        x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),y=N.get(m,'Enemy_Y_Position',i))
    def observe(memory,cpu):
        nonlocal pickup,head_count,minimum,head_return,best_head
        minimum=min(minimum,cpu.sp)
        if head_return==(cpu.pc,cpu.sp):
            head_return=None
            s=state(m)
            if 320<=s['x']<=352 and(best_head is None or s['y']<best_head['player']['y']):
                best_head=dict(player=s,tile=cpu.a,row=N.get(m,'R2'),fraction=N.get(m,'R4'),
                    base=N.get(m,'R6')+256*N.get(m,'R7'))
            if cpu.a and 320<=s['x']<=352 and len(solid_heads)<16:
                solid_heads.append(dict(tick=tick,player=s,tile=cpu.a,row=N.get(m,'R2'),
                    fraction=N.get(m,'R4'),base=N.get(m,'R6')+256*N.get(m,'R7'),
                    bounce=N.get(m,'BlockBounceTimer'),hurt=N.get(m,'GuestHurtTicks')))
        if cpu.pc<32768:return
        tag=memory.rawtags[(cpu.pc-32768)//8192]
        if tag==3 and jump_tick is not None and tick-jump_tick<16 and bytes(memory[cpu.pc:cpu.pc+3])==bytes.fromhex('8d6bc0'):
            source_writes.append(dict(tick=tick-jump_tick,pc=cpu.pc,A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p,
                player=state(m),previous=memory[0xc06c],air_epoch=memory[0xc07e],
                rect=list(memory[0xc03e:0xc042]),contact=memory[0xc0ea],
                gravity=list(memory[0xc07f:0xc084]),start_y=memory[0xc076]))
        if(tag,cpu.pc)==(query_bank,query_point):
            head_return=(memory[0x100+((cpu.sp+1)&255)]+256*memory[0x100+((cpu.sp+2)&255)]+1,(cpu.sp+2)&255)
        if(tag,cpu.pc)==(head_bank,head_point):head_count+=1
        if(tag,cpu.pc)==(pickup_bank,pickup_point):
            pickup=dict(tick=tick,player=state(m),actor=actor(cpu.x),owner=N.get(m,'InvPickupOwner',cpu.x),prepared=N.get(m,'InvPickup',cpu.x))
    for tick in range(1600):
        s=state(m);x,y=s['x'],s['y'];ground=s['source_state']==1 and s['state']==0
        if slot is None and 256<=320-s['camera']<=287:
            slot=next(i for i in range(5,-1,-1)if not N.get(m,'Enemy_Flag',i))
            prior=N.get(m,'ObjectOffset');N.put(m,ObjectOffset=slot)
            for name,value in dict(Enemy_Flag=1,Enemy_ID=0x25,Enemy_PageLoc=1,Enemy_X_Position=64,
                Enemy_Y_Position=192,Enemy_Y_HighPos=1).items():m[W.address(m.bundle,name)+slot]=value
            N.invoke(m,'InitEnemyObject',x=slot)
            m[0x47+slot]=128;m[0x646+slot]=5;N.put(m,ObjectOffset=prior)
            setup=dict(tick=tick,player=s,actor=actor(slot),left=320,center=336,initial_top=192,
                width=32,oscillator=128,box=5,relative=320-s['camera'])
            assert setup['actor']['x']==320 and setup['actor']['y']==192
        item=next((actor(i)for i in range(6)if N.get(m,'Enemy_Flag',i)and N.get(m,'Enemy_ID',i)==46),None)
        ride=slot is not None and N.get(m,'Enemy_Flag',slot)and N.get(m,'Enemy_ID',slot)==0x25 and y+32==N.get(m,'Enemy_Y_Position',slot)and y<176 and s['source_state']==1
        if pickup:
            pad=0
            if s['status']==1 and s['engine']==8:
                assert setup and head_count and not N.get(m,'Enemy_Flag',pickup['actor']['slot'])
                return dict(passed=True,setup=setup,pickup=pickup,final=s,head_effects=head_count,
                    events=events,best_head=best_head,bump_curve=curve,minimum_SP=minimum,ROM_written=False,
                    scope='Explicit stock actor fixture at its offscreen admission plane; no player/item/terrain/power grants. Not a production helper birth or natural-route qualification.')
        elif item:
            phase='collect';target=item['x']-8;pad=1 if x<target-1 else 2 if x>target+1 else 0
        elif x<328:
            phase='approach';pad=1
            near=any(N.get(m,'Enemy_Flag',i)==1 and N.get(m,'Enemy_ID',i)in(2,6)
                and not N.get(m,'Enemy_State',i)&32 and N.get(m,'Enemy_Y_Position',i)>=172
                and 8<=actor(i)['x']-x<=30 for i in range(6))
            if ground and tick>=rearm and near:hold=tick+8;rearm=tick+47
            if tick<hold:pad+=128
        elif x>329:pad=2
        else:
            if ride and phase!='rise'and phase!='bump':
                phase='rise';released=0;hold=0;events.append(dict(event='board',tick=tick,player=s,actor=actor(slot)))
            if phase=='rise':
                pad=0;released+=1
                if ride and N.get(m,'Enemy_Y_Position',slot)<=180 and released>=4:
                    phase='bump';hold=tick+8;jump_tick=tick;events.append(dict(event='jump',tick=tick,player=s,actor=actor(slot)))
            elif phase!='bump':
                phase='board';pad=0
                if slot is not None and ground and tick>=rearm and 192<=N.get(m,'Enemy_Y_Position',slot)<=208:
                    hold=tick+8;rearm=tick+47
            else:pad=0
            if tick<hold:pad+=128
        m.controller_pad=pad;Frames.frame(m,observe)
        if jump_tick is not None and tick-jump_tick<55:
            q=state(m)
            curve.append(dict(tick=tick-jump_tick,pad=pad,x=q['x'],y=q['y'],dy=q['dy'],
                state=q['state'],source_state=q['source_state'],source_y=q['source_y'],
                platform_y=N.get(m,'Enemy_Y_Position',slot),slot_id=N.get(m,'Enemy_ID',slot)))
        if solid_heads and not head_count:
            return dict(passed=False,reason='source-rise-stopped-before-native-head',setup=setup,
                pickup=pickup,final=state(m),events=events,head_effects=head_count,best_head=best_head,
                bump_curve=curve,solid_heads=solid_heads,source_state_writes=source_writes)
        if state(m)['lives']<2 or state(m)['source_state']==5 or state(m)['engine']==11:
            return dict(passed=False,reason='life-lost',setup=setup,pickup=pickup,final=state(m),events=events,
                head_effects=head_count,best_head=best_head,bump_curve=curve,solid_heads=solid_heads,source_state_writes=source_writes)
    return dict(passed=False,reason='fixture-bound',setup=setup,pickup=pickup,final=state(m),events=events,
        head_effects=head_count,best_head=best_head,bump_curve=curve,solid_heads=solid_heads)


def route(seed,raw,limit=1600):
    # This derivative adds work-RAM reads required by DK's source state. All
    # RAM, ROM and input still use the actual established CPU/peripheral model.
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    assert sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
    lua=LuaRuntime(unpack_returned_tuples=True);events={};callbacks=[]
    context=dict(cpu=None,exit=None,receipt=None)
    emu=lua.table();emu.memType=lua.table_from(dict(nesDebug=0,nesPrgRom=1,nesWorkRam=2))
    emu.eventType=lua.table_from(dict(inputPolled=0,endFrame=1));emu.callbackType=lua.table_from(dict(exec=0))
    def read(at,kind=0):
        if kind==1:return raw[16+at]
        if kind==2:return seed.ram[at//8192][at&8191]
        return seed[at]
    def mapped(pc):
        if pc<32768:return None
        tag=seed.rawtags[(pc-32768)//8192]
        return lua.table_from(dict(memType=1 if tag&128 else 2,address=(tag&127)*8192+(pc&8191)))
    def cpu_state():
        c=context['cpu'];return lua.table_from({f'cpu.{k}':getattr(c,k)if c else 0 for k in ('pc','sp','a','x','y')})
    def set_input(pad,port):
        assert port==0
        seed.controller_pad=sum(bit for name,bit in (('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[name])
    def emit(value):
        print(value,flush=True)
        if value.startswith('SMB_NATIVE_RECEIPT '):context['receipt']=json.loads(value[19:])
    emu.read,emu.convertAddress,emu.getState,emu.setInput=read,mapped,cpu_state,set_input
    emu.stop=lambda code:context.update(exit=code)
    emu.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    emu.addMemoryCallback=lambda fn,_kind,lo,hi=None:callbacks.append((lo,lo if hi is None else hi,fn))
    lua.globals().emu=emu;lua.globals().CPU_CONTROLLER_OPENING=True;lua.globals().print=emit
    text=controller(raw);lua.execute(text)
    def observe(_memory,c):
        context['cpu']=c
        for lo,hi,fn in callbacks:
            if lo<=c.pc<=hi:fn()
    for tick in range(limit):
        events[0]();Frames.frame(seed,observe);events[1]()
        if context['exit']is not None:break
    return dict(passed=context['exit']==0,stopped=context['exit']is not None,logical_updates=tick+1,
        final=state(seed),controller_SHA256=sha256(text.encode()).hexdigest(),receipt=context['receipt'],
        physical_cadence_claim=False,ROM_written=False,output_files=0)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--jumps',action='store_true')
    ap.add_argument('--route',action='store_true');ap.add_argument('--fixtures',action='store_true')
    ap.add_argument('--helper-fixture',action='store_true');args=ap.parse_args()
    raw=C.ROM.read_bytes();opening,m,source=cold(raw)
    print('DKJR_CURRENT_COLD '+json.dumps(dict(ROM_SHA256=sha256(raw).hexdigest(),
        opening=opening,source=source,final=state(m)),separators=(',',':')),flush=True)
    if args.jumps:print('DKJR_CURRENT_JUMPS '+json.dumps(jumps(m),separators=(',',':')),flush=True)
    if args.fixtures:print('DKJR_CURRENT_ITEM_FIXTURES '+json.dumps(fixtures(m),separators=(',',':')),flush=True)
    if args.helper_fixture:
        result=helper_fixture(m)
        assert not result['passed'] and result['reason']=='source-rise-stopped-before-native-head'
        assert result['head_effects']==0 and result['pickup']is None
        assert result['solid_heads'][0]['tile']==193 and result['solid_heads'][0]['fraction']>=4
        assert result['solid_heads'][0]['player']['dy']==0
        assert any(q['pc']==0xa3b9 and q['A']==4 and q['player']['source_state']==3
            and q['player']['source_y']==159 for q in result['source_state_writes'])
        result['reproduced_expected_negative']=True
        print('DKJR_CURRENT_HELPER_FIXTURE '+json.dumps(result,separators=(',',':')),flush=True)
    if args.route:
        result=route(m,raw)
        assert result['stopped'] and not result['passed']
        receipt=result.pop('receipt')
        assert receipt['reason']=='four-ground-jumps-no-authored-item' and receipt['attempts']==4
        assert receipt['authored_question_cell']==193 and not receipt['head_effects']and not receipt['pickups']
        assert result['final']['x']==328 and result['final']['lives']==2
        result['reproduced_expected_negative']=True
        print('DKJR_CURRENT_NATURAL '+json.dumps(result,separators=(',',':')),flush=True)


if __name__=='__main__':main()
