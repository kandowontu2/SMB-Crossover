"""Exact-current Quick CPU scope: native fixtures, camera and logical cost."""
from collections import Counter
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re

import audit_current_roster_powerups_1110 as C
import check_roster_powerup_continuation_1110 as Frames

N,W,L=C.N,C.W,C.L
R=Path(__file__).resolve().parents[2]
PIN='a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
ROW=dict(name='QUICK MAN',slot=9,cycle=2,raw=9)
COOKIE=bytes.fromhex('a7092005e731d952bdb4b950826271bc')
SOURCE=R/'tools/reference/quick_natural_powerups_1113.lua'


def cold(raw):
    assert sha256(raw).hexdigest()==PIN
    b=W.Symbols.bundle();b['raw']=raw
    opening,m=C.cold(b,ROW)
    assert N.get(m,'FmAlts')&32 and bytes(m.ram[2][0x1fe0:0x1ff0])==COOKIE
    assert N.get(m,'QmField_06C0')==N.get(m,'QmField_0099')==40
    return opening,m


def player(m):
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),high=N.get(m,'Player_Y_HighPos'),
        state=N.get(m,'Player_State'),dy=N.get(m,'Player_Y_Speed'),
        engine=N.get(m,'GameEngineSubroutine'),lives=N.get(m,'NumberofLives'),
        status=N.get(m,'PlayerStatus'),HP=N.get(m,'QmField_06C0'),maxHP=N.get(m,'QmField_0099'),
        camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'))


def fixtures(seed):
    rows=[]
    for kind in range(4):
        m=L.clone(seed);m.controller_pad=0
        if kind<2:
            before=N.get(m,'QmField_06C0');N.invoke(m,'HuInjury',p=0x21)
            assert N.get(m,'QmField_06C0')==before-4
        N.put(m,ObjectOffset=5)
        for name,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,
            Enemy_X_Position=N.get(m,'Player_X_Position'),Enemy_PageLoc=N.get(m,'Player_PageLoc'),
            Enemy_Y_Position=N.get(m,'Player_Y_Position'),Enemy_Y_HighPos=1).items():
            m[W.address(m.bundle,name)+5]=value
        N.invoke(m,'NrPrepare',a=kind,x=5,y=0)
        physical=N.get(m,'PowerUpType',5)
        assert physical==kind and N.get(m,'InvPickupOwner',5)==9 and N.get(m,'InvPickup',5)==252
        assert N.get(m,'InvRisePhase',5)==0
        before=player(m)
        result=N.invoke(m,'HandlePowerUpCollision',a=kind,x=5,y=0,p=0x21)
        after=player(m)
        assert not N.get(m,'Enemy_Flag',5)
        assert not N.get(m,'GuestPowerupActive')
        assert after['status']==before['status']==0
        if kind<2:
            assert before['HP']==36 and after['HP']==after['maxHP']==40
            assert N.get(m,'Square2SoundQueue')==16
        elif kind==2:
            assert N.get(m,'StarInvincibleTimer')==35
            assert N.get(m,'AreaMusicQueue')==64
        else:assert N.get(m,'FloateyNum_Control',5)==11
        for _ in range(12):Frames.frame(m)
        final=player(m)
        assert final['engine']==8 and final['HP']>0
        assert final['lives']==before['lives']+int(kind==3)
        rows.append(dict(kind=kind,prepared_physical_kind=physical,before=before,collected=after,final=final,
            actual_Main_NMI_updates=12,native_return={k:result[k]for k in ('A','X','Y','P')},
            scope='Explicit mature native actor fixture; HP deficit comes from real HuInjury. No natural item claim.'))
    return rows


