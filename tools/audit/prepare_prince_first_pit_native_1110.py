"""Bind Prince's native first-pit turn, run-up and original A replay."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import check_prince_first_pit_late_1110 as Late
from deliver_helper_camera_render_1110 import bindings
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


Pit, R, N, Route, Recovery = Late.Pit, Late.R, Late.N, Late.Route, Late.Recovery
PRIOR = R/'build/prince-fourth-pipe-native-1110'
PINS = {
    PRIOR/'ready.json': '9fc449707bfa40ee538b6ec2af151867d52ffd8543eaf14bcc3c9224bc8e224b',
    PRIOR/'controller.lua': '8aed2c9e58cf300326a9ef3815bd7f59e041c7d54efbef8b1c2de6d88d3528d4',
    Late.EARLY: Late.EARLY_SHA,
    Late.EARLY.with_name('late.json'): 'f72541b60fd4c75946ae9c59d15f1350ec72ca774bcfcf8ebcd31069cbe05168',
    Late.EARLY.with_name('camera.json'): '65e427fad7907f42fd401552801d66bdde19379ce61cc23a7a83ea08ecd74ebd',
}
BRAKE_RIGHT, BRAKE_LEFT, ARM, HEADROOM = 1048, 1040, 1059, 62


def qualify():
    template, _, _ = Pit.Current.current()
    raw = Route.ROM.read_bytes()
    assert sha256(raw).hexdigest() == Route.PIN
    base = dict(template, raw=raw)
    env, model, labels, _ = Pit.start(base, Pit.authored(base))
    stage = 'initial'
    states = []
    pads = {'initial': 1, 'brake-right': 0, 'left': 2, 'brake-left': 0, 'run-up': 1}
    for epoch in range(420):
        q = Late.sample(model, epoch)
        x = q['x']
        idle = q['frame'] == 15 and q['mode'] == 0 and q['support'] and q['a_lock'] == 0
        assert (q['engine'], q['hp'], q['lives']) == (8, 4, 2)
        previous = stage
        if stage == 'initial' and x >= BRAKE_RIGHT:
            stage = 'brake-right'
        elif stage == 'brake-right' and idle:
            stage = 'left'
        elif stage == 'left' and x <= BRAKE_LEFT and q['facing'] == 0:
            stage = 'brake-left'
        elif stage == 'brake-left' and idle:
            stage = 'run-up'
        elif (stage == 'run-up' and ARM <= x <= 1077 and q['camera_right']-x >= HEADROOM
              and q['phase'] in (0, 1) and Recovery.running(model, q)):
            states.append(dict(stage='A', state=q))
            break
        if stage != previous:
            states.append(dict(stage=stage, state=q))
        assert x < (1081 if stage == 'run-up' else 1095), (stage, q)
        Route.controls(env, model, labels, pads[stage])
    assert [(r['stage'], r['state']['x'], r['state']['camera_right']) for r in states] == [
        ('brake-right', 1049, 1066), ('left', 1071, 1091), ('brake-left', 1040, 1093),
        ('run-up', 1012, 1093), ('A', 1059, 1125)]
    flight = Late.flight(env, model, labels, 'Right')
    assert flight['terminal'] == 'far-ground'
    assert (flight['end']['x'], flight['end']['y'], flight['end']['hp'], flight['end']['lives']) == (1152, 176, 4, 2)
    assert [(p['frame'],p['x'],p['foot']) for p in flight['poses'] if 39<=p['frame']<=43] == [
        (39,1107,213), (40,1131,206), (41,1142,201), (42,1147,193), (43,1152,211)]
    return dict(states=states, flight=flight)


WITNESS = r'''
local function writeFirstPit(ok,why)
 if route.first_pit_written then return end
 route.first_pit_written=true
 writejson('first-pit.json',{passed=ok,reason=why,ROM_sha256=Q.ROM_sha256,route=route.first_pit,
   controller_only=true,emulated_writes=false,state=state(),frame=frame,
   initial_lives=initialLives,final_lives=r('NumberofLives')})
end
'''


CONTROL = r'''
local function firstPitTurn(s,o,support)
 if not o or o.kind~='pit' or o.left~=1104 then return false end
 local p=route.first_pit
 local x=s.world_x
 if not p then
  p={stage='initial',events={}}
  route.first_pit=p
 end
 if p.stage=='flight' then return false end
 local left,right=currentEdges()
 local function change(stage,pad)
  p.stage=stage
  p.changed=admitted
  p.events[#p.events+1]={stage=stage,Main=admitted,state=s,camera_left=left,camera_right=right,support=support}
  route.pad=pad
  routeLog('first-pit-'..stage)
 end
 if p.changed and admitted-p.changed>155 then routeFail('First-pit original turn exceeded its phase bound')end
 if p.stage=='initial' then
  route.pad={'right'}
  if x>=BRAKE_RIGHT then change('brake-right',{})end
 elseif p.stage=='brake-right' then
  route.pad={}
  if idleReady(s) and support then change('left',{'left'})end
 elseif p.stage=='left' then
  route.pad={'left'}
  if x<=BRAKE_LEFT and s.source_facing==0 then change('brake-left',{})end
 elseif p.stage=='brake-left' then
  route.pad={}
  if idleReady(s) and support then change('run-up',{'right'})end
 elseif p.stage=='run-up' then
  route.pad={'right'}
  if x>=ARM and x<=1077 and right-x>=HEADROOM and (s.phase&3)<=1
      and support and runReady(s) and s.source_facing==255 then
   if not solid(1088,208) or solid(1104,208) or solid(1120,208) or not solid(1136,208) then
    routeFail('First-pit takeoff lacks the actual native two-tile gap')
   end
   change('flight',{'right','a'})
   p.request=p.events[#p.events]
   routeMode('takeoff',{'right','a'});return true
  end
  if x>=1081 then routeFail('First-pit run-up did not establish camera room and actual support')end
 end
 if x>=1095 then routeFail('First-pit turn approached the lip before takeoff')end
 return true
end
'''


def controller():
    text = (PRIOR/'controller.lua').read_text(encoding='utf-8')
    text = once(text, 'local function routeWrite(ok,why)', WITNESS + '\nlocal function routeWrite(ok,why)\n'
                ' if not route.first_pit_written then writeFirstPit(false,why) end')
    control = CONTROL
    for name, value in (('BRAKE_RIGHT',BRAKE_RIGHT),('BRAKE_LEFT',BRAKE_LEFT),('ARM',ARM),('HEADROOM',HEADROOM)):
        control = control.replace(name, str(value))
    text = once(text,'local function fullTick(finish)', control + '\nlocal function fullTick(finish)')
    text = once(text, ' if fourthCapHop(s,o,support) then return end',
                ' if firstPitTurn(s,o,support) then return end\n if fourthCapHop(s,o,support) then return end')
    text = once(text, "  routeLog('supported-far-side')", """  if o.kind=='pit' and o.left==1104 then
   local p=route.first_pit
   if not p or not p.request or not p.request.support or not p.admission or p.admission.source_action~=4
       or s.native_y~=176 or s.native_y_high~=1 or not support or not solid(s.world_x+2,208) then
    routeFail('First pit lacks actual original running A and native far-bank support')
   end
   p.far_ground=s
   writeFirstPit(true,'Actual original running A crossed the first native pit after a supported turn and run-up')
  end
  routeLog('supported-far-side')""")
    text = once(text, "   routeMode('aerial',{'right'})\n  elseif age>28 then", """   if o and o.kind=='pit' and o.left==1104 and route.first_pit then route.first_pit.admission=s end
   routeMode('aerial',{'right'})
  elseif age>28 then""")
    text = once(text, "  if s.source_action~=4 and age>=12 and support then", """  if s.source_action~=4 and age>=12 and support then
   if o and o.kind=='pit' and o.left==1104 and x+13<o.left then
    route.first_pit.short_landing=s
    routeFail('First-pit original jump returned to the near bank')
   end""")
    text = once(text, 'or not route.fourth_hop or not route.fourth_hop.far_ground then',
                'or not route.fourth_hop or not route.fourth_hop.far_ground\n'
                '      or not route.first_pit or not route.first_pit.far_ground then')
    assert text.count(Route.PIN) == 1 and 'emu.write(' not in text
    sys.path.insert(0,str(Route.Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    for p, digest in PINS.items():
        assert sha(p) == digest, p
    prior = Pit.Current.read(PRIOR/'ready.json')
    assert prior['ROM_sha256'] == Route.PIN and not prior['emulated_writes']
    bindings(prior['bindings'])
    negative = Pit.actual_failure()
    positive = qualify()
    source = controller()
    refs = {Path(__file__), Path(Late.__file__), Path(Pit.__file__), *PINS, *map(Path,prior['bindings']),
            *(R/p for p in Pit.Current.read(Late.EARLY)['bindings'])}
    out.mkdir()
    proof = out/'turn-evidence.json'
    proof.write_text(json.dumps(dict(passed=True,ROM_SHA256=Route.PIN,controller_only=True,ROM_written=False,
                      Mesen_run=False,native_negative=negative,CPU_route=positive,
                      scope='Actual original controls and native parser geometry on the CPU. '
                            'The fourth-pipe landing is the prior explicit CPU terrain fixture.',
                      bindings={p.relative_to(R).as_posix():sha(p) for p in sorted(refs)}),indent=2)+'\n',encoding='utf-8')
    prepare(out/'native', Route.ROM, source, refs|{proof}, expected=Route.PIN, timeout=prior['timeout'],
            allow_interactive=prior['allow_interactive'],
            scope='Original supported stop, left turn and running A at the first pit. '
                  'All prior third, pair, fourth and full-stage witnesses remain bound.')
    assert sum(p.is_file() for p in out.rglob('*')) == 4


if __name__ == '__main__':
    main()
