"""Steve Star/1UP semantics using declared native actors and real Main/NMI."""

from contextlib import nullcontext,redirect_stdout
from io import StringIO
import json
from unittest.mock import patch

import replay_steve_natural_pickups_1113 as Natural


Native,N,W,FRAME = Natural.Native,Natural.N,Natural.W,Natural.FRAME
PIN = Native.IDLE_CANDIDATE


def state(m):
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                y=N.get(m,'Player_Y_Position'),health=N.get(m,'JnHealth'),
                lives=N.get(m,'NumberofLives'),hurt=N.get(m,'JnHurt'),
                tier=N.get(m,'JnOwnedTier'),selected=N.get(m,'JnSelected'),
                ammo=[N.get(m,'JnAmmo',i) for i in range(10)],
                pattern=m.ram[2][0x1f1],armor=m.ram[2][0x1f2],
                upgrade_state=m.ram[2][0x1f4],robot=m.ram[2][0x1f6],
                pending=m.ram[2][0x3fd],star=N.get(m,'StarInvincibleTimer'),
                status=N.get(m,'PlayerStatus'),freeze=N.get(m,'GuestPowerupActive'))


def actor(m,slot):
    return dict(slot=slot,id=N.get(m,'Enemy_ID',slot),flag=N.get(m,'Enemy_Flag',slot),
                kind=N.get(m,'PowerUpType',slot),state=N.get(m,'Enemy_State',slot),
                x=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot),
                y=N.get(m,'Enemy_Y_Position',slot),box=N.get(m,'Enemy_BoundBoxCtrl',slot),
                tag=N.get(m,'InvPickup',slot),floaty=N.get(m,'FloateyNum_Control',slot))


