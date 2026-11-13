"""Exact-current Quick CPU scope: native fixtures, camera and logical cost."""
from collections import Counter
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re
import subprocess

import audit_current_roster_powerups_1110 as C
import check_roster_powerup_continuation_1110 as Frames

N,W,L=C.N,C.W,C.L
R=Path(__file__).resolve().parents[2]
PIN='a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
ROW=dict(name='QUICK MAN',slot=9,cycle=2,raw=9)
COOKIE=bytes.fromhex('a7092005e731d952bdb4b950826271bc')
SOURCE=R/'tools/reference/quick_natural_powerups_1113.lua'
INSTALLED='4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3'


def proof_parent(raw):
    digest=sha256(raw).hexdigest()
    if digest==PIN:return raw,dict(input_SHA256=digest,proof_parent_SHA256=PIN,inverse_applied=False)
    assert digest==INSTALLED
    from compose_quick_climb_material_1113 import inverse,transform
    parent=inverse(raw)
    assert sha256(parent).hexdigest()==PIN and transform(parent)[0]==raw
    return parent,dict(input_SHA256=digest,proof_parent_SHA256=PIN,inverse_applied=True,
        scope='Explicit installed Quick inverse to frozen a3 proof input; no PIN replacement or ROM output.')


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


def jump_curves(seed):
    """Real source jumps in the existing native opening, enemy-free fixture."""
    settled=L.clone(seed);settled.controller_pad=0
    for i in range(6):settled[W.address(settled.bundle,'Enemy_Flag')+i]=0
    for _ in range(60):Frames.frame(settled)
    assert player(settled)['y']==176 and N.get(settled,'QmField_002C')==3
    rows=[]
    for name,held in (
        ('tap_A',lambda t:128 if t==0 else 0),
        ('hold_A_12',lambda t:128 if t<12 else 0),
        ('hold_A_40',lambda t:128 if t<40 else 0),
        ('hold_A_B_40',lambda t:192 if t<40 else 0),
        ('run_hold_A_40',lambda t:129 if t<40 else 0),
        ('air_release_repress',lambda t:128 if t<12 or 18<=t<40 else 0)):
        m=L.clone(settled);samples=[];stores=[];previous=None;peak=256
        entry=W.address(m.bundle,'CX_3C_859F')
        for tick in range(75):
            m.controller_pad=held(tick)
            def observe(memory,cpu):
                if cpu.pc==entry and memory.rawtags[1]==1:stores.append(tick)
            Frames.frame(m,observe)
            row=dict(tick=tick,pad=held(tick),**player(m),source_state=N.get(m,'QmField_002C'),
                source_held=N.get(m,'QmField_0023'),source_edges=N.get(m,'QmField_0027'),
                source_y=N.get(m,'QmField_04A0'),source_vy=[N.get(m,'QmField_0640'),N.get(m,'QmField_0660')])
            peak=min(peak,row['y'])
            if tick<4 or tick in (11,12,17,18,39,40,74) or row['state']!=previous:samples.append(row)
            previous=row['state']
            assert row['engine']==8 and row['lives']==2
        assert stores==[0],(name,stores)
        assert samples[0]['source_vy']==[4,223]
        rows.append(dict(name=name,jump_store_ticks=stores,minimum_y=peak,
            samples=samples,scope='Six enemy flags cleared in clone; native opening terrain and actual Main/NMI unchanged. No natural-route or physical cadence claim.'))
    return rows


