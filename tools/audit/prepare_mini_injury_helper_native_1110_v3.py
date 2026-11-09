"""Wait for native injury to regain ground before requesting the jump edge."""

import argparse
import json
from pathlib import Path
import sys

import prepare_mini_injury_helper_native_1110 as V1


V2 = V1.R/'build/mini-injury-helper-v2-native-1110'
NEGATIVE = V2/'capture/result.json'


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    text,ready_path,ready = V1.bound_template(V2/'controller.lua')
    rom = Path(ready['ROM'])
    q = json.loads(NEGATIVE.read_text(encoding='utf-8'))
    assert q['ROM_sha256']==ready['ROM_sha256'] and not q['passed']
    assert q['injury_helper']['start']['timer']==239 and not q['injury_helper']['native_steps']
    assert not q['injury_helper'].get('jump_request')
    assert V1.sha(rom)==ready['ROM_sha256']
    for path,digest in ready['bindings'].items():
        assert V1.sha(path)==digest,path

    text = V1.unique(text,"   check(injury.start.input&0x80==0 and read(0x055b)&0x80==0,\n"
        "    'A is released before requesting the native jump')\n"
        "   check(r('Player_State')==0,'Native injury jump starts on solid ground')\n"
        "   injury.jump_request=injury.start\n   keep_holding_right()\n  end",'''  end
  -- ForceInjury sets native Player_State=1 before the timed freeze.
  -- Wait for native background collision to put the feet back on ground.
  if not injury.jump_request and r('Player_State')==0 then
   local request=snapshot_native()
   check(request.input&0x80==0 and read(0x055b)&0x80==0,
    'A is released before requesting the native jump')
   check(request.timer>=0xe0 and request.right<856,
    'Ground returns early enough to attempt the injury jump')
   injury.jump_request=request
   keep_holding_right()
  end''')
    sys.path.insert(0,str(V1.LUA))
    from lupa.lua54 import LuaRuntime

    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    refs = {Path(__file__),ready_path,NEGATIVE,*map(Path,ready['bindings'])}
    V1.prepare(args.output,rom,text,refs,expected=ready['ROM_sha256'],timeout=180,
               allow_interactive=ready['allow_interactive'],
               scope='Earned mushroom and side injury. The controller waits for restored native ground, '
                     'then requests an acknowledged jump over the pipe and witnesses offscreen X864 '
                     'construction and visible entry during the same injury. Input only.')


if __name__=='__main__':
    main()
