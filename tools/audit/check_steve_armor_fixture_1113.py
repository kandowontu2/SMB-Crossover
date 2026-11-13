"""Controller-only CPU route through the private native six-question fixture."""

import json

import check_jay_silius_scene_lifecycle_1110 as Scene
import check_roster_powerup_continuation_1110 as Frames
import replay_steve_armor_native_1113 as Native


def check(candidate,info):
    image,proof = Native.fixture(candidate)
    lua = Native.controller(candidate,info)
    bundle = Native.Roster.W.Symbols.bundle()
    bundle['raw'] = image
    m = Scene.menu(bundle,2)
    N,W = Native.Roster.N,Native.Roster.W
    idle = W.address(bundle,'IdleLoop')
    for startup in range(480):
        if tuple(N.get(m,name) for name in ('OperMode','OperMode_Task','GameEngineSubroutine')) == (1,3,8):
            break
        m.controller_pad = 0
        W.clear_logs(m)
        N.consume(m)
        cpu = N.NesMPU(memory=m,pc=idle)
        cpu.sp,cpu.p = 255,0x31
        cpu.stPushWord(0xe33b)
        for _ in range(4_000_000):
            if (cpu.pc,cpu.sp) == (idle+12,252):
                break
            assert m[cpu.pc],('BRK',hex(cpu.pc))
            cpu.step()
        else:
            raise AssertionError(('Fixture cold frame bound',hex(cpu.pc)))
    else:
        raise AssertionError('Fixture active stage bound')
    updates = 0
    def position():
        return N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),N.get(m,'Player_Y_Position')
    def frame(pad=0):
        nonlocal updates
        m.controller_pad = pad
        Frames.frame(m)
        updates += 1
        assert N.get(m,'GameEngineSubroutine') == 8 and N.get(m,'NumberofLives') == 2
        assert N.get(m,'JnHealth') == 6,(updates,position(),N.get(m,'JnHealth'))
    def walk(target):
        for _ in range(240):
            gap = target-position()[0]
            if abs(gap) <= 1:
                return
            frame(1 if gap > 0 else 2)
        raise AssertionError(('Fixture walk bound',target,position()))
    receipts = []
    for token,x in enumerate(Native.POINTS,1):
        walk(x-7)
        for _ in range(7):
            frame()
        for age in range(62):
            frame(128 if age < 9 else 0)
        assert (N.get(m,'InvPickup',5),N.get(m,'Enemy_State',5)) == (0x8c,128),(
            token,position(),N.get(m,'InvPickup',5),N.get(m,'Enemy_State',5))
        walk(x-34)
        for _ in range(9):
            frame()
        for age in range(90):
            frame(129 if age < 9 else 1)
            if m.ram[2][0x3fd]:
                break
        else:
            raise AssertionError(('Fixture collection bound',token,position()))
        assert not N.get(m,'Enemy_Flag',5) and not N.get(m,'InvPickup',5)
        for flight in range(96):
            frame()
            if not m.ram[2][0x3fd]:
                break
        else:
            raise AssertionError(('Fixture token flight bound',token))
        receipts.append(dict(token=token,world_question_left=x,top=144,
                             collection_updates=age+1,flight_updates=flight+1,
                             pattern=m.ram[2][0x1f1],robot=m.ram[2][0x1f6]))
        print(json.dumps(dict(event='native_fixture_question',**receipts[-1]),sort_keys=True),flush=True)
        if token == 3:
            for _ in range(300):
                frame()
                if m.ram[2][0x1f6] == 1 and not m.ram[2][0x1f3] and not m.ram[2][0x1f4]:
                    break
            else:
                raise AssertionError('Fixture first robot bound')
    states = set()
    for entry in range(300):
        frame()
        states.add(m.ram[2][0x1f4])
        if m.ram[2][0x1f2] and not m.ram[2][0x1f4]:
            break
    else:
        raise AssertionError(('Fixture armor bound',states))
    assert 13 in states and m.ram[2][0x1f2] == 127
    return proof|dict(menu_startup_updates=startup,controller_updates=updates,
                Lua_syntax_compiled=False,controller_SHA256=Native.Packet.Entry.digest(lua.encode()),
                questions=receipts,armor_timer=127,state13_transport_passed=True,
                runtime_state_writes=0,output_files=0,Mesen_run=False,
                scope='Actual native menu, parser and controller route through a private level-data-only ROM fixture. All six powerups are revealed, prepared, matured and collected by native gameplay.')


if __name__ == '__main__':
    candidate,info = Native.proposal(Native.Live.Art.D.HOST.read_bytes())
    print(json.dumps(check(candidate,info),sort_keys=True),flush=True)
