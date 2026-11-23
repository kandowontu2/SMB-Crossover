"""Current helper proposal: genuine controller-only Mushroom and slot audit.

No emulator, game-state fixture, ROM file or output producer is used. The
immutable old first-item policy is rebound only after exact current binding.
"""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path
import io
import json
from unittest.mock import patch

import compose_dkjr_mushroom_helper_1123 as C
import check_dkjr_head_bridge_current_1123 as Head
import replay_dkjr_first_pickup_1113 as Replay
import check_dkjr_powerups_current_1113 as Route
from check_ff_stdout_controller_source_1110 import LuaRuntime

N, W, B, H = Head.N, Head.W, Head.B, C.H
REPLAY_SHA = 'cc60b16977d3795ed5caf6397090dadf8a7be38a402d253b7793cf65d29dd616'
CONTROLS_SHA = 'c844e5403e47bfbf5b62b8d440caf6ba440ee20d1d5cee5b638a933cf8f4606d'


def controller(raw, *, cutoff=180, route=False):
    assert H(raw) == C.CANDIDATE
    C.inverse(raw)
    assert H(Path(Replay.__file__).read_bytes()) == REPLAY_SHA
    assert H(Replay.CONTROLS.read_bytes()) == CONTROLS_SHA
    text = Replay.controller(raw)
    assert cutoff in (180, 182, 184)
    if cutoff != 180:
        text = Replay.one(text, "r('Enemy_Y_Position',p)<=180", f"r('Enemy_Y_Position',p)<={cutoff}")
    if route:
        # Keep the real birth/carry observer live from the cold opening while
        # the first-item policy owns pads. Only read-only Lua bookkeeping is
        # private to this adapter; the model's gameplay memory stays native.
        controls = Replay.CONTROLS.read_text().split('\nemu.addMemoryCallback', 1)[0]
        controls = Replay.one(controls, "r('Enemy_Y_Position',p)<=180", f"r('Enemy_Y_Position',p)<={cutoff}")
        labels = {name: W.address(W.Symbols.bundle(), name) for name in
            ('PlayerStatus','GuestPowerupActive','Player_X_Position','Player_PageLoc',
             'Player_Y_Position','Player_State','Enemy_Flag','Enemy_ID','Enemy_State',
             'Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','PowerUpType',
             'ScreenLeft_X_Pos','ScreenLeft_PageLoc')}
        text = Replay.full_stage_controller(raw)
        text = Replay.one(text, '[336]=128,', '[336]=188,')
        adapter = '''local slotAdmissionWait,slotAdmissionReady
local mushroomPolicy=(function()
 local L=LABELS
 local hold,rearm,attempts,phase,released,epoch=0,0,0,'approach',0,0
 local itemBirth,matureSeen,pickupReturn,settled
 local function r(n,i)return read(L[n]+(i or 0))end
 local function ram(at)return emu.read(2*8192+at,emu.memType.nesWorkRam)end
 local function ground()return r('Player_State')==0 and ram(0x6b)==1 end
 local function nearEnemy()
  for i=0,5 do local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-x();local id=r('Enemy_ID',i)
   if r('Enemy_Flag',i)==1 and(id==2 or id==6)and r('Enemy_State',i)&32==0 and r('Enemy_Y_Position',i)>=172 and dx>=8 and dx<=30 then return true end
  end;return false
 end
CONTROLS
 return function()
  epoch=updates
  if r('GuestPowerupActive')~=0 then return 0 end
  if r('PlayerStatus')==1 then
   settled=settled or updates
   if updates-settled>=30 then return nil end
   return 0
  end
  return control()
 end
end)()
'''.replace('LABELS', '{'+','.join(f'{n}={v}' for n,v in labels.items())+'}').replace('CONTROLS', controls)
        text = Replay.one(text, 'local function drive()\n', adapter+'local function drive()\n')
        text = Replay.one(text, ' lastUpdate=updates\n', ''' lastUpdate=updates
 local mushroomBits=mushroomPolicy()
 if mushroomBits~=nil then bits=mushroomBits;return end
 if index==3 and phase=='approach' and not slotAdmissionReady then
  assert(x()>=658 and x()<=664 and camera()<593 and read(0xbd)==176 and ram(2,0x6b)==1,
   'Safe authored bank before880 admission window')
  local n=0;for i=0,5 do if read(0x10+i)~=0 then n=n+1 end end
  if not slotAdmissionWait then
   slotAdmissionWait=updates;remember('wait-for-native-slot');events[#events].actors=approachActors()
  end
  assert(updates-slotAdmissionWait<=600,'Finite ordinary offscreen enemy wait')
  if n==6 then bits=0;return end
  slotAdmissionReady=true;remember('native-slot-free');events[#events].actors=approachActors()
 end
 if births['880'] and read(STATUS_ADDRESS)==1 and read(0x75f)==2 and ram(2,0x68)==0 then
  assert(births['336'] and births['416'] and births['480'] and births['560'] and births['624'] and births['688'] and births['752'], 'All prior authored lift admissions')
  assert(not currentTop(336),'New helper retired before880 admission')
  finish(true,'Natural Mushroom and safe original route through880 admission');return
 end
'''.replace('STATUS_ADDRESS',str(labels['PlayerStatus'])))
    assert not any(q in text for q in ('emu.write', 'emu.setState', 'io.open', 'takeScreenshot', 'loadState', 'saveState'))
    LuaRuntime().compile(text)
    return text


