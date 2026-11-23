"""Separate earned-Mushroom-to-Flower controller on the private Giant repair.

Preserves the frozen first-Mushroom factory.  Root alone may use --run, in the
existing two-file slot.  All other modes compile in memory and print hashes.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import run_mega_giant_pickups_native_1123 as M
from check_ff_stdout_controller_source_1110 import LuaRuntime

PARENT_SOURCE = 'be8a05a62f78c8dde4ec448ff5fb8b378e4ac1ee05ed063d9c92d9eb3310978f'
FLOWER_SOURCE = '52d16533e5c033c72a28624c78384cb9448d3be26a0714a2857b2b6de8a87da5'
H = lambda data: sha256(data).hexdigest()


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


TRAVEL = r'''
local heldUntil,routeStarted=0,false
local routeFlags,jumps={},{}
local function choose()
 if tier==1 then return {right=true}end
 if completion then return {}end
 local xx,y=x(),r('Player_Y_Position')
 local ground,speed=r('Player_State')==0,r('Player_X_Speed')
 local function launch(key,n)
  routeFlags[key]=true;heldUntil=active+n;jumps[#jumps+1]={reason=key,hero=sample()}
 end
 if r('GameEngineSubroutine')~=8 then return {right=true}end
 if not routeFlags.first_pipe and xx>=395 and xx<430 and ground then launch('first_pipe',35)
 elseif not routeFlags.second_pipe and xx>=580 and xx<607 and ground then launch('second_pipe',40)
 else
  local stop
  for _,p in ipairs({679,853})do if xx>=p and xx<p+32 and not routeFlags[p]then stop=p;break end end
  if stop then
   if ground and y==176 then launch(stop,28)
   else return speed>0 and speed<128 and {left=true}or{}end
  elseif ground and active>=heldUntil then
   for _,p in ipairs({1104,1376})do
    if not routeFlags[p]and xx>=p-30 and xx<p then launch(p,28);break end
   end
  end
 end
 return {right=true,b=true,a=active<heldUntil}
end
'''


def controller(current, out):
    assert H(Path(M.__file__).read_bytes()) == PARENT_SOURCE
    assert H((M.R/'tools/audit/probe_mega_giant_flower_route_1123.py').read_bytes()) == FLOWER_SOURCE
    image, text, proof = M.controller(current, out)
    speed = M.W.address(M.W.Symbols.bundle(), 'Player_X_Speed')
    text = once(text, '["ram"]={', f'["ram"]={{["Player_X_Speed"]={speed},')
    text = once(text, 'local previousActive=0', 'local previousActive=0\nlocal tier,target=1,336\nlocal checkpoints={}')
    text = once(text, 'growth=growth,growth_entries=growthEntries,first_post_age=firstPostAge,',
        'checkpoints=checkpoints,tier=tier,growth=growth,growth_entries=growthEntries,first_post_age=firstPostAge,')
    text = once(text, "assert(x()>=300 and x()<=310 and r('Player_Y_Position')==176,'Real first block reach')",
        "assert(x()>=target-32 and x()<=target-20 and r('Player_Y_Position')<=176\n   and r('Player_Y_Position')>=80,'Real authored item block reach')")
    text = once(text, "assert(x()==336 and r('Player_Y_Position')==144,'Existing native Giant source-cell projection')",
        "assert(x()==target and r('Player_Y_Position')==144,'Existing native Giant source-cell projection')")
    text = once(text, 'a.id==46 and a.kind==0 then', 'a.id==46 and a.kind==tier-1 then')
    text = once(text, "assert(marks.native_head and a.x==336 and a.y<=144 and a.state>=1,'Actual block-born Mushroom')",
        "assert(marks.native_head and a.x==target and a.y<=144 and a.state>=1,'Actual authored block-born upgrade')")
    text = once(text, 'a.id==46 and a.kind==0 and a.state>=6 then', 'a.id==46 and a.kind==tier-1 and a.state>=6 then')
    text = once(text, "assert(r('PlayerStatus')==0 and r('NumberofLives')==2,'Healthy unpowered true collection')",
        "assert(r('PlayerStatus')==tier-1 and r('NumberofLives')==2,'Healthy earned-tier true collection')")
    text = once(text, "r('GuestPowerupOld')==0 and r('GuestPowerupTarget')==1,",
        "r('GuestPowerupOld')==tier-1 and r('GuestPowerupTarget')==tier,")
    text = once(text, "and r('GuestPowerupAge')==60 and r('PlayerStatus')==1 and r('PlayerSize')==0",
        "and r('GuestPowerupAge')==60 and r('PlayerStatus')==tier and r('PlayerSize')==0")
    text = once(text, "assert(r('PlayerStatus')==1 and r('PlayerSize')==0 and r('GameEngineSubroutine')==8",
        "assert(r('PlayerStatus')==tier and r('PlayerSize')==0 and r('GameEngineSubroutine')==8")
    text = once(text, "finish(true,'Natural Giant Mushroom, sixty growth clocks and twenty-five grounded returns')", """
    checkpoints[#checkpoints+1]={tier=tier,marks=marks,birth=birth,collection=collected,
     growth=growth,growth_entries=growthEntries,first_post_age=firstPostAge,
     growth_completed=completion,resumed=resumed}
    if tier==1 then
     tier,target=2,1248;marks={};birth=nil;collected=nil;growth={};growthEntries={}
     firstPostAge=nil;completion=nil;resumed={}
    else
     finish(true,'Natural Giant Mushroom and Flower, full source growth and grounded continuation')
    end
""")
    text = once(text, "assert(active<600,'Finite first Mushroom approach')", "assert(active<1800,'Finite natural two-upgrade route')")
    text = once(text, 'local function wait(n)', TRAVEL + '\nlocal function wait(n)')
    text = once(text, "emu.setInput(menuReady and {right=true}or pad,0)", "emu.setInput(menuReady and choose()or pad,0)")
    LuaRuntime().compile(text)
    return image, text, proof


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--compile-only', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = ap.parse_args()
    args.output.mkdir(exist_ok=True)
    current = M.Probe.ROM.read_bytes()
    image, text, proof = controller(current, args.output)
    print('GIANT FLOWER READY ' + json.dumps(dict(**proof, Lua_SHA256=H(text.encode()),
        source_SHA256=H(Path(__file__).read_bytes()))), flush=True)
    if args.compile_only:
        assert not list(args.output.rglob('*'))
        return 0
    import run_stdout_mesen_1110 as Native
    from nightly_patch_guard_v1 import check
    target, script = M.SLOT/'candidate.nes', M.SLOT/'controller.lua'
    assert set(M.SLOT.iterdir()) == {target, script} and target.read_bytes() == current
    before = check(M.Probe.ROM)
    assert not before['matching_patch_files']
    Native.require_free_workspace(M.R, target, allow_interactive=True)
    previous = script.read_bytes()
    try:
        target.write_bytes(image)
        script.write_bytes(text.encode())
        result = Native.run(script, target, M.SLOT/'capture', H(image), 240)
        assert result['outputs_written'] == 0 and not result['images']
        print('GIANT FLOWER RESULT ' + json.dumps(result, separators=(',', ':')), flush=True)
        return int(not result['passed'])
    finally:
        script.write_bytes(previous)
        target.write_bytes(current)
        assert set(M.SLOT.iterdir()) == {target, script} and M.Probe.ROM.read_bytes() == current
        assert check(M.Probe.ROM) == before


if __name__ == '__main__':
    raise SystemExit(main())
