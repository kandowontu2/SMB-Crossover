"""Observe actual native1-2 initialization, original fall and health writers.

No positions, actors, physics, health or inventory are seeded. The unchanged
root stage controller drives the stock1-1 flag/castle route, then stays neutral.
"""
import argparse
from collections import deque
from hashlib import sha256
import json
from unittest.mock import patch

import check_prince_draw_cache_native_1113 as Native
import check_prince_earned_sword_combat_1113 as Fight
import prince_draw_cache_1113 as Fix

P=Fight.P
ENV=dict(SMB_PRINCE_KOOPA_BRAKE='1470',SMB_PRINCE_KOOPA_MODE='air',
    SMB_PRINCE_GOOMBA_BRAKE='1710',SMB_PRINCE_GOOMBA_CLIMB='1',
    SMB_PRINCE_FINISH_STOP='0',SMB_PRINCE_FINISH_COMBAT='1',
    SMB_PRINCE_FINISH_BRICK_WAIT='1',SMB_PRINCE_FINISH_COMBAT_GAP='112',
    SMB_PRINCE_FINISH_LURE='1')


def view(m):
    row=Fight.state(m)
    for name in ('WorldNumber','LevelNumber','AreaType','AreaNumber','PlayerEntranceCtrl',
                 'AltEntranceControl','OperMode_Task','GameEngineSubroutine','PlayerEntranceCtrl',
                 'Player_State','Player_Y_Speed','Player_Y_MoveForce','Player_CollisionBits'):
        row[name]=P.N.get(m,name)
    s=m.ram[2]
    row.update(fall_count=s[0x6c6],controlled_fall=s[0x4d4],fall_step=s[0x6da],
               original_ready=s[0xab],epoch_valid=s[0xaa],dead=s[0xac],origin=s[0x89],
               delta=s[0x88],sourceFoot=int.from_bytes(s[0x84:0x86],'little'))
    return row