class Trace:
    def __init__(self, observe):
        self.observe = observe
    def run(self, cpu, stop):
        Head.Verify.finish(cpu, stop, lambda c: self.observe(c.memory, c) if self.observe else None)


def normal_frame(m, observe=None):
    return B.main_step(m, m.controller_pad, Trace(observe))


def score(m):
    at = N.address(m.bundle, 'Player1ScoreDisplay')
    value = 0
    for digit in m[at:at+6]:
        assert digit < 10
        value = value*10+digit
    return value


def first_mushroom(raw, *, cutoff=180, route=False):
    text = controller(raw, cutoff=cutoff, route=route)
    m, opening = Head.cold(raw)
    birth, mature, collected, pending, work, credit = None, None, None, None, None, None
    counters, ages, events, growth, recent = Counter(), set(), [], None, []
    lift_range=[255,0]
    hooks = {(((W.location(m.bundle, name)-16)//8192)|128, W.address(m.bundle, name)): name
        for name in ('HandlePowerUpCollision', 'GuestPowerupUpdate', 'EraseEnemyObject')}
    def item(i):
        return dict(Head.actor(m, i), kind=N.get(m, 'PowerUpType', i),
                    owner=N.get(m, 'InvPickupOwner', i), stamp=N.get(m, 'InvPickup', i))
    def token(cpu):
        return ((m[0x101+cpu.sp]+256*m[0x102+cpu.sp]+1)&65535, cpu.sp+2)
    def observe(memory, cpu):
        nonlocal birth, mature, collected, pending, work, growth
        tag, pc = Head.point(cpu)
        if (tag, pc) == (3, 0xb8f0):
            assert work is None
            work = dict(token=token(cpu), move=False, clock=False)
            counters['source_entries'] += 1
        if work and (tag, pc) == (3, 0xa2e8):
            work['move'] = True
        if work and (tag, pc) == (3, 0xaf2d):
            work['clock'] = True
        if work and (pc, cpu.sp) == work['token']:
            assert work['move'] and work['clock']
            counters['source_returns'] += 1
            if collected:
                counters['post_collection_source_returns'] += 1
            work = None
        name = hooks.get((tag, pc))
        if name == 'HandlePowerUpCollision' and cpu.x < 6 and N.get(m, 'Enemy_ID', cpu.x) == 46 and N.get(m, 'Enemy_Flag', cpu.x):
            actor = item(cpu.x)
            assert birth and mature and birth['slot'] == mature['slot'] == cpu.x
            assert actor['kind'] == 0 and actor['state'] & 128 and actor['owner'] == 40 and actor['stamp'] == 252
            pending = dict(token=token(cpu), actor=actor, before_score=score(m))
        if pending and (pc, cpu.sp) == pending['token']:
            assert not N.get(m, 'Enemy_Flag', pending['actor']['slot'])
            collected = dict(actor=pending['actor'], before_score=pending['before_score'],
                hero=Head.state(m), erased=True, entries=counters['source_entries'], returns=counters['source_returns'])
            pending = None
        if name == 'GuestPowerupUpdate' and collected and N.get(m, 'GuestPowerupActive'):
            age = N.get(m, 'GuestPowerupAge')
            assert 0 <= age < 60 and age not in ages
            ages.add(age)
            frozen = bytes(m.ram[2][:0x800])
            if growth is None:
                growth = frozen
            assert frozen == growth, 'Original source state changed during native growth'
        if (tag, pc) == (2, 0xd1f0) and cpu.x < 6:
            a = Head.actor(m, cpu.x)
            if a['id'] == 37:
                events.append(dict(event='native_helper_birth', hero=Head.state(m), actor=a,
                    slots=Head.actors(m), ordinal=m.ram[2][0x8fd]))
        if name == 'EraseEnemyObject' and cpu.x < 6 and N.get(m, 'Enemy_ID', cpu.x) == 37:
            events.append(dict(event='native_helper_erase', hero=Head.state(m), actor=Head.actor(m, cpu.x), slots=Head.actors(m)))
    def after(memory):
        nonlocal birth, mature, credit
        if collected and credit is None and N.get(m,'GuestPowerupActive')==0 and N.get(m,'PlayerStatus')==1:
            credit=score(m)
            assert credit==collected['before_score']+1000
        if Head.state(m)['x'] >= 330:
            recent.append(dict(hero=Head.state(m), actors=Head.actors(m), pad=m.controller_pad,
                source_hurt=m.ram[2][0x68], status=N.get(m, 'PlayerStatus')))
            if len(recent)>45:recent.pop(0)
        for i in range(6):
            if N.get(m, 'Enemy_Flag', i) and N.get(m, 'Enemy_ID', i)==37 and Head.actor(m,i)['x']==336:
                py=N.get(m, 'Enemy_Y_Position',i)
                lift_range[0]=min(lift_range[0],py);lift_range[1]=max(lift_range[1],py)
            if N.get(m, 'Enemy_Flag', i) and N.get(m, 'Enemy_ID', i) == 46:
                actor = item(i)
                if birth is None:
                    birth = actor
                if actor['state'] & 128 and mature is None:
                    mature = actor
    with patch.object(Route.Frames, 'frame', normal_frame):
        with redirect_stdout(io.StringIO()):
            result = Route.route(m, raw, 4000 if route else 2200, controller_text=text, observe_extra=observe, after_frame=after)
    assert result['passed'], dict(reason=(result.get('receipt') or {}).get('reason'),
        birth=birth,mature=mature,collected=collected,work=dict(counters),events=events,
        route_events=(result.get('receipt') or {}).get('events'),recent=recent[-3:])
    assert birth and mature and collected and pending is None and work is None
    assert ages == set(range(60)) and counters['post_collection_source_returns'] >= 25
    assert credit == collected['before_score']+1000
    assert N.get(m, 'PlayerStatus') == 1 and N.get(m, 'GuestPowerupActive') == 0
    assert Head.state(m)['lives'] == 2 and m.ram[2][0x68] == 0
    report = dict(passed=True, ROM_SHA256=H(raw), controller_SHA256=H(text.encode()), cutoff=cutoff, route=route,
        opening_Main=opening, logical_updates=result['logical_updates'], receipt=result['receipt'],
        birth=birth, mature=mature, collected=collected, growth_ages=sorted(ages), added_lift_top_range=lift_range,
        work=dict(counters), Mushroom_credit=credit, final_score=score(m), events=events, final=Head.state(m), outputs=0,
        scope='Genuine menu/cold/controller and naturally constructed336 helper; actual authored Mushroom, maturity/contact/erase/growth/1000 credit and25 source Move+Clock returns. No seeded actor or Mesen.')
    if route:
        report['native_route_events']=[e for e in result['receipt']['events'] if e['event'] in ('wait-for-native-slot','native-slot-free','roof')]
    return report, m


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', action='store_true')
    parser.add_argument('--cutoff', type=int, choices=(180,182,184), default=180)
    parser.add_argument('--neighbors', action='store_true', help='Run first-item thresholds180,182,184 independently through ordinary menu/cold inputs')
    args=parser.parse_args()
    parent = C.M.ROM.read_bytes()
    raw, composition = C.proposal(parent)
    assert C.inverse(raw) == parent
    print('DK M HELPER COMPOSE '+json.dumps(composition, separators=(',', ':')), flush=True)
    for cutoff in (180,182,184) if args.neighbors else (args.cutoff,):
        result, _ = first_mushroom(raw, cutoff=cutoff, route=args.route)
        result['composition'] = composition
        result['bindings'] = {Path(p).name: H(Path(p).read_bytes()) for p in (C.__file__, __file__)}
        receipt = H(json.dumps(result, sort_keys=True, separators=(',', ':')).encode())
        result.pop('receipt',None)
        print('DK M HELPER PASS '+json.dumps(result, separators=(',', ':')), flush=True)
        print('RECEIPT '+receipt, flush=True)


if __name__ == '__main__':
    main()