def profile(seed):
    cases=[]
    for name,pad in (('idle',0),('walk_right',1)):
        m=L.clone(seed);m.controller_pad=pad
        # Explicit enemy-free cost fixture, separate from natural gameplay.
        for i in range(6):m[W.address(m.bundle,'Enemy_Flag')+i]=0
        samples=[];calls=Counter();minimum=255;source_errors=[]
        loop=W.address(m.bundle,'GameLoop');native_bank=((W.location(m.bundle,'GameLoop')-16)//8192)|128
        points={W.address(m.bundle,n):n for n in ('QhMovement','QhUi','QhDraw')}
        for tick in range(64):
            state={'cpu':None,'start':None};start=player(m)
            def observe(memory,cpu):
                nonlocal minimum
                state['cpu']=cpu;minimum=min(minimum,cpu.sp)
                if cpu.pc>=32768:
                    tag=memory.rawtags[(cpu.pc-32768)//8192]
                    if (tag,cpu.pc)==(native_bank,loop):state['start']=cpu.processorCycles
                    if tag==1 and cpu.pc in points:calls[points[cpu.pc]]+=1
            Frames.frame(m,observe)
            assert state['start']is not None
            end=player(m)
            enemies=sum(bool(N.get(m,'Enemy_Flag',i)) for i in range(6))
            source=N.get(m,'QmField_0460')+256*N.get(m,'QmField_0440')
            if source!=(end['x']+8)&65535:source_errors.append((tick,source,end['x']))
            samples.append(dict(logical=tick,GameLoop_cycles=state['cpu'].processorCycles-state['start'],
                idle_NMI_Main_cycles=state['cpu'].processorCycles,enemies=enemies,
                x=end['x'],camera=end['camera'],relative=end['x']-end['camera']))
            assert end['engine']==8 and end['lives']==2
        empty=[row for row in samples if row['enemies']==0]
        assert empty and not source_errors,source_errors[:6]
        values=[row['GameLoop_cycles']for row in empty]
        cases.append(dict(name=name,logical_updates=64,enemy_free_updates=len(empty),
            mean_GameLoop_cycles=sum(values)/len(values),max_GameLoop_cycles=max(values),
            native_source_x_mismatches=source_errors,final=player(m),minimum_SP=minimum,
            actual_source_calls=dict(calls),maximum_camera_relative=max(row['relative']for row in samples),
            scope='Explicit six-flag enemy-free CPU fixture. One NMI/logical update; no physical lag/cadence claim.'))
    return cases


def controller(raw,mode='mushroom'):
    assert mode in ('mushroom','items','full')
    b=W.Symbols.bundle();b['raw']=raw;text=SOURCE.read_text()
    names=set(re.findall(r"r\('([^']+)'",text))|set(re.findall(r'\bL\.(\w+)',text))
    labels={name:W.address(b,name)for name in sorted(names)}
    pre='local L={'+','.join(f'{name}={value}'for name,value in labels.items())+'}\n'
    pre+=f'local ROM_SHA="{sha256(raw).hexdigest()}"\nlocal MODE="{mode}"\n'
    pre+=f'local PICKUP_OFFSET={W.location(b,"HandlePowerUpCollision")-16}\nlocal HEAD_OFFSET={W.location(b,"NativeRarePlayerHeadCollisionCore")-16}\n'
    return pre+text


def route(seed,raw,limit,mode):
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    assert sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
    lua=LuaRuntime(unpack_returned_tuples=True);events={};callbacks=[]
    context=dict(cpu=None,exit=None,receipt=None)
    emu=lua.table();emu.memType=lua.table_from(dict(nesDebug=0,nesPrgRom=1))
    emu.eventType=lua.table_from(dict(inputPolled=0,endFrame=1));emu.callbackType=lua.table_from(dict(exec=0))
    def read(at,kind=0):return raw[16+at]if kind==1 else seed[at]
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
    text=controller(raw,mode);lua.execute(text)
    def observe(_m,c):
        context['cpu']=c
        for lo,hi,fn in callbacks:
            if lo<=c.pc<=hi:fn()
    for tick in range(limit):
        events[0]();Frames.frame(seed,observe);events[1]()
        if context['exit']is not None:break
    result=dict(passed=context['exit']==0,stopped=context['exit']is not None,logical_updates=tick+1,
        final=player(seed),controller_SHA256=sha256(text.encode()).hexdigest(),receipt=context['receipt'],
        physical_cadence_claim=False,ROM_written=False,output_files=0)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cold-only',action='store_true')
    parser.add_argument('--route',choices=('mushroom','items','full'));parser.add_argument('--limit',type=int,default=1800)
    args=parser.parse_args()
    raw=C.ROM.read_bytes();opening,seed=cold(raw)
    print('QUICK_CURRENT_COLD '+json.dumps(dict(ROM_SHA256=sha256(raw).hexdigest(),opening=opening),separators=(',',':')),flush=True)
    if args.cold_only:return
    if args.route:
        result=route(seed,raw,args.limit,args.route)
        print('QUICK_CURRENT_NATURAL '+json.dumps(result,separators=(',',':')),flush=True)
        assert result['passed'];return
    print('QUICK_CURRENT_FIXTURES '+json.dumps(fixtures(seed),separators=(',',':')),flush=True)
    print('QUICK_CURRENT_COST '+json.dumps(profile(seed),separators=(',',':')),flush=True)


if __name__=='__main__':main()