def original_jump_policy():
    """Bounded leaves from the supplied CX ROM, without historical extraction."""
    from py65.devices.mpu6502 import MPU
    donor=Path('C:/NES/the stash/Rockman_CX-world44.spcs.bio.nes').read_bytes()
    pin='e04a4523e4ff0a0c7bfad1d30acedb9140c0972fa3be1c62e5d42a09664b5f6e'
    assert sha256(donor).hexdigest()==pin
    body=donor[0x78010:0x80010]
    def leaf(pc,stop,values):
        cpu=MPU();cpu.memory[0x8000:]=body
        for address,value in values.items():cpu.memory[address]=value
        cpu.pc=pc;steps=0
        while cpu.pc!=stop:
            cpu.step();steps+=1;assert steps<32
        return cpu
    rows=[]
    for edge in (0,1):
        c=leaf(0x8588,0x85ad,{0x27:edge,0x9b:128,0x3b:223,0x3c:4,0x2c:3})
        assert c.memory[0x2c]==(6 if edge else 3)
        if edge:assert c.memory[0x640:0x641]+c.memory[0x660:0x661]==[4,223]
        rows.append(dict(entry='3C:8588',fresh_A=edge,state=c.memory[0x2c],
            VY=[c.memory[0x640],c.memory[0x660]]))
    for held in (0,1):
        c=leaf(0x869a,0x86a8,{0x23:held,0x640:4,0x660:223})
        assert [c.memory[0x640],c.memory[0x660]]==([4,223]if held else[1,0])
        rows.append(dict(entry='3C:869A',held_A=held,VY=[c.memory[0x640],c.memory[0x660]]))
    states={state:body[0x790+state]+256*body[0x783+state]for state in (3,6,12)}
    assert states=={3:0x8560,6:0x8609,12:0xbe81}
    return dict(ROM_SHA256=pin,source_file='C:/NES/the stash/Rockman_CX-world44.spcs.bio.nes',
        physical_PRG_banks=[60,61],ground_A_leaf=body[0x588:0x5ad].hex(),
        air_release_leaf=body[0x69a:0x6a8].hex(),wall_A_branch=body[0x3e94:0x3ea1].hex(),
        state_entries={str(k):f'{v:04X}'for k,v in states.items()},actual_original_CPU_leaves=rows,
        scope='Original ground fresh-A and preguarded air-release leaves; no original live game, terrain or unlock claim.')


def flag_scope(m):
    """Inspect the real route's held-right pole stop, without repositioning."""
    assert player(m)['x']==3152 and player(m)['y']==176 and player(m)['high']==1
    start=player(m);queries=[];pending=[]
    point=W.address(m.bundle,'QuickManWorldProbe')
    def observe(memory,cpu):
        if pending and (cpu.pc,cpu.sp)==pending[-1]['return']:
            q=pending.pop();q.pop('return');q.update(A=cpu.a,material=N.get(m,'QuickManWork_00'))
            queries.append(q)
        if cpu.pc==point and memory.rawtags[1]==1:
            pending.append(dict(x=N.get(m,'R0')+256*N.get(m,'R1'),
                y=N.get(m,'QuickManWork_0A'),high=N.get(m,'QuickManWork_0B'),
                **{'return':(m[0x100+((cpu.sp+1)&255)]+256*m[0x100+((cpu.sp+2)&255)]+1,(cpu.sp+2)&255)}))
    for _ in range(3):m.controller_pad=1;Frames.frame(m,observe)
    assert not pending
    raw=m.bundle['raw'];table=raw[W.location(m.bundle,'BlockBufferAddr'):W.location(m.bundle,'BlockBufferAddr')+4]
    attrs=raw[W.location(m.bundle,'MTileAttribute'):W.location(m.bundle,'MTileAttribute')+256]
    def tile(x,y):
        page=(x>>8)&1;base=table[page]+256*table[2+page]
        a=base+((x&255)>>4)+(y&240)-32;v=m[a]
        return dict(x=x,y=y,address=a,tile=v,flags=attrs[v])
    probes=[]
    for index in range(3,7):
        q=L.clone(m);ret=N.invoke(q,'CrossoverSourceSideProbe',a=0,x=0,y=index)
        probes.append(dict(index=index,returned=ret['A'],Y=ret['Y'],R4=N.get(q,'R4'),
            R5=N.get(q,'R5'),R6=N.get(q,'R6'),R7=N.get(q,'R7')))
    from py65.disassembler import Disassembler
    from py65.devices.mpu6502 import MPU
    flat=bytearray(65536);flat[0xa000:0xc000]=m.ram[1]
    cpu=MPU(memory=flat);ds=Disassembler(cpu);pc=point;code=[]
    # Raw1 is selected only for this read-only disassembly of its owned bytes.
    for _ in range(35):
        n,op=ds.instruction_at(pc);code.append(f'{pc:04X} {bytes(cpu.memory[pc:pc+n]).hex()} {op}');pc+=n
    return dict(before=start,after=player(m),actual_Main_NMI_updates=3,source_queries=queries,
        native_side_probes=probes,cells=[tile(x,y)for x in (3153,3167,3168,3176)for y in (187,196,205)],
        mounted_source_world_disassembly=code,scope='Actual natural-route model, no position/actor/tile writes. Native probe calls use declared index fixtures in clones.')


