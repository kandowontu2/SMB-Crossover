"""Six explicit native token pickups followed by actual Steve Main/NMI frames."""

import argparse
import json
from unittest.mock import patch

import audit_current_roster_powerups_1110 as Roster
import check_roster_powerup_continuation_1110 as Frames
import steve_armor_live_1113 as Live
import steve_armor_packet_1113 as Packet
import steve_armor_wave_1113 as Wave


def check(raw, *, fast_order=False,full_clock=False):
    if fast_order:
        with patch.object(Live,'order_blocks',lambda rows:rows):
            candidate,info = Live.proposal(raw)
    else:
        candidate,info = Live.proposal(raw)
    bundle = Roster.W.Symbols.bundle()
    bundle['raw'] = candidate
    opening,m = Roster.cold(bundle,dict(name='STEVE HERMANN',slot=15,cycle=2,raw=16))
    N,W = Roster.N,Roster.W
    _,incumbent,_ = Wave.incumbent(raw)
    updates = 0

    def state():
        return dict(update=updates,frame=N.get(m,'FrameCounter'),
                    pattern=m.ram[2][0x1f1],countdown=m.ram[2][0x1f3],
                    upgrade_state=m.ram[2][0x1f4],robot=m.ram[2][0x1f6],
                    armor=m.ram[2][0x1f2],windup=m.ram[2][0x1f9],
                    pending=m.ram[2][0x3fd],health=N.get(m,'JnHealth'),
                    lives=N.get(m,'NumberofLives'))

    def frame(pad=0,observe=None):
        nonlocal updates
        m.controller_pad = pad
        Frames.frame(m,observe)
        updates += 1
        assert N.get(m,'GameEngineSubroutine') == 8 and N.get(m,'NumberofLives') == 2, state()

    # The lifecycle scene explicitly removes the opening NPCs. Terrain,
    # menu, native controllers, token preparation and collection stay live.
    for slot in range(6):
        m[W.address(bundle,'Enemy_Flag')+slot] = 0
    for _ in range(30):
        frame()
    assert N.get(m,'JnHealth') == 6 and not m.ram[2][0x1f2]
    pickups = []
    for token in range(6):
        N.put(m,ObjectOffset=5)
        for name,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=0,
                               Enemy_X_Position=N.get(m,'Player_X_Position'),
                               Enemy_PageLoc=N.get(m,'Player_PageLoc'),
                               Enemy_Y_Position=N.get(m,'Player_Y_Position'),
                               Enemy_Y_HighPos=1).items():
            m[W.address(bundle,name)+5] = value
        N.invoke(m,'NrPrepare',a=0,x=5,y=0)
        m[W.address(bundle,'Enemy_State')+5] = 128
        assert N.get(m,'InvPickup',5) == 0x8c
        N.invoke(m,'HandlePowerUpCollision',a=0,x=5,y=0)
        assert not N.get(m,'Enemy_Flag',5) and m.ram[2][0x3fd], state()
        for flight in range(96):
            frame()
            if not m.ram[2][0x3fd]:
                break
        else:
            raise AssertionError(('Token flight bound',state()))
        pickups.append(dict(token=token+1,flight_updates=flight+1,state=state()))
        print(json.dumps(dict(event='native_token_collected',**pickups[-1]),sort_keys=True),flush=True)
        if token == 2:
            for arrival in range(300):
                frame()
                if m.ram[2][0x1f6] == 1 and not m.ram[2][0x1f4] and not m.ram[2][0x1f3]:
                    break
            else:
                raise AssertionError(('First original robot bound',state()))
            assert not m.ram[2][0x1f2],state()
    transitions = []
    previous = None
    for entry in range(300):
        frame()
        current = state()
        key = (current['upgrade_state'],bool(current['armor']))
        if key != previous:
            transitions.append(current)
        previous = key
        if current['armor'] and current['upgrade_state'] == 0:
            break
    else:
        raise AssertionError(('Original armor grant bound',state()))
    assert any(row['upgrade_state'] == 13 for row in transitions),transitions
    assert m.ram[2][0x1f2] == 127 and N.get(m,'JnHealth') == 6,state()
    armor_grant = state()
    attacks = []
    for face in (1,2):
        for _ in range(6 if face == 2 else 0):
            frame(2)
        assert N.get(m,'PlayerFacingDir') == face
        births = []
        positions = []
        def observe(model,cpu):
            if model.rawtags[1] == 3 and cpu.pc == incumbent['StevePunchBirth']:
                births.append(updates)
        for age in range(50):
            frame(64 if age < 3 else 0,observe)
            if m[0x5c87]:
                positions.append(m[0x5c88]+256*m[0x5c89])
        assert len(births) == 1 and len(positions) == 14,(face,births,positions,state())
        assert all((b-a)&65535 == (4 if face == 1 else 65532)
                   for a,b in zip(positions,positions[1:])),(face,positions)
        attacks.append(dict(facing=face,actual_B_edge=True,births=1,positions=positions))
    natural_exit = None
    if full_clock:
        exit_states = []
        previous = None
        prior_timer = m.ram[2][0x1f2]
        clock_events = 0
        for elapsed in range(2300):
            frame()
            current = state()
            key = (current['upgrade_state'],current['armor'])
            if current['armor'] != prior_timer:
                assert current['frame']&15 == 0,state()
                assert current['armor'] == (prior_timer-1 if prior_timer > 2 else 0),state()
                clock_events += 1
            prior_timer = current['armor']
            if key != previous and (current['armor'] in (120,2,0) or current['upgrade_state']):
                exit_states.append(current)
            previous = key
            if not current['armor'] and not current['upgrade_state']:
                break
        else:
            raise AssertionError(('Natural armor clock/exit bound',state()))
        assert any(row['upgrade_state'] == 16 for row in exit_states),exit_states
        assert m.ram[2][0x1f6] == 1 and N.get(m,'JnHealth') == 6,state()
        natural_exit = dict(updates=elapsed+1,clock_events=clock_events,
                            source_16_frame_clock_verified=True,states=exit_states,terminal=state())
    return dict(parent=Packet.Entry.digest(raw),candidate=Packet.Entry.digest(candidate),
                opening=opening,pickups=pickups,armor_entry=transitions,armor_grant=armor_grant,
                controller_attacks=attacks,natural_clock_exit=natural_exit,
                packet_order_optimized=not fast_order,output_files=0,release_qualified=False,
                fixture_scope='Six actual prepared native mature token actors are explicitly placed and collected at the player. Opening NPCs are removed. No token pattern, robot, armor timer or armor pose is seeded. Every subsequent update uses native Main/NMI and controller input.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fast-order',action='store_true')
    parser.add_argument('--full-clock',action='store_true')
    parser.add_argument('--before-quick',action='store_true')
    args = parser.parse_args()
    print(json.dumps(check(Packet.qualification_parent(before_quick=args.before_quick),
                           fast_order=args.fast_order,full_clock=args.full_clock),
                     sort_keys=True),flush=True)
