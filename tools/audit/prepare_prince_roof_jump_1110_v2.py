"""Replay the original running jump from the third pipe on exact Prince 50a6."""

import argparse
import csv
import json
from pathlib import Path
import sys

import check_prince_run_support_funded_irq_1110 as Model
from check_prince_player_pipeline_1102_v67 import terrain
from deliver_helper_camera_render_1110 import bindings
from prepare_prince_full11_1110 import once
import prepare_prince_run_support_native_1110 as Stage
from prepare_selected_native_packet_v1 import prepare, sha


R,Current,P,N,I = Model.R,Model.Current,Model.P,Model.N,Model.I
ROOT = R/'build/prince-run-support-native-1110'
PACKET = ROOT/'native'
CAPTURE = PACKET/'capture'
ROM = ROOT/'prince-private.nes'
MANIFEST = ROOT/'candidate.json'
LEVEL = R/'src/level_tiles.s'
INPUTS = {
    'third-pipe.json':'fb443269f5abc660cae5bd98f094da96853cc3264581fd72ef87711ff5ec6d0c',
    'full11.json':'9faabdbb4bdd0b2ebdb7127392ff80eb66fa6b602355b510c8ef23afc53443c7',
    'prince-diagnostic.json':'38c6fad853ca886dff8020de65e2a2d357d9fd321d35ff9a0b46d71b252cd56f',
    'binding.json':'0f6c4169a86bb486cf7e781d3d0c1c846d2e6de66780c6be48c974d64ea4512f',
    'full11-route.csv':'da21cbf35c182cf34bbfa4fc4db8f2adfd084e9da5bdd5e536c4ccf0ba32281a',
}

ROOF_JUMP = '''
local function roofJump(s,o,support)
 if o.left~=736 or not route.on_top then return false end
 if route.mode=='pipe-cross' and not route.third_jump and s.world_x>=745 and s.world_x<=752
    and s.native_y>=111 and s.native_y<=115 and support and runReady(s) then
  route.third_jump={takeoff=s,takeoff_Main=admitted,minimum_foot=s.physical_foot,maximum_x=s.world_x,nearby={}}
  routeMode('third-roof-takeoff',{'right','a'});return true
 end
 if route.mode=='third-roof-takeoff' then
  route.pad={'right','a'}
  if s.source_action==4 then
   route.third_jump.admission=s;route.third_jump.admission_Main=admitted
   routeMode('third-roof-flight',{'right'})
  elseif admitted-route.changed>28 then routeFail('Third roof did not admit genuine original running A')end
  return true
 end
 if route.mode=='third-roof-flight' then
  local jump=route.third_jump
  jump.minimum_foot=math.min(jump.minimum_foot,s.physical_foot)
  jump.maximum_x=math.max(jump.maximum_x,s.world_x)
  if admitted%4==0 and s.world_x>=780 and #jump.nearby<24 then
   for slot=0,5 do
    local id=ram(L.Enemy_ID+slot);local flags=ram(L.Enemy_Flag+slot)
    local x=ram(L.Enemy_X_Position+slot)+256*ram(L.Enemy_PageLoc+slot)
    if flags==1 and id<=6 and math.abs(x-s.world_x)<=48 and #jump.nearby<24 then
     jump.nearby[#jump.nearby+1]={Main=admitted,source_x=s.world_x,source_foot=s.physical_foot,
      enemy_slot=slot,enemy_id=id,enemy_x=x,enemy_y=ram(L.Enemy_Y_Position+slot)}
    end
   end
  end
  route.pad={'right'}
  if admitted-route.changed>150 then routeFail('Original roof-jump fall did not reach native far-side support')end
  return true
 end
 return false
end
'''


