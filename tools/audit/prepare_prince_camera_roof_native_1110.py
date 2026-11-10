"""Test and stage the original running jump from Prince's third 1-1 pipe."""

import argparse
import json
from pathlib import Path
import sys

import check_prince_goomba_climb_handoff_1110 as Climb
from prepare_prince_camera_framing_native_1110 import PIN, R, SYMBOLS, checked, once, read
from prepare_prince_camera_framing_native_1110_v3 import ROM
from prepare_prince_camera_framing_native_1110_v4 import OUT as PRIOR
from prepare_selected_native_packet_v1 import prepare, sha


Route, N, Seam, Recovery = Climb.Route, Climb.N, Climb.Seam, Climb.Recovery
OUT = R / 'build/prince-camera-roof-native-1110'
PINS = {
    PRIOR / 'ready.json': 'a7c74e3af6e50a9f7a6450ed4526297fe088614bf24b60f8312fa4649e4786ba',
    PRIOR / 'controller.lua': '1a03103c6db993f6a009a7900eb9762743b198479dbcde991fbc3a0ec13b2af2',
    PRIOR / 'capture/full11.json': 'b8ccae5ccacc8c240be55b846f3412957260bbdfa02eeee38f823b9b67eea980',
    PRIOR / 'capture/prince-diagnostic.json': 'beba201865f5519c048b0f324452ac49cd6f9b1061e8bd980d0a37211cc1dcdb',
}


ROOF = r'''
local function thirdRoof(s,o,support,finish)
 if not o or o.left~=736 or not route.on_top then return false end
 local x=s.world_x
 if route.mode=='pipe-cross' then
  if x>=745 and x<=752 and math.abs(s.native_y-112)<=2 and support and runReady(s)
      and s.source_facing==255 then
   local capX=x+13
   local solidCap,tile=solid(capX,144)
   if not solidCap then capX=x+2;solidCap,tile=solid(capX,144)end
   if not solidCap or (tile&0xfc)~=0x10 or solid(capX,143) then
    return true,framedFinish(false,'Third running A requires actual exposed native cap support',finish)
   end
   route.third_roof={request=s,request_Main=admitted,cap_x=capX,cap_tile=tile,
     minimum_foot=s.physical_foot,maximum_x=x,samples={}}
   routeMode('third-roof-takeoff',{'right','a'});return true
  elseif x>752 then
   return true,framedFinish(false,'Third cap passed the supported running A window',finish)
  end
 end
 local jump=route.third_roof
 if route.mode=='third-roof-takeoff' then
  route.pad={'right','a'}
  if s.source_action==4 then
   jump.admission=s;jump.admission_Main=admitted
   routeMode('third-roof-flight',{'right'})
  elseif admitted-route.changed>28 then
   return true,framedFinish(false,'Third native cap did not admit original running A',finish)
  end
  return true
 end
 if route.mode=='third-roof-flight' then
  route.pad={'right'}
  jump.minimum_foot=math.min(jump.minimum_foot,s.physical_foot)
  jump.maximum_x=math.max(jump.maximum_x,x)
  if admitted%4==0 and #jump.samples<24 then
   local actors={}
   for _,b in ipairs(thirdGroup.births) do actors[#actors+1]=groupActor(b.slot)end
   jump.samples[#jump.samples+1]={Main=admitted,player=s,actors=actors}
  end
  if admitted-route.changed>150 then
   return true,framedFinish(false,'Original third roof jump did not reach the far floor',finish)
  end
  return true
 end
 return false
end
'''


def negative():
    full, diagnostic = (read(PRIOR / 'capture' / file)
                        for file in ('full11.json', 'prince-diagnostic.json'))
    assert full['ROM_sha256'] == diagnostic['ROM_sha256'] == PIN
    assert not full['passed'] and full['reason'] == 'Actual original source or native death'
    assert (full['admitted'], full['state']['world_x'], full['HP'], full['final_lives']) == (1265, 853, 0, 2)
    contact, = diagnostic['first_pipe_route']['precontacts']
    assert (contact['camera'], contact['pad'], contact['behavior']) == (729, 1, 0)
    assert contact['native_player_world'] == [855, 184, 867, 208]
    assert contact['native_enemy_world'] == [863, 198, 873, 204]
    assert (contact['enemy']['id'], contact['native_DY'], contact['easy_descending']) == (6, 255, 0)
    debits = diagnostic['first_pipe_route']['HP_bus_writes'][1:]
    assert [(q['PC'], q['write_value']) for q in debits] == [(0xa345, n) for n in (4, 3, 2, 1, 0)]
    return contact


def terrain(x, y):
    if y >= 208:
        return 0x54
    for left, top in ((96, 160), (224, 144), (400, 144)):
        if left <= x < left + 32 and y >= top:
            return (0x12 if y < top + 16 else 0x14) + int(x >= left + 16)
    return 0