class Probe(Natural.Controller):
    def __init__(self,m):
        super().__init__(m)
        self.cpu = None
        self.record = True
        self.writes = []
        self.pads = []
        self.states = []
        names = ('PwrUpJmp','UnionPwrUpCore','NrPrepare','JnPreparePickup','HuFullBox',
                 'GetEnemyBoundBox','PlayerCollisionCore','HandlePowerUpCollision',
                 'NrPickup','JnCollectPickup','MarioSourcePowerupCollision',
                 'ShellOrBlockDefeat','JnInjury','InitEnemyObject','GetAreaMusic',
                 'FloateyNumbersCore')
        self.targets = {(((W.location(m.bundle,name)-16)//8192)|128,W.address(m.bundle,name)):name
                        for name in names}
        self.addresses = {W.address(m.bundle,name):name for name in
                          ('StarInvincibleTimer','AreaMusicQueue','Square2SoundQueue',
                           'NumberofLives','JnHealth')}

    def __enter__(self):
        probe = self
        self.bus_type = type(self.model)
        self.cpu_type = N.NesMPU
        class ObservedBus(self.bus_type):
            def __setitem__(model,at,value):
                if probe.record and isinstance(at,int) and at in probe.addresses:
                    field = probe.addresses[at]
                    if value or field in ('StarInvincibleTimer','JnHealth'):
                        probe.writes.append(dict(update=probe.updates,field=field,value=value,
                                                 pc=probe.cpu.pc if probe.cpu else None))
                return super().__setitem__(at,value)
        class ObservedCPU(self.cpu_type):
            def step(cpu):
                probe.cpu = cpu
                if cpu.pc >= 0x8000:
                    bank = cpu.memory.rawtags[(cpu.pc-0x8000)//8192]
                    name = probe.targets.get((bank,cpu.pc))
                    if name:
                        probe.calls[name] += 1
                        if name in ('GetEnemyBoundBox','PlayerCollisionCore') and cpu.x == 5:
                            probe.calls[name+'PickupSlot'] += 1
                        if name in ('ShellOrBlockDefeat','JnInjury','InitEnemyObject','GetAreaMusic'):
                            row = dict(update=probe.updates,routine=name,player=state(probe.model))
                            if cpu.x < 6 and name != 'GetAreaMusic':
                                row['enemy'] = actor(probe.model,cpu.x)
                            probe.events.append(row)
                return super().step()
        self.model.__class__ = ObservedBus
        self.cpu_patch = patch.object(N,'NesMPU',ObservedCPU)
        self.cpu_patch.__enter__()
        return self

    def __exit__(self,*exc):
        self.cpu_patch.__exit__(*exc)
        self.model.__class__ = self.bus_type

    def frame(self,pad=0,observe=None):
        self.model.controller_pad = pad
        self.updates += 1
        FRAME(self.model,observe)
        self.pads.append(pad)
        self.states.append(Native.Packet.Entry.digest(json.dumps(state(self.model),sort_keys=True).encode()))
        assert Natural.Punch.mode(self.model) == (1,3,8),state(self.model)
        assert N.get(self.model,'NumberofLives') >= 2 and N.get(self.model,'JnHealth') > 0,state(self.model)

    def values(self,field):
        return [row['value'] for row in self.writes if row['field'] == field]


def fixture(probe,kind):
    """Only native actor data and its declared mature state are supplied."""
    m = probe.model
    initial = state(m)
    assert not N.get(m,'Enemy_Flag',5)
    probe.record = False
    for name,value in dict(Enemy_ID=46,PowerUpType=kind,
                           Enemy_X_Position=initial['x']&255,Enemy_PageLoc=initial['x']>>8,
                           Enemy_Y_Position=initial['y']+7,Enemy_Y_HighPos=1,
                           Enemy_X_Speed=16,Enemy_MovingDir=1).items():
        m[W.address(m.bundle,name)+5] = value
    probe.record = True
    N.invoke(m,'PwrUpJmp',a=kind,x=5,y=0)
    assert N.get(m,'Enemy_BoundBoxCtrl',5) == 3 and N.get(m,'PowerUpType',5) == kind
    assert state(m) == initial,state(m)
    probe.record = False
    m[W.address(m.bundle,'Enemy_State')+5] = 128
    m[W.address(m.bundle,'Enemy_SprAttrib')+5] = 0
    probe.record = True
    prepared = actor(m,5)
    for age in range(12):
        probe.frame()
        if not N.get(m,'Enemy_Flag',5):
            break
    else:
        raise AssertionError(('Native mature fixture collection bound',kind,state(m),actor(m,5),probe.calls))
    assert probe.calls['PwrUpJmp'] == probe.calls['UnionPwrUpCore'] == 1
    assert probe.calls['JnPreparePickup'] == probe.calls['HandlePowerUpCollision'] == 1
    assert probe.calls['GetEnemyBoundBoxPickupSlot'] and probe.calls['PlayerCollisionCorePickupSlot']
    assert probe.calls['MarioSourcePowerupCollision'] == 1
    assert 32 in probe.values('Square2SoundQueue')
    return dict(kind=kind,initial=initial,prepared=prepared,collected=state(m),
                collection_updates=age+1,actor_erased=True)


def cold(raw):
    assert Native.Packet.Entry.digest(raw) == PIN
    model,startup = Natural.opening(raw)
    cookie = raw[Native.Packet.Entry.prg(94,0xb2ef):Native.Packet.Entry.prg(94,0xb2ef)+16]
    assert all(bytes(model.ram[bank][0x1fe0:0x1ff0]) == cookie for bank in (1,2,3))
    assert state(model)['health'] == 6 and state(model)['lives'] == 2
    return model,startup


def source_preserved(before,after):
    for field in ('health','tier','selected','ammo','pattern','armor','upgrade_state','robot','pending','status','freeze'):
        assert before[field] == after[field],(field,before[field],after[field])


def effect(raw,kind):
    model,startup = cold(raw)
    with Probe(model) as probe:
        result = fixture(probe,kind)
        before = result['initial']
        source_preserved(before,result['collected'])
        if kind == 2:
            assert probe.values('StarInvincibleTimer') == [35],probe.writes
            assert 64 in probe.values('AreaMusicQueue')
            for _ in range(480):
                probe.frame(1)
                defeats = [e for e in probe.events if e['routine'] == 'ShellOrBlockDefeat']
                if defeats:
                    break
            else:
                raise AssertionError(('Natural first Goomba Star contact bound',state(model),probe.events))
            hit = defeats[0]
            assert hit['enemy']['id'] == 6 and hit['player']['star'] > 0
            slot = hit['enemy']['slot']
            assert N.get(model,'Enemy_State',slot)&32 and N.get(model,'FloateyNum_Control',slot) == 1
            assert not probe.calls['JnInjury'] and state(model)['health'] == 6
            result['natural_Goomba_Star_defeat'] = hit|dict(native_defeated_state=N.get(model,'Enemy_State',slot),
                                                           native_score=1,health_retained=True,controller_B_used=False)
            for _ in range(1000):
                probe.frame()
                if not N.get(model,'StarInvincibleTimer'):
                    break
            else:
                raise AssertionError('Original Star timer expiry bound')
            assert probe.values('StarInvincibleTimer') == list(range(35,-1,-1))
            assert 1 in probe.values('AreaMusicQueue') and probe.calls['GetAreaMusic']
            result['timer_writes'] = probe.values('StarInvincibleTimer')
            result['music_requests'] = probe.values('AreaMusicQueue')
        else:
            assert N.get(model,'FloateyNum_Control',5) == 11
            for _ in range(70):
                probe.frame()
            assert N.get(model,'NumberofLives') == before['lives']+1
            assert probe.values('NumberofLives') == [3] and 64 in probe.values('Square2SoundQueue')
            result['deferred_life_award'] = [e for e in probe.writes if e['field'] in ('NumberofLives','Square2SoundQueue')]
        final = state(model)
        source_preserved(before,final)
        assert final['lives'] == before['lives']+int(kind == 3)
        result.update(final=final,calls=dict(probe.calls),menu_startup_updates=startup,
                      actual_Main_NMI_updates=probe.updates,writes=probe.writes)
        return result


def ordinary_contact(raw):
    model,startup = cold(raw)
    with Probe(model) as probe:
        for _ in range(480):
            probe.frame(1)
            if N.get(model,'JnHealth') < 6:
                break
        else:
            raise AssertionError('Unprotected natural first Goomba contact bound')
        hits = [e for e in probe.events if e['routine'] == 'JnInjury']
        assert len(hits) == 1 and hits[0]['enemy']['id'] == 6
        assert state(model)['health'] == 4 and not state(model)['star']
        return dict(actual_Main_NMI_updates=probe.updates,contact=hits[0],final=state(model),
                    menu_startup_updates=startup,actor_or_item_fixture=False)


def check(raw):
    star,oneup = effect(raw,2),effect(raw,3)
    control = ordinary_contact(raw)
    return dict(passed=True,ROM_SHA256=PIN,Star=star,oneUP=oneup,unprotected_control=control,
                source_health_weapon_pattern_armor_seeds=0,new_helpers=0,output_files=0,Mesen_run=False,
                scope='Each case starts through actual cold/menu/Start/parser on exact62ba. Star/1UP actors are explicitly placed mature after real native PwrUpJmp and preparation. Main/NMI performs boxes, collision, collection and continuation. Star combat uses the actual stock parser Goomba and ordinary Right without B. The control uses the same unmodified stock level without a pickup fixture.')


def natural(raw, *, include_streams=False):
    model,startup = cold(raw)
    _,punch,_ = Native.Live.Wave.incumbent(Natural.Idle.reverse(raw))
    with Probe(model) as probe:
        for pad in [0]*6+[64]*12+[0]*6:
            probe.frame(pad)
        with patch.object(Natural.Frames,'frame',probe.existing_frame):
            fight = Natural.Punch.natural_goomba(model,dict(symbols=punch))
        first = probe.token(336,329,302,1)
        with patch.object(Natural.Frames,'frame',probe.existing_frame):
            to_hidden = Natural.Route.continue_route(model,target=1014,max_updates=1800)
        assert abs(to_hidden['x']-1014) <= 1 and to_hidden['y'] == 176,to_hidden
        probe.walk(1017)
        for _ in range(7):
            probe.frame()
        hidden_launch = probe.state()
        for age in range(120):
            probe.frame(128 if age < 9 else 0)
            if N.get(model,'Enemy_ID',5) == 46 and N.get(model,'PowerUpType',5) == 3 and N.get(model,'Enemy_State',5)&128:
                break
        else:
            raise AssertionError(('Natural hidden1UP maturity bound',probe.state(),probe.events))
        hidden_mature = actor(model,5)
        for chase in range(120):
            probe.frame(1)
            if not N.get(model,'Enemy_Flag',5):
                break
        else:
            raise AssertionError(('Natural hidden1UP collection bound',probe.state(),actor(model,5)))
        hidden_contact = probe.state()
        assert N.get(model,'FloateyNum_Control',5) == 11
        for _ in range(12):
            probe.frame()
        assert N.get(model,'NumberofLives') == 3
        hidden = dict(launch=hidden_launch,mature=hidden_mature,contact=hidden_contact,
                      chase_updates=chase+1,life_award=state(model))
        print(json.dumps(dict(event='natural_hidden1UP',**hidden),sort_keys=True),flush=True)
        with patch.object(Natural.Frames,'frame',probe.existing_frame):
            to_flower = Natural.Route.continue_route(model,target=1236,max_updates=1500)
        assert abs(to_flower['x']-1236) <= 1 and to_flower['y'] == 176,to_flower
        second = probe.token(1248,1239,1214,5)
        with patch.object(Natural.Frames,'frame',probe.existing_frame):
            to_star = Natural.Route.continue_route(model,target=1607,max_updates=1500)
        assert abs(to_star['x']-1607) <= 1 and to_star['y'] == 176,to_star
        probe.walk(1609)
        for _ in range(7):
            probe.frame()
        star_launch = probe.state()
        for age in range(120):
            probe.frame(128 if age < 9 else 0)
            if N.get(model,'Enemy_ID',5) == 46 and N.get(model,'PowerUpType',5) == 2 and N.get(model,'Enemy_State',5)&128:
                break
        else:
            raise AssertionError(('Natural Star maturity bound',probe.state(),probe.events))
        star_mature = actor(model,5)
        star_trace = []
        for chase in range(180):
            gap = actor(model,5)['x']-state(model)['x']-8
            if gap > 4:
                pad = 1
            elif gap < -4:
                pad = 2
            else:
                pad = 0
            probe.frame(pad)
            if chase%8 == 0:
                star_trace.append(dict(update=probe.updates,pad=pad,player=state(model),actor=actor(model,5)))
            if not N.get(model,'Enemy_Flag',5):
                break
        else:
            raise AssertionError(('Natural Star collection bound',probe.state(),actor(model,5)))
        star_contact = probe.state()
        assert N.get(model,'StarInvincibleTimer') > 0
        assert 35 in probe.values('StarInvincibleTimer') and 64 in probe.values('AreaMusicQueue')
        for _ in range(24):
            probe.frame()
        star = dict(launch=star_launch,mature=star_mature,contact=star_contact,chase_updates=chase+1,
                    trace=star_trace,final=state(model))
        assert star['final']['lives'] == 3 and star['final']['pattern'] == 5
        result = dict(passed=True,ROM_SHA256=PIN,menu_startup_updates=startup,
                    actual_Main_NMI_updates=probe.updates,fight=fight,first=first,
                    hidden1UP=hidden,second=second,Star=star,
                    crossings=[to_hidden,to_flower,to_star],native_calls=dict(probe.calls),
                    native_events=probe.events,writes=probe.writes,
                    input_SHA256=Native.Packet.Entry.digest(bytes(probe.pads)),
                    state_SHA256=Native.Packet.Entry.digest(''.join(probe.states).encode()),
                    runtime_state_writes=0,new_helpers=0,output_files=0,Mesen_run=False,
                    scope='Natural stock1-1 route from actual cold/menu/Start/parser. All four authored powerups are revealed, matured and collected by ordinary controller gameplay. Actor, source inventory, health, pattern and armor values are supplied only by the game.')
        if include_streams:
            result['streams'] = dict(pads=probe.pads,states=probe.states)
        return result


def compact(result):
    if 'hidden1UP' in result:
        star = {key:value for key,value in result['Star'].items() if key != 'trace'}
        return dict(passed=result['passed'],ROM_SHA256=PIN,
                    actual_Main_NMI_updates=result['actual_Main_NMI_updates'],
                    menu_startup_updates=result['menu_startup_updates'],
                    first_Alpha=result['first']['contact'],hidden1UP=result['hidden1UP'],
                    second_Alpha=result['second']['contact'],Star=star,
                    native_calls=result['native_calls'],input_SHA256=result['input_SHA256'],
                    state_SHA256=result['state_SHA256'],runtime_state_writes=0,
                    new_helpers=0,output_files=0,Mesen_run=False)
    rows = {key:{name:value for name,value in result[key].items() if name != 'writes'}
            for key in ('Star','oneUP')}
    return dict(passed=result['passed'],ROM_SHA256=PIN,**rows,
                unprotected_control=result['unprotected_control'],
                source_health_weapon_pattern_armor_seeds=0,new_helpers=0,output_files=0,Mesen_run=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--natural',action='store_true')
    parser.add_argument('--verbose',action='store_true')
    args = parser.parse_args()
    raw = Native.Live.Art.D.HOST.read_bytes()
    with nullcontext() if args.verbose else redirect_stdout(StringIO()):
        result = natural(raw) if args.natural else check(raw)
    print(json.dumps(result if args.verbose else compact(result),sort_keys=True),flush=True)