def controller(raw,mode='mushroom'):
    assert mode in ('mushroom','items','full')
    b=W.Symbols.bundle();b['raw']=raw;text=SOURCE.read_text()
    if mode=='mushroom':
        text=subprocess.check_output(['git','show','c8b464b9:tools/reference/quick_natural_powerups_1113.lua'],cwd=R).decode()
    elif mode=='items':
        text=subprocess.check_output(['git','show','0956e57d:tools/reference/quick_natural_powerups_1113.lua'],cwd=R).decode()
    elif mode=='full':
        text=subprocess.check_output(['git','show','a7dc2ba8:tools/reference/quick_natural_powerups_1113.lua'],cwd=R).decode()
    names=set(re.findall(r"r\('([^']+)'",text))|set(re.findall(r'\bL\.(\w+)',text))
    labels={name:W.address(b,name)for name in sorted(names)}
    pre='local L={'+','.join(f'{name}={value}'for name,value in labels.items())+'}\n'
    pre+=f'local ROM_SHA="{sha256(raw).hexdigest()}"\nlocal MODE="{mode}"\n'
    pre+=f'local PICKUP_OFFSET={W.location(b,"HandlePowerUpCollision")-16}\nlocal HEAD_OFFSET={W.location(b,"NativeRarePlayerHeadCollisionCore")-16}\n'
    if mode=='full':pre+='local STAGE_OFFSETS={'+','.join(f'{n}={W.location(b,n)-16}'for n in ('HandleClimbing','FlagpoleCollision'))+'}\n'
    result=pre+text
    if mode=='mushroom'and sha256(raw).hexdigest()==PIN:
        assert sha256(result.encode()).hexdigest()=='a8b617b0a44587bfbb8875c828e95c019a36a58fbeb036e33ecb07ed20355dd4'
    elif mode=='items'and sha256(raw).hexdigest()==PIN:
        assert sha256(result.encode()).hexdigest()=='a28640952287b1bf4d42c30c4ca988aede4be9e869bcec3b56b4dec4af63ba22'
    elif mode=='full'and sha256(raw).hexdigest()==PIN:
        assert sha256(result.encode()).hexdigest()=='2283a8e704a209b1bd9595a69eb87b3e4e956074682f312eb448c3fee051dcf5'
    return result


def route(seed,raw,limit,mode,controller_text=None):
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
    text=controller(raw,mode)if controller_text is None else controller_text;lua.execute(text)
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
    parser.add_argument('--jump-curves',action='store_true')
    parser.add_argument('--flag-diagnostic',action='store_true')
    parser.add_argument('--route',choices=('mushroom','items','full'));parser.add_argument('--limit',type=int,default=1800)
    args=parser.parse_args()
    raw,input_info=proof_parent(C.ROM.read_bytes());opening,seed=cold(raw)
    print('QUICK_PROOF_INPUT '+json.dumps(input_info,separators=(',',':')),flush=True)
    print('QUICK_CURRENT_COLD '+json.dumps(dict(ROM_SHA256=sha256(raw).hexdigest(),opening=opening),separators=(',',':')),flush=True)
    if args.cold_only:return
    if args.jump_curves:
        print('QUICK_ORIGINAL_JUMP_POLICY '+json.dumps(original_jump_policy(),separators=(',',':')),flush=True)
        print('QUICK_CURRENT_JUMPS '+json.dumps(jump_curves(seed),separators=(',',':')),flush=True);return
    if args.flag_diagnostic:
        result=route(seed,raw,2600,'full')
        assert not result['passed']
        print('QUICK_FLAG_SCOPE '+json.dumps(flag_scope(seed),separators=(',',':')),flush=True);return
    if args.route:
        result=route(seed,raw,args.limit,args.route)
        print('QUICK_CURRENT_NATURAL '+json.dumps(result,separators=(',',':')),flush=True)
        assert result['passed'];return
    print('QUICK_CURRENT_FIXTURES '+json.dumps(fixtures(seed),separators=(',',':')),flush=True)
    print('QUICK_CURRENT_COST '+json.dumps(profile(seed),separators=(',',':')),flush=True)


if __name__=='__main__':main()