def crossing(env, seed, labels, right, earliest):
    model = N.fork(seed)
    Seam.terrain(model, terrain)
    Seam.layout(model, right - 255, 678, scroll=0)
    Route.install_group(model)
    stage = 'approach'
    events = []
    birth = None
    pads = dict(approach=1, settle=0, up=8, ledge=9, climb=8, roof=1, takeoff=129, flight=1)

    def move(target):
        nonlocal stage, change
        events.append(dict(stage=target, **q))
        stage, change = target, tick

    change = 0
    for tick in range(440):
        q = Recovery.sample(model, tick)
        x, y = q['x'], q['y']
        if len(q['actors']) == 2 and birth is None:
            birth = q
        if q['hp'] == 0 or q['lives'] != 2 or q['engine'] != 8:
            break
        support = Recovery.grounded(model, q)
        on_cap = support and x + 13 >= 736 and x < 768 and abs(y - 112) <= 2
        if stage == 'approach' and x >= 690:
            move('settle')
        elif stage == 'settle' and support and q['frame'] == 15 and q['mode'] == 0 and not q['a_lock']:
            move('up')
        elif stage in ('up', 'ledge') and (q['mode'] in (2, 6) or q['action'] == 10):
            move('climb')
        elif stage == 'up' and tick - change >= 55:
            move('ledge')
        elif stage == 'climb' and on_cap:
            move('roof')
        elif stage == 'roof' and earliest is not None and earliest <= x <= 760 and on_cap and Recovery.running(model, q):
            move('takeoff')
        elif stage == 'takeoff' and q['action'] == 4:
            move('flight')
        elif stage in ('roof', 'flight') and x >= 875 and y == 176 and support:
            if birth and q['actors'] and all(a['x'] + 13 < x + 2 for a in q['actors']):
                move('clear')
                break
        Route.controls(env, model, labels, pads[stage])
    return dict(initial_right=right, takeoff_min=earliest, outcome=stage,
                actual_group=birth, events=events, end=q)


def controller():
    text = (PRIOR / 'controller.lua').read_text(encoding='utf-8')
    text = once(text, 'local function fullTick(finish)', ROOF + '\nlocal function fullTick(finish)')
    text = once(text, "local function framedFinish(ok,why,finish)\n cameraWrite(ok,why)",
                "local function framedFinish(ok,why,finish)\n route.third_group=thirdGroup\n cameraWrite(ok,why)")
    text = once(text, " local age=admitted-(route.changed or route.start)",
                """ local age=admitted-(route.changed or route.start)
 if route.index>=3 and not thirdGroup.clear and #thirdGroup.births==2 and x>=872
    and s.native_y==176 and support then
  local a,b=groupActor(thirdGroup.births[1].slot),groupActor(thirdGroup.births[2].slot)
  if a.flag==1 and b.flag==1 and a.id==6 and b.id==6 and (a.state&32)==0 and (b.state&32)==0
      and a.x+13<x+2 and b.x+13<x+2 then
   thirdGroup.clear={Main=admitted,frame=frame,player=s,actors={a,b}}
  end
 end""")
    text = once(text, " if o and x>=o.right+16 and support then",
                """ if o and x>=o.right+16 and support then
  if o.left==736 then
   local j=route.third_roof
   if not j or not j.admission or j.minimum_foot>=144 or s.native_y~=176 then
    return framedFinish(false,'Third pipe lacks the actual supported running A and far-side floor',finish)
   end
   j.far_ground=s;j.far_ground_Main=admitted
  end""")
    text = once(text, " if route.mode=='pipe-cross' then route.pad={'right'};return end",
                """ if thirdRoof(s,o,support,finish) then return end
 if route.mode=='pipe-cross' then route.pad={'right'};return end""")
    assert 'emu.write(' not in text and text.count(PIN) == 1
    sys.path.insert(0, str(R / 'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def stage(out, inputs, receipt):
    ready = read(PRIOR / 'ready.json')
    assert ready['ROM_sha256'] == PIN and not ready['emulated_writes']
    refs = {Path(__file__), receipt, *inputs, *checked(ready['bindings'])}
    scope = 'Original third-pipe running A from actual supported cap. No camera-driven input. '
    prepare(out / 'native', ROM, controller(), refs, expected=PIN, timeout=ready['timeout'],
            allow_interactive=ready['allow_interactive'], rom_symbols=SYMBOLS,
            scope=scope + 'Exact bd9f control-only retry.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out == OUT
    direct = checked(PINS)
    terminal = negative()
    raw = ROM.read_bytes()
    assert sha(ROM) == PIN
    assert not (out / 'native').exists()
    template, _, _ = Route.Current.current()
    env, seed, labels, reference = Climb.Earned.fixture(dict(template, raw=raw))
    earlier = out / 'cpu.json'
    assert sha(earlier) == '9a6c363b104f9ef8a63e82388d5b285004c64290cb6207edba7824ddd885f15e'
    historical = read(earlier)
    assert historical['ROM_sha256'] == PIN and historical['negative_native_contact'] == terminal
    cases = []
    for right, earliest in ((811, None), (811, 745)):
        result = crossing(env, seed, labels, right, earliest)
        cases.append(result)
        print(right, earliest, result['outcome'], result['end']['x'], result['end']['hp'],
              [(q['stage'], q['epoch'], q['x'], q['camera_right']) for q in result['events']], flush=True)
    assert cases == historical['cases'][:2]
    original, chosen = cases
    assert original['actual_group'] and original['end']['hp'] == 0
    assert chosen['outcome'] == 'clear' and (chosen['end']['hp'], chosen['end']['lives']) == (5, 2)
    assert [q['x'] for q in chosen['events'] if q['stage'] in ('takeoff', 'flight')] == [745, 745]
    out.mkdir(exist_ok=True)
    refs = (Path(__file__), Path(Climb.__file__), Path(Route.__file__), ROM, earlier)
    receipt = out / 'cpu-v5.json'
    receipt.write_text(json.dumps(dict(
        ROM_sha256=PIN, controller_only_after_explicit_CPU_scene_setup=True, native_pending=True,
        negative_native_contact=terminal, source_seed=reference, cases=cases,
        scope='Cold Prince GameLoop, translated left approach, authored pipe and native enemy parser. '
              'The camera then scrolls only through the normal controller and qualified native worker.',
        bindings={str(p.relative_to(R)): sha(p) for p in refs}), indent=2)+'\n', encoding='utf-8')
    stage(out, {*direct, *refs}, receipt)


if __name__ == '__main__':
    main()
