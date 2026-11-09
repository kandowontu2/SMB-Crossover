"""Stage earlier native injury so the jump can rise before the pipe wall."""

import argparse
import json
from pathlib import Path
import sys

import prepare_mini_injury_helper_native_1110 as V1


V3 = V1.R/'build/mini-injury-helper-v3-native-1110'
NEGATIVE = V3/'capture/result.json'
COLUMN = V1.R/'build/native-column-palette-1110/proof.json'


def staged_approach(text):
    text = V1.unique(text,'   state=read(0x1f+slot),x=',
        '   state=read(0x1f+slot),direction=read(0x53f+slot),x_speed=read(0x47+slot),x=')
    text = V1.unique(text,'   input=read(0xdc),support=',
        '   input=read(0xdc),x_speed=read(0x46),state=r("Player_State"),support=')
    text = V1.unique(text,'  route_pad={right=true,b=true,a=injury.jump_request~=nil}', '''  if injury.braking and injury.airborne then
   local x,y=player_x(),r('Player_Y_Position')
   if y<=107 or (y<=133 and x<715) then
    injury.braking=false
    injury.brake_release=snapshot_native()
   end
  end
  route_pad={right=not injury.braking,left=injury.braking,b=true,a=injury.jump_request~=nil}''')
    text = V1.unique(text,'  keep_holding_right()\n  if updates%8==0 and #injury.approach<48 then', '''  if not injury.coast and s.x>=687*16 then
   check(s.nativeState==0 and s.nativeY==176,'Coast begins on the ground west of the tall pipe')
   injury.coast=snapshot_native()
  end
  if injury.coast and s.vx==0 and not injury.meet then
   local q=snapshot_native()
   if not injury.parked then injury.parked=q end
   for slot=0,5 do
    local enemy=actor(slot)
    local gap=enemy.x-q.x
    if enemy.flag==1 and enemy.id==6 and enemy.state==0 and enemy.direction==2
     and enemy.x<=730 and gap>=6 and gap<=17 and enemy.y==184 then
     injury.meet=q
     injury.meet.enemy=enemy
     break
    end
   end
  end
  if injury.coast and not injury.meet then route_pad={} else keep_holding_right() end
  if updates%8==0 and #injury.approach<48 then''')
    text = V1.unique(text,'  q.enemy=enemy\n  injury.force=q\n  keep_holding_right()', '''  q.enemy=enemy
  injury.force=q
  check(injury.parked and injury.meet and q.x<=711 and q.side_hold==0,
   'Earlier real side contact leaves jump room and a clear camera')
  injury.braking=q.x_speed>=16 and q.x_speed<128 and q.x>=702
  keep_holding_right()''')
    text = V1.unique(text,"   check(injury.force~=nil,'Engine10 must follow actual powered contact')",
        "   check(injury.force~=nil,'Engine10 must follow actual powered contact')\n"
        "   check(read(0x0782)==0,'Native injury starts without a pipe-side hold')")
    return text


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom',type=Path,required=True)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    text,ready_path,ready = V1.bound_template(V3/'controller.lua')
    for path,digest in ready['bindings'].items():
        assert V1.sha(path)==digest,path
    old = Path(ready['ROM'])
    q = json.loads(NEGATIVE.read_text(encoding='utf-8'))
    assert q['ROM_sha256']==ready['ROM_sha256'] and not q['passed']
    injury = q['injury_helper']
    assert injury['jump_ack']['input']&128 and injury['airborne']['y']<injury['jump_ack']['y']
    assert injury['post_control'][-1]['right']==852 and injury['post_control'][-1]['side_hold']==16
    rom = args.rom.resolve()
    expected = V1.sha(rom)
    metadata = rom.with_suffix('.json')
    info = json.loads(metadata.read_text(encoding='utf-8'))
    assert info['candidate_SHA256']==expected
    raw = rom.read_bytes()
    rebuilt = bytearray(old.read_bytes())
    column = json.loads(COLUMN.read_text(encoding='utf-8'))
    assert column['passed']
    if rom!=old:
        for patch in column['patches']:
            off = patch['file_offset']
            before,after = (bytes.fromhex(patch[key]) for key in ('old_hex','new_hex'))
            assert rebuilt[off:off+len(before)]==before and len(before)==len(after)
            rebuilt[off:off+len(after)] = after
        assert rebuilt==raw,'Only the shared column renderer may differ from the v3 ROM'
    text = V1.unique(text,f'["ROM_sha256"]="{ready["ROM_sha256"]}"',f'["ROM_sha256"]="{expected}"')
    text = staged_approach(text)
    for physical, values in V1.PRG_HOOK.findall(text):
        at = 16+int(physical)
        want = bytes(map(int,values.split(',')))
        assert raw[at:at+len(want)]==want,(hex(at),want.hex())
    sys.path.insert(0,str(V1.LUA))
    from lupa.lua54 import LuaRuntime

    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    refs = {Path(__file__),ready_path,NEGATIVE,COLUMN,metadata,*map(Path,ready['bindings'])}
    V1.prepare(args.output,rom,text,refs,expected=expected,timeout=180,
               allow_interactive=ready['allow_interactive'],
               scope='Earned mushroom and earlier contact with the pipe-side Goomba after it turns. '
                     'The acknowledged native jump must leave the camera free to cross the X864 '
                     'helper’s offscreen and visible edges during the same injury. Input only.')


if __name__=='__main__':
    main()