def native_evidence():
    for name,digest in INPUTS.items():
        assert sha(CAPTURE/name)==digest,name
    witness,full,diagnostic,native = (Current.read(CAPTURE/name) for name in (
        'third-pipe.json','full11.json','prince-diagnostic.json','binding.json'))
    assert witness['ROM_sha256']==full['ROM_sha256']==diagnostic['ROM_sha256']==native['ROM_sha256']==Stage.PIN
    assert not witness['passed'] and not full['passed'] and native['exit_code']==1
    assert full['state']['world_x']==800 and full['HP']==0 and full['route']['index']==2
    assert full['route']['max_x']==802 and full['route']['mode']=='pipe-cross'
    hits = witness['source_support_publications']
    assert [p['before']['source_mode'] for p in hits]==[255,1,1,1,1]
    assert all(p['surface']==144 and p['query_x']==736 and p['cap_tile']==18 for p in hits)
    assert witness['physical_support']['world_x']==723 and witness['original_hang']['source_mode']==2
    contact, = diagnostic['first_pipe_route']['precontacts']
    changes = diagnostic['first_pipe_route']['HP_bus_writes'][1:]
    assert [p['write_value'] for p in changes]==[4,3,2,1,0]
    assert all(p['Main']==contact['Main']==1280 and p['PC']==0xa345 for p in changes)
    assert contact['native_enemy']['id']==6 and contact['native_enemy']['x']==807
    assert (contact['behavior'],contact['native_DY'],contact['native_state'],contact['physical_foot'])==(0,0,2,204)
    assert contact['native_enemy_world'][1]==198 and contact['native_player_world'][2]>=contact['native_enemy_world'][0]
    with (CAPTURE/'full11-route.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    actual, = [r for r in rows if r['Main']=='1224']
    assert (actual['X'],actual['Y'],actual['source_action'],actual['source_frame'],actual['source_mode'])==('745','112','1','6','1')
    native_level = bytes.fromhex('1ec2006b068b8663b70f05030623064bb7bb005bb7fb373bb70f0b1b37ff')
    assert ROM.read_bytes()[19023:19023+len(native_level)]==native_level
    source = LEVEL.read_text(encoding='utf-8')
    assert 'adc #$30\n        and #%11110000' in source and 'adc #$18                  ;add 24 pixels for next enemy' in source
    return dict(cap_publications=len(hits),fatal_source_HP=[5,4,3,2,1,0],native_contact=contact,
                actual_roof_run_pose={k:int(actual[k]) for k in ('Main','X','Y','source_action','source_frame','source_mode')})


def cpu_jump():
    old,_,_ = Current.current()
    raw = ROM.read_bytes()
    assert P.sha(raw)==Stage.PIN
    base = dict(old,raw=raw)
    seed,_ = P.Q.C.C.cold(base,38)
    e,m,labels = P.Q.first8(base,seed)

    def pipe(x,y):
        if y>=208:
            return 0x54
        if not 192<=x<224 or y<144:
            return 0
        return (0x12 if y<160 else 0x14)+int(x>=208)

    terrain(m,pipe)
    rows = {}
    pad = 1
    for epoch in range(380):
        s = Current.row(m,epoch)
        assert s['hp']==5 and s['lives']==2 and s['engine']==8
        if epoch==77:
            pad = 0
        if epoch==113:
            pad = 8
        if epoch==217:
            pad = 1
        if epoch==257:
            assert (s['x'],s['y'],s['action'],s['frame'],s['mode'],s['native_state'])==(201,112,1,6,1,0)
            rows['takeoff'] = s
            pad = 129
        if 'takeoff' in rows and 'admission' not in rows and s['action']==4:
            rows['admission'] = s
            pad = 1
        if 'admission' in rows and ('apex' not in rows or s['foot']<rows['apex']['foot']):
            rows['apex'] = s
        if 'admission' in rows and s['x']>=224+16 and s['y']==176 and s['native_state']==0:
            rows['far_ground'] = s
            break
        m.controller_pad = pad
        N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
        e['run'](m,'GameLoop',labels)
    assert (rows['admission']['epoch'],rows['apex']['x'],rows['apex']['foot'])==(259,303,130)
    assert (rows['far_ground']['x'],rows['far_ground']['y'],rows['far_ground']['epoch'])==(347,176,324)
    return dict(translated_world_X_offset=544,exact_ROM_SHA256=Stage.PIN,controller_only_after_cpu_terrain=True,
                explicit_terrain='Native typed 64px pipe and flat far side; no enemy actors seeded',checkpoints=rows)


def rebind(source):
    source = once(source,'local function fullTick(finish)',ROOF_JUMP+'\nlocal function fullTick(finish)')
    source = once(source," if route.mode=='pipe-cross' then\n  route.pad={'right'}",
                  " if o and roofJump(s,o,support) then return end\n if route.mode=='pipe-cross' then\n  route.pad={'right'}")
    source = once(source,'  terminal=state(),Main=admitted,frame=frame,initial_lives=initialLives,final_lives=r(\'NumberofLives\')})',
                  '  roof_jump=route.third_jump,terminal=state(),Main=admitted,frame=frame,initial_lives=initialLives,final_lives=r(\'NumberofLives\')})')
    source = once(source,"   if not last or not last.after or route.third_support_pending or not route.hang or s.native_y~=176 then",
                  "   local jump=route.third_jump\n   if not last or not last.after or route.third_support_pending or not route.hang or s.native_y~=176\n"
                  "     or not jump or not jump.admission or jump.minimum_foot>=144 then")
    assert 'emu.write(' not in source and source.count(Stage.PIN)==1
    sys.path.insert(0,str(Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime

    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    ready_path,control = PACKET/'ready.json',PACKET/'controller.lua'
    ready,bound = Current.read(ready_path),Current.read(CAPTURE/'binding.json')
    assert ready['ROM_sha256']==sha(ROM)==Stage.PIN and bound['ready_sha256']==sha(ready_path)
    assert Current.read(MANIFEST)['candidate_SHA256']==Stage.PIN and not ready['emulated_writes']
    bindings(ready['bindings'])
    native,cpu = native_evidence(),cpu_jump()
    source = rebind(control.read_text(encoding='utf-8'))
    refs = {Path(__file__),LEVEL,MANIFEST,ready_path,control,*(CAPTURE/name for name in INPUTS),*map(Path,ready['bindings'])}
    out.mkdir()
    evidence = out/'roof-jump-plan.json'
    record = dict(passed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Stage.PIN,negative=native,cpu_fixture=cpu,
                  native_pending=True,scope='Original action4 on supported third cap; same full route and strict separate landing witness.',
                  bindings={str(path.resolve()):sha(path) for path in sorted(refs)})
    evidence.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    prepare(out/'native',ROM,source,refs|{evidence},expected=Stage.PIN,timeout=ready['timeout'],
            scope='Exact 50a6. Original running A from the supported third cap. Separate third-pipe and full-stage results.',
            allow_interactive=ready['allow_interactive'])
    assert sum(path.is_file() for path in out.rglob('*'))==4


if __name__=='__main__':
    main()
