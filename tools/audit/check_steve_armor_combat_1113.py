"""Controller-only combat/protection in a declared native level-data fixture."""

import json
from unittest.mock import patch

import check_steve_armor_fixture_1113 as Prefix
import check_roster_powerup_continuation_1110 as Frames
import replay_steve_armor_combat_1113 as Combat
import steve_armor_idle_1113 as Idle


def check(candidate,info):
    with patch.object(Prefix.Native,'fixture',Combat.fixture):
        prefix,m = Prefix.check(candidate,info,return_model=True)
    N,W = Combat.Native.Roster.N,Combat.Native.Roster.W
    spawns,defeats,contacts = [],[],[]
    killed = set()
    pending = None
    injury_calls = 0
    updates = prefix['controller_updates']
    points = {(((W.location(m.bundle,name)-16)//8192)|128,W.address(m.bundle,name)):name
              for name in ('InitEnemyObject','JnInjury','JnDefeat')}
    symbols = info['runtime']['symbols']

    def actor(slot):
        return dict(slot=slot,x=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot),
                    y=N.get(m,'Enemy_Y_Position',slot),state=N.get(m,'Enemy_State',slot))

    def observe(model,cpu):
        nonlocal pending,injury_calls
        bank = model.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc >= 0x8000 else -1
        name = points.get((bank,cpu.pc))
        if name == 'InitEnemyObject' and N.get(model,'Enemy_ID',cpu.x) == 6:
            born = actor(cpu.x)
            assert born['x'] in Combat.NPC_X and born['y'] == 176,born
            spawns.append(born)
        elif name == 'JnInjury':
            injury_calls += 1
        elif name == 'JnDefeat' and N.get(model,'Enemy_ID',cpu.x) == 6 and cpu.x not in killed:
            killed.add(cpu.x)
            defeats.append(actor(cpu.x))
        if bank != 1:
            return
        if cpu.pc == symbols['ArmorDamage'] and model.ram[2][0x1f2] and model.ram[2][0x97e] >= 32:
            pending = dict(timer=model.ram[2][0x1f2],hp=N.get(model,'JnHealth'),
                           slot=N.get(model,'JnSavedX'),update=updates)
        elif cpu.pc == symbols['ArmorDamageProtected'] and pending:
            hit = pending
            pending = None
            expected = 2 if hit['timer'] < 8 else (hit['timer']-8)|7
            assert model.ram[2][0x1f2] == expected and model.ram[2][0x97e] == 0,hit
            assert N.get(model,'JnHealth') == hit['hp'] == 6,hit
            assert N.get(model,'Enemy_ID',hit['slot']) == 6,hit
            contacts.append(hit|dict(after=expected))

    def position():
        return N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
    def frame(pad=0):
        nonlocal updates
        m.controller_pad = pad
        Frames.frame(m,observe)
        updates += 1
        assert (N.get(m,'GameEngineSubroutine'),N.get(m,'NumberofLives'),N.get(m,'JnHealth')) == (8,2,6),(
            updates,position(),N.get(m,'Player_Y_Position'))
    for _ in range(480):
        gap = 1040-position()
        if abs(gap) <= 1:
            break
        frame(1 if gap > 0 else 2)
    else:
        raise AssertionError(('Combat ground approach',position()))
    assert N.get(m,'Player_State') == 0 and N.get(m,'Player_Y_Position') == 176
    for _ in range(400):
        frame()
        if contacts:
            break
    else:
        raise AssertionError(('Actual armor contact bound',spawns,[actor(s) for s in range(6)]))
    assert len(spawns) == 2 and injury_calls > 0
    retained = False
    positions = []
    for age in range(90):
        frame(64 if age < 3 else 0)
        if m[0x5c87]:
            positions.append(m[0x5c88]+256*m[0x5c89])
            retained |= bool(defeats)
        if len(defeats) == 2 and not m[0x5c87] and age >= 30:
            break
    else:
        raise AssertionError(('Native wave defeats bound',spawns,contacts,defeats,positions,[actor(s) for s in range(6)]))
    assert retained and len(positions) == 14,(positions,defeats)
    for _ in range(6):
        frame(2)
    assert N.get(m,'PlayerFacingDir') == 2
    left = []
    for age in range(50):
        frame(64 if age < 3 else 0)
        if m[0x5c87]:
            left.append(m[0x5c88]+256*m[0x5c89])
    assert len(left) == 14
    exit_seen = False
    for clock in range(2300):
        frame()
        exit_seen |= m.ram[2][0x1f4] == 16
        if not m.ram[2][0x1f2] and not m.ram[2][0x1f4]:
            break
    else:
        raise AssertionError('Combat fixture natural exit bound')
    assert exit_seen and m.ram[2][0x1f6] == 1
    image,proof = Combat.fixture(candidate)
    lua = Combat.controller(candidate,info)
    return proof|dict(controller_SHA256=Combat.Native.Packet.Entry.digest(lua.encode()),Lua_compiled=True,
        actual_native_spawns=spawns,actual_native_defeats=defeats,native_injury_calls=injury_calls,
        accepted_contacts=contacts,wave_retained_after_native_hit=retained,
        right_wave_positions=positions,left_wave_positions=left,controller_updates=updates,
        natural_exit=True,terminal_health=6,terminal_lives=2,runtime_state_writes=0,
        output_files=0,Mesen_run=False)


if __name__ == '__main__':
    candidate,info = Idle.proposal(Idle.Native.Live.Art.D.HOST.read_bytes(),optimized=False)
    print(json.dumps(check(candidate,info),sort_keys=True),flush=True)