def check(raw,limit,*,abi_only=False,binding=None):
    class CapturedEntrance(Exception):pass
    original=Native.stage_controller(raw[Fix.Packet.COOKIE:Fix.Packet.COOKIE+16].hex())
    script=original
    for key,value in ENV.items():
        script=script.replace(f"os.getenv('{key}')",repr(value))
    with (Fix.current_binding if binding is None else binding)(raw):
        model,opening=P.cold(raw)
        bundle=model.bundle
        native_points={((P.W.location(bundle,name)-16)//8192|128,P.W.address(bundle,name)):name
            for name in ('InitScreen','Entrance_GameTimerSetup','Entrance_GameTimerSetupCore',
                         'PlayerEntrance','PlayerRdy','PlayerCtrlRoutine')}
        labels=json.loads((Fix.Packet.R/'build/prince-actor-1101-v1/native-labels-v153.json').read_text())
        for name in ('PpNativeInit','PpHostInit','PpNativeTick','PpNativeFresh'):
            if name in labels:
                native_points[(2,labels[name])]=name
        symbols={}
        for line in (Fix.Packet.R/'build/prince-actor-1101-v1/contact-core.lbl').read_text().splitlines():
            cells=line.split()
            if len(cells)==3 and cells[0]=='al':symbols[cells[2].lstrip('.')]=int(cells[1],16)
        for name in ('PpN_5_814C','PpN_7_D455','PpN_7_D464','PpN_7_D467','PpN_7_E9A4'):
            if name in symbols:native_points[(3,symbols[name])]=name
        events=[];last=None;writes=[];tail=deque(maxlen=18);updates=0;boundary=None;entrance=None
        level_at=P.W.address(bundle,'LevelNumber')
        engine_at=P.W.address(bundle,'GameEngineSubroutine')
        field_at=dict(health=0x6cf,fall_count=0x6c6,controlled_fall=0x4d4,original_ready=0xab,epoch_valid=0xaa)
        frame=P.Frames.frame
        def observe(m,cpu):
            nonlocal last,boundary,entrance
            if m[level_at]!=1 or m[engine_at] not in (7,8) or P.N.get(m,'AreaType')!=2:return
            current={name:m.ram[2][offset] for name,offset in field_at.items()}
            if last:
                for field in field_at:
                    if last['state'][field]!=current[field] and len(writes)<90:
                        writes.append(dict(update=updates,field=field,old=last['state'][field],
                            new=current[field],writer={key:last[key] for key in ('pc','bank','A','X','Y','SP')},state=view(m)))
            tag=m.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc>=0x8000 else -1
            last=dict(pc=cpu.pc,bank=tag,A=cpu.a,X=cpu.x,Y=cpu.y,SP=cpu.sp,state=current)
            name=native_points.get((tag,cpu.pc))
            if name and sum(event['name']==name for event in events)<3 and len(events)<40:
                events.append(dict(update=updates,name=name,**dict(last,state=view(m))))
            if name=='PlayerEntrance' and m[engine_at]==7 and P.N.get(m,'Player_Y_Position')>=48 \
                    and P.N.get(m,'PlayerEntranceCtrl') not in (6,7) \
                    and P.N.get(m,'AltEntranceControl')!=2 and entrance is None:
                entrance=P.N.fork(m)
                entrance.__class__=type(m).__bases__[0]
                print(json.dumps(dict(event='actual_engine7_pre_Rdy',update=updates,state=view(m))),flush=True)
                if abi_only:raise CapturedEntrance()
            if m[engine_at]==8 and boundary is None:
                boundary=dict(update=updates,**dict(last,state=view(m)))
        def tracked(m,*args,**kwargs):
            nonlocal updates
            updates+=1
            out=frame(m,observe)
            if P.N.get(m,'LevelNumber')==1:
                row=view(m)
                if not tail or (row['y'],row['action'],row['health'],row['fall_count'])!=tuple(
                    tail[-1][key] for key in ('y','action','health','fall_count')):
                    tail.append(dict(update=updates,**row))
            return out
        def finish(m,c,stop,observe=None):
            # Same actual CPU frame: the room's8M-cycle cold decoder exceeds
            # the generic per-frame500k instruction fixture limit. This is a
            # local harness bound only; game timing and code stay unchanged.
            for _ in range(4_000_000):
                if (c.pc,c.sp)==stop:return c
                if observe:observe(m,c)
                assert m[c.pc],('BRK',hex(c.pc),m.rawtags)
                c.step()
            raise AssertionError(('Prince room-cold CPU frame bound',hex(c.pc),c.sp))
        with patch.object(P,'recovery_controller',lambda image:script),patch.object(P.Frames,'frame',tracked),\
             patch.object(P.Frames.L,'finish',finish):
            try:result=P.route(model,raw,limit,recover=True)
            except CapturedEntrance:
                result=dict(passed=False,logical_updates=updates,reason='Declared source checkpoint before native PlayerRdy; complete stage result is not asserted')
    abi=None
    if entrance is not None:
        abi=entry_abi(entrance)
    return dict(ROM_SHA256=sha256(raw).hexdigest(),native_Lua_SHA256=sha256(original.encode()).hexdigest(),
        source_env_binding_SHA256=sha256(script.encode()).hexdigest(),opening=opening,
        route=result,entry=boundary,events=events,writes=writes,tail=list(tail),terminal=view(model),native_engine7_ABI=abi,
        runtime_outcome_or_physics_seeds=0,outputs=0,Mesen=False)


def entry_abi(seed):
    """Unchanged neutral native calls on the actual engine7 pre-Rdy clone."""
    m=P.N.fork(seed)
    initial=view(m)
    assert initial['GameEngineSubroutine']==7 and initial['AreaType']==2
    assert initial['PlayerEntranceCtrl']==1 and initial['AltEntranceControl']==0 and initial['y']==48,initial
    adder=P.N.invoke(m,'MegaManCollisionAdder',a=38,x=0,y=2,p=0x21)
    profile=adder['Y']
    index=m[P.W.address(m.bundle,'BlockBufferAdderData')+profile]
    ybase=P.W.address(m.bundle,'BlockBuffer_Y_Adder')
    offsets=[m[ybase+index+i] for i in range(3)]
    rows=[]
    for tick in range(96):
        P.N.invoke(m,'AutoControlPlayer',a=0,x=0,y=0,p=0x21)
        row=view(m)
        if tick<3 or row['y']==176 or tick%8==0:
            rows.append(dict(tick=tick,**{key:row[key] for key in
                ('x','y','health','fall_count','Player_State','Player_Y_Speed','Player_Y_MoveForce','GameEngineSubroutine')}))
        assert row['GameEngineSubroutine']==7 and row['health']==initial['health']
        assert row['fall_count']==initial['fall_count']
        if row['y']==176 and row['Player_State']==0 and row['Player_Y_Speed']==0:break
    else:raise AssertionError(('Native engine7 neutral floor bound',rows[-3:]))
    return dict(passed=True,initial=initial,actual_native_adder=adder,profile=profile,
                head_and_feet_adders=offsets,rows=rows,terminal=row,
                scope='Direct unchanged AutoControlPlayer(0) calls from a clone of genuinely reached PlayerEntrance engine7/Y>=48, before PlayerRdy. No native engine/actor/health/physics fields are seeded. This is a native-call ABI fixture, not a mounted repair, Main/NMI or physical test.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',action='store_true')
    p.add_argument('--limit',type=int,default=9000)
    p.add_argument('--abi-only',action='store_true')
    p.add_argument('--entry',action='store_true',help='Strict private309 native handoff, frozen209 source streams')
    p.add_argument('--compact',action='store_true')
    args=p.parse_args()
    import prince_entrance_handoff_1113 as Entry
    candidate=Entry.frozen_parent()
    parent=Fix.reverse(candidate)
    binding=None
    if args.entry:
        assert not args.parent
        candidate,_=Entry.proposal(candidate)
        binding=Entry.current_binding
    result=check(parent if args.parent else candidate,args.limit,abi_only=args.abi_only,binding=binding)
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if args.compact:
        result={key:result[key] for key in ('ROM_SHA256','native_Lua_SHA256','source_env_binding_SHA256',
                'opening','entry','terminal','runtime_outcome_or_physics_seeds','outputs','Mesen','receipt_SHA256')} | {
            'route':{key:result['route'][key] for key in ('passed','reason','logical_updates') if key in result['route']},
            'native_engine7_ABI_passed':result['native_engine7_ABI']['passed'] if result['native_engine7_ABI'] else False}
    print(json.dumps(result,sort_keys=True),flush=True)
