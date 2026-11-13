"""Current Karnov progression fixtures and one shared controller CPU route."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import check_thomas_powerups_current_1112 as Base
import check_karnov_bomb_1112 as Bomb
from replay_karnov_bomb_1112 import controller as old_controller

C, N, W, Frames = Base.C, Base.N, Base.W, Base.Frames
R = Path(__file__).resolve().parents[2]
SOURCE = R/'tools/reference/karnov_natural_bomb_1113.lua'
PIN = '318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d'
CURRENT = '65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643'
SCENE = 'a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'


def authenticate(raw):
    if sha256(raw).hexdigest()==SCENE:
        from compose_karnov_scene_motor_1113 import inverse as motor_inverse
        parent=motor_inverse(raw)
        assert sha256(parent).hexdigest()==CURRENT
        authenticate(parent)
        return
    if sha256(raw).hexdigest() == PIN:
        return
    assert sha256(raw).hexdigest() == CURRENT
    from compose_thomas_oneup_lift_1113 import inverse
    parent = inverse(raw)
    assert sha256(parent).hexdigest() == PIN
    for page, count, _ in Bomb.Compose.OWNED.values():
        start=Bomb.Compose.CHR+1024*page
        assert raw[start:start+1024*count] == parent[start:start+1024*count]
    assert raw[16+64*8192:16+65*8192] == parent[16+64*8192:16+65*8192]


def cold(raw):
    authenticate(raw)
    bundle = W.Symbols.bundle()
    bundle['raw'] = raw
    opening, model = C.cold(bundle, dict(name='KARNOV', slot=7, cycle=1, raw=34))
    assert model.ram[2][0x65] == model.ram[2][0x860] == model.ram[2][0xbb] == 0
    return opening, model


def progression(seed):
    model = C.L.clone(seed)
    rows = []
    for i, kind in enumerate((0, 1, 1, 1)):
        N.put(model, ObjectOffset=5)
        for name, value in dict(Enemy_Flag=1, Enemy_State=128, Enemy_ID=46,
                PowerUpType=kind, Enemy_X_Position=N.get(model, 'Player_X_Position'),
                Enemy_PageLoc=N.get(model, 'Player_PageLoc'), Enemy_Y_Position=N.get(model, 'Player_Y_Position'),
                Enemy_Y_HighPos=1).items():
            model[W.address(model.bundle, name)+5] = value
        N.invoke(model, 'NrPrepare', a=kind, x=5)
        physical = N.get(model, 'PowerUpType', 5)
        assert physical == kind
        N.invoke(model, 'HandlePowerUpCollision', x=5)
        state = model.ram[2]
        row = dict(pickup=i+1, kind=physical, shot=state[0x65]&3, health=state[0x68],
                   cycle=state[0x860], option=state[0x8e], owned=state[0x8f],
                   boots=state[0xbd], bomb=state[0xbb], erased=not N.get(model, 'Enemy_Flag', 5))
        assert row['erased'] and row['shot'] == (1 if i == 0 else 2)
        assert row['cycle'] == (0 if i < 2 else i-1)
        rows.append(row)
        if i == 2:
            # Explicit native scene-context fixture after earned source
            # fields. No source/gear/cycle field is seeded or overwritten.
            saved = bytes(state[:0x800]), state[0x860]
            area = N.get(model, 'AreaAddrsLOffset')
            N.put(model, AreaAddrsLOffset=area^1, DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255)
            N.invoke(model, 'InitScreen')
            assert model.ram[2][0x860] == saved[1] == 1
            assert all(model.ram[2][a] == saved[0][a] for a in (0x65, 0x68, 0x8e, 0x8f, 0xbb, 0xbd))
            N.put(model, DisableScreenFlag=0, Mirror_PPUMASK=24)
    assert rows[-1]['bomb'] == 1 and rows[-1]['owned'] & 2 and rows[-1]['option'] == 1
    return dict(passed=True, directed_mature_actor_fixtures=True, natural_claim=False,
                four_pickup_sequence=rows, same_life_scene_retained_cycle_and_gear=True)


def controller(raw, stop_after=0):
    bundle = W.Symbols.bundle()
    bundle['raw'] = raw
    import re
    source_text=SOURCE.read_text()
    if stop_after==2:
        # Keep root's exact qualified two-pickup replay reproducible while
        # later-only route work continues in the current source file.
        source_text=subprocess.check_output(['git','show',
            '66e595f3:tools/reference/karnov_natural_bomb_1113.lua'],cwd=R).decode()
    elif stop_after==3:
        source_text=subprocess.check_output(['git','show',
            'f19ecfb5:tools/reference/karnov_natural_bomb_1113.lua'],cwd=R).decode()
    names = set(re.findall(r"r\('([^']+)'", source_text))
    names.update(re.findall(r'\bL\.(\w+)',source_text))
    names.update(('Block_Buffer_1', 'HandlePowerUpCollision', 'HandleEnemyFBallCol'))
    labels = {name: W.address(bundle, name) for name in sorted(names)}
    contact = old_controller(raw, 'fixture')
    ret = int(re.search(r'local BOMB_CONTACT_RETURN=(\d+)', contact)[1])
    pre = 'local L={'+','.join(f'{key}={value}' for key, value in labels.items())+'}\n'
    pre += f'local ROM_SHA="{sha256(raw).hexdigest()}"\nlocal STOP_AFTER={stop_after or "nil"}\n'
    pre += f'local PICKUP_OFFSET={W.location(bundle,"HandlePowerUpCollision")-16}\nlocal BOMB_CONTACT_RETURN={ret}\n'
    at=16+64*8192+0x1ffc
    assert raw[at:at+3] == bytes.fromhex('e88a60')
    pre += f'local MANUAL_CREATED=0xbffc\nlocal MANUAL_OFFSET={at-16}\n'
    if 'HEAD_OFFSET' in source_text:
        pre += f'local HEAD_OFFSET={W.location(bundle,"NativeRarePlayerHeadCollisionCore")-16}\n'
    result=pre+source_text
    if stop_after==2 and sha256(raw).hexdigest()==CURRENT:
        assert sha256(result.encode()).hexdigest()=='88ccc41014cea57d2e95e48833f27291f7bf566356481362c4cbbe08b6f0eba4'
    if stop_after==3 and sha256(raw).hexdigest()==SCENE:
        assert sha256(result.encode()).hexdigest()=='57763e630aeae8ea0a0792646dd200bec841410b72942b1d1cde89af96754f35'
    return result


def route(seed, raw, limit, stop_after):
    from check_ff_stdout_controller_source_1110 import LuaRuntime, DLL, DLL_SHA
    assert sha256(DLL.read_bytes()).hexdigest() == DLL_SHA
    lua = LuaRuntime(unpack_returned_tuples=True)
    events, memory_callbacks, state = {}, [], dict(model=seed, cpu=None, stopped=False, exit_code=None)
    emu = lua.table()
    types = dict(nesDebug=0, nesWorkRam=1, nesPrgRom=2, nesSpriteRam=3)
    emu.memType = lua.table_from(types)
    emu.eventType = lua.table_from(dict(inputPolled=0, endFrame=1))
    emu.callbackType = lua.table_from(dict(exec=0))
    def read(at, kind=0):
        m = state['model']
        if kind == 1:
            return m.ram[at//8192][at%8192]
        if kind == 2:
            return raw[16+at]
        return m[at]
    def mapped(at):
        m=state['model']
        if at<0x8000:return None
        tag=m.rawtags[(at-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(at&8191)))
    def get_state():
        cpu=state['cpu']
        return lua.table_from({f'cpu.{key}':getattr(cpu,key) if cpu else 0 for key in ('pc','sp','a','x','y')})
    def set_input(pad, _port):
        seed.controller_pad = sum(bit for name, bit in (('right',1),('left',2),('down',4),('up',8),
                                 ('start',16),('select',32),('b',64),('a',128)) if pad[name])
    def stop(code):state.update(stopped=True,exit_code=code)
    emu.read,emu.convertAddress,emu.getState,emu.setInput,emu.stop=read,mapped,get_state,set_input,stop
    emu.addEventCallback=lambda fn,event:events.setdefault(event,fn)
    emu.addMemoryCallback=lambda fn,_kind,lo,hi=None:memory_callbacks.append((lo,lo if hi is None else hi,fn))
    lua.globals().emu=emu
    lua.globals().CPU_CONTROLLER_OPENING=True
    text=controller(raw,stop_after)
    lua.execute(text)
    # The real CPU cold helper already did menu/start/parser+60 opening
    # inputs. Only the controller scheduler begins at its active phase.
    assert N.get(seed,'SelectedCharacter')==34
    def observe(memory,cpu):
        state['cpu']=cpu
        for lo,hi,fn in memory_callbacks:
            if lo<=cpu.pc<=hi:fn()
    for i in range(limit):
        events[0]()
        Frames.frame(seed,observe)
        events[1]()
        if state['stopped']:break
    x=Base.player(seed)['x']//16*16
    block=W.address(seed.bundle,'Block_Buffer_1')
    nearby={xx:{yy:seed[block+((xx//256)%2)*208+((yy-32)//16)*16+(xx%256)//16]
                for yy in range(64,225,16)} for xx in range(x-32,x+81,16)}
    return dict(passed=state['exit_code']==0, stopped=state['stopped'],updates=i+1,
                final=Base.player(seed),source=dict(shot=seed.ram[2][0x65],health=seed.ram[2][0x68],
                cycle=seed.ram[2][0x860],bomb=seed.ram[2][0xbb]),nearby_tiles=nearby if state['exit_code']!=0 else {},
                controller_SHA256=sha256(text.encode()).hexdigest())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--route',action='store_true')
    p.add_argument('--limit',type=int,default=1800)
    p.add_argument('--stop-after',type=int,choices=range(5),default=0)
    p.add_argument('--write-controller',type=Path)
    args=p.parse_args()
    raw=C.ROM.read_bytes()
    if args.write_controller:
        assert not args.write_controller.exists()
        args.write_controller.write_text(controller(raw,args.stop_after),encoding='utf-8',newline='\n')
        print(json.dumps(dict(controller=str(args.write_controller),ROM_SHA256=sha256(raw).hexdigest())))
        return
    opening,seed=cold(raw)
    print('KARNOV_NATURAL_COLD '+json.dumps(opening),flush=True)
    result=route(seed,raw,args.limit,args.stop_after) if args.route else progression(seed)
    print('KARNOV_NATURAL_RESULT '+json.dumps(result),flush=True)
    assert result['passed']


if __name__=='__main__':main()
