"""Root-only natural Star replay on the installed exact6201 Downloads image.

Recover exactc691 only in memory and reconstruct6201 byte-for-byte.  This
launcher never writes a ROM: the native run opens the actual Downloads file.
The existing shared controller is restored from memory after the run.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import run_mega_giant_flower_native_1123 as Flower
import install_mega_giant_item_semantics_1123 as Installed
from check_ff_stdout_controller_source_1110 import LuaRuntime

H = lambda raw: sha256(raw).hexdigest()
FLOWER_PIN = '37c80205fdf01f8dfb633a63e70eaf06e73ed026bf9fd0ee1108e38304628fde'
SOURCE_PROOF = '556560c1ccaccbb4f4d206da56cb5df34d14b8c5197a53136ffba35df50fa76e'
LIFE_PROOF = '2c82cb8634fb143e69845ccc81c93436c81a25a709c72cbd138352bd941dc4bb'
once = Flower.once
M = Flower.M

STAR_OBSERVER = r'''
 if tier==3 and collected then
  assert(r('PlayerStatus')==2 and r('PlayerSize')==0 and r('GuestPowerupActive')==0,
   'Star preserves the two naturally earned upgrade tiers')
  if not completion then
   assert(starWrites.timer and starWrites.music and starWriteOrder==2
    and starWrites.timer.hero.main==collected.hero.main and starWrites.music.hero.main==collected.hero.main,
    'Actual mapped collector wrote Star timer35 and music64')
   assert(r('StarInvincibleTimer')>0,'Native Star remains active after collector Main')
   completion=sample();completion.star_timer=starWrites.timer.value;completion.star_music=starWrites.music.value
   completion.observed_timer=r('StarInvincibleTimer');completion.observed_music=r('AreaMusicQueue')
  else
   assert(r('StarInvincibleTimer')>0 and r('GameEngineSubroutine')==8 and r('Player_State')==0
    and r('Player_Y_Position')==176 and r('Player_Y_HighPos')==1,'Grounded native Star continuation')
   local s=sample();s.star_timer=r('StarInvincibleTimer');resumed[#resumed+1]=s
   if #resumed==25 then
    assert(score()>=collected.hero.score+1000 and x()>completion.x,'Actual Star reward and retained movement')
    checkpoints[#checkpoints+1]={tier=3,marks=marks,birth=birth,collection=collected,
     effect=completion,writes=starWrites,resumed=resumed}
    finish(true,'Natural Giant Mushroom, Flower and Star with actual rewards and grounded continuation')
   end
  end
  return
 end
'''

STAR_WRITES = r'''
hook('starTimerStore',function()
 if tier~=3 or not collected then return end
 assert(not starWrites.timer and starWriteOrder==0,'One actual collected Star timer store')
 armedStarTimer=true
end)
hook('starMusicStore',function()
 if tier~=3 or not collected then return end
 assert(starWrites.timer and not starWrites.music and starWriteOrder==1,'Star music follows real timer store')
 armedStarMusic=true
end)
emu.addMemoryCallback(safe(function(_,value)
 if not armedStarTimer then return end
 assert(tier==3 and collected and value==35 and starWriteOrder==0,'Actual native STA StarInvincibleTimer35')
 armedStarTimer=false;starWriteOrder=1;starWrites.timer={hero=sample(),value=value,pc=C.hooks.starTimerStore.pc}
end),emu.callbackType.write,C.ram.StarInvincibleTimer)
emu.addMemoryCallback(safe(function(_,value)
 if not armedStarMusic then return end
 assert(tier==3 and collected and value==64 and starWriteOrder==1,'Actual native STA AreaMusicQueue64')
 armedStarMusic=false;starWriteOrder=2;starWrites.music={hero=sample(),value=value,pc=C.hooks.starMusicStore.pc}
end),emu.callbackType.write,C.ram.AreaMusicQueue)
'''


def controller(current, out, kind='star'):
    assert H(Path(Flower.__file__).read_bytes()) == FLOWER_PIN
    assert H((M.R/'tools/audit/probe_mega_giant_star_route_1123.py').read_bytes()) == SOURCE_PROOF
    if H(current) == Installed.CANDIDATE:
        parent = Installed.recover_parent(current)
        assert H(parent) == M.DK
    else:
        assert H(current) == M.DK
        parent = current
    image, text, proof = Flower.controller(parent, out)
    assert H(image) == Installed.CANDIDATE and Installed.recover_parent(image) == parent
    if H(current) == Installed.CANDIDATE:
        assert image == current
    b = M.W.Symbols.bundle()
    if kind == 'life':
        assert H((M.R/'tools/audit/probe_mega_giant_life_route_1123.py').read_bytes()) == LIFE_PROOF
        text = life_controller(text)
        LuaRuntime().compile(text)
        assert H(text.encode()) == '0c19304603d558bc87fdb8e1b9769c9f635bf4064c5790ca5052231ed2909a57'
        return image, text, dict(**proof, actual_Downloads_SHA256=H(current),
            reconstructed_installed_image_equal=H(current)==H(image), ROM_writes=False)
    assert kind == 'star'
    extra = ''.join(f'[{json.dumps(name)}]={M.W.address(b,name)},' for name in ('StarInvincibleTimer', 'AreaMusicQueue'))
    text = once(text, '["ram"]={', '["ram"]={'+extra)
    # Bind the actual two STA instructions, not a delayed queue snapshot.
    # They execute only after the real mature actor's collector callback.
    start, at = M.W.address(b, 'MarioSourcePowerupCollision'), M.W.location(b, 'MarioSourcePowerupCollision')
    packet = bytes.fromhex('a9238d9c07a9408d010160')
    assert start == 0xaf71 and at == 28545 and image[at+23:at+34] == packet
    assert (M.W.address(b, 'StarInvincibleTimer'), M.W.address(b, 'AreaMusicQueue')) == (0x79c, 0x101)
    definitions = []
    for name, delta, code in (('starTimerStore', 25, bytes.fromhex('8d9c07')),
                              ('starMusicStore', 30, bytes.fromhex('8d0101'))):
        assert image[at+delta:at+delta+3] == code
        row = dict(pc=start+delta, offset=at+delta-16, hex=code.hex())
        definitions.append(f'C.hooks[{json.dumps(name)}]={M.lua(row)}')
    text = once(text, 'local frame,main,active,entered,menuReady,done=',
        '\n'.join(definitions)+'\nlocal frame,main,active,entered,menuReady,done=')
    text = once(text, 'local checkpoints={}',
        'local checkpoints={}\nlocal starWrites,starWriteOrder,armedStarTimer,armedStarMusic={},0,false,false')
    text = once(text, 'checkpoints=checkpoints,tier=tier,',
        'star_writes=starWrites,checkpoints=checkpoints,tier=tier,')
    text = once(text, "hook('GameLoop',function()main=main+1 end)",
        "hook('GameLoop',function()main=main+1 end)\n"+STAR_WRITES)
    text = once(text, "if emu.read(at,emu.memType.nesDebug)==0xc1 and not marks.head_origin then",
        "if emu.read(at,emu.memType.nesDebug)==(tier==3 and 0x57 or 0xc1) and not marks.head_origin then")
    text = once(text, "assert(emu.read(6,emu.memType.nesDebug)==0xc1,'Original Mushroom metatile retained')",
        "assert(emu.read(6,emu.memType.nesDebug)==(tier==3 and 0x57 or 0xc1),'Original authored item metatile retained')")
    text = once(text, "assert(emu.read(at,emu.memType.nesDebug)==0xc1,'Native handler received actual C1')",
        "assert(emu.read(at,emu.memType.nesDebug)==(tier==3 and 0x57 or 0xc1),'Native handler received original item material')")
    text = once(text, "finish(true,'Natural Giant Mushroom and Flower, full source growth and grounded continuation')", """
     tier,target=3,1616;marks={};birth=nil;collected=nil;growth={};growthEntries={}
     firstPostAge=nil;completion=nil;resumed={}
""")
    text = once(text, " if collected then\n  if r('GuestPowerupActive')~=0 then", STAR_OBSERVER+" if collected then\n  if r('GuestPowerupActive')~=0 then")
    text = once(text, "assert(active<1800,'Finite natural two-upgrade route')", "assert(active<2200,'Finite natural three-item route')")
    LuaRuntime().compile(text)
    return image, text, dict(**proof, actual_Downloads_SHA256=H(current),
        reconstructed_installed_image_equal=H(current)==H(image), ROM_writes=False)


LIFE_OBSERVER = r'''
 if tier==2 and collected then
  assert(r('PlayerStatus')==1 and r('PlayerSize')==0 and r('GuestPowerupActive')==0,
   'Hidden life preserves the naturally earned Mushroom')
  if not completion then
   if r('NumberofLives')==3 then completion=sample()end
  else
   assert(r('NumberofLives')==3 and r('GameEngineSubroutine')==8,'Actual hidden life credit retained')
   if r('Player_State')==0 and r('Player_Y_Position')==176 and r('Player_Y_HighPos')==1 then
    resumed[#resumed+1]=sample()
    if #resumed==25 then
     assert(x()>completion.x,'Movement after actual extra life reward')
     checkpoints[#checkpoints+1]={kind=3,marks=marks,birth=birth,collection=collected,
      credit=completion,resumed=resumed}
     finish(true,'Natural Giant Mushroom and hidden one-up with real plus-one and grounded continuation')
    end
   end
  end
  return
 end
'''

LIFE_CONTROL = r'''
local function chooseLife()
 if tier==1 or x()<980 and lifePhase=='approach'then return nil end
 if completion then return {right=true}end
 if lifePhase=='approach'then lifePhase='align';lifeSince=active end
 assert(active-lifeSince<260,'Finite genuine hidden-block alignment and jump')
 if lifePhase=='align'then
  local xx,y,v=x(),r('Player_Y_Position'),r('Player_X_Speed')
  if v>=128 then v=v-256 end
  if y~=176 or r('Player_State')~=0 then
   return v>0 and {left=true}or v<0 and {right=true}or{}
  end
  if math.abs(v)<=2 and xx>=1015 and xx<=1017 then
   lifePhase='jump';lifeLaunch=sample();lifeLaunch.vx=v;lifeJump=active
   return {a=true}
  end
  local predicted=xx+v*math.abs(v)/64
  if predicted>1017 then return {left=true}end
  if predicted<1015 then return {right=true}end
  return v>0 and {left=true}or v<0 and {right=true}or{}
 end
 return not birth and active-lifeJump<24 and {a=true}or{}
end
'''


def life_controller(text):
    text = once(text, 'local checkpoints={}', "local checkpoints={}\nlocal lifePhase,lifeSince,lifeLaunch,lifeJump='approach',nil,nil,nil")
    text = once(text, 'checkpoints=checkpoints,tier=tier,',
        'life_phase=lifePhase,life_launch=lifeLaunch,checkpoints=checkpoints,tier=tier,')
    text = once(text, 'tier,target=2,1248;', 'tier,target=2,1024;')
    text = once(text, 'a.id==46 and a.kind==tier-1 then', 'a.id==46 and a.kind==(tier==2 and 3 or 0) then')
    text = once(text, 'a.id==46 and a.kind==tier-1 and a.state>=6 then',
        'a.id==46 and a.kind==(tier==2 and 3 or 0) and a.state>=6 then')
    old = """ if marks.leaf and not marks.native_head then
  local at=marks.head_origin.cell
  assert(emu.read(at,emu.memType.nesDebug)==0xc1,'Native handler received actual C1')
  marks.native_head=sample()
 end"""
    new = """ if tier==2 then
  local at=emu.read(9,emu.memType.nesDebug)+256*emu.read(10,emu.memType.nesDebug)+emu.read(5,emu.memType.nesDebug)
  local tile=emu.read(at,emu.memType.nesDebug)
  if tile==0x5f or tile==0x60 then
   assert(lifeLaunch and x()>=1008 and x()<=1028 and r('Player_Y_Position')<160,
    'Real ordinary underside jump into the authored hidden block')
   assert(not marks.native_head,'Exactly one genuine hidden-block head effect')
   marks.native_head=sample();marks.native_head.cell=at;marks.native_head.tile=tile
  end
 elseif marks.leaf and not marks.native_head then
  local at=marks.head_origin.cell
  assert(emu.read(at,emu.memType.nesDebug)==0xc1,'Native handler received actual C1')
  marks.native_head=sample()
 end"""
    text = once(text, old, new)
    text = once(text, "assert(r('NumberofLives')==2 and r('WorldNumber')==0 and r('LevelNumber')==0\n  and r('InjuryTimer')==0,'Healthy original 1-1 work')",
        "assert((r('NumberofLives')==2 or tier==2 and collected and r('NumberofLives')==3)\n  and r('WorldNumber')==0 and r('LevelNumber')==0 and r('InjuryTimer')==0,'Healthy original 1-1 work')")
    text = once(text, " if collected then\n  if r('GuestPowerupActive')~=0 then", LIFE_OBSERVER+" if collected then\n  if r('GuestPowerupActive')~=0 then")
    text = once(text, "local function choose()\n if tier==1 then return {right=true}end",
        LIFE_CONTROL+"\nlocal function choose()\n local lifePad=chooseLife();if lifePad then return lifePad end\n if tier==1 then return {right=true}end")
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--item', choices=('star', 'life'), default='star')
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--compile-only', action='store_true')
    mode.add_argument('--run', action='store_true')
    a = ap.parse_args()
    a.output.mkdir(exist_ok=True)
    current = M.Probe.ROM.read_bytes()
    image, text, proof = controller(current, a.output, a.item)
    print('GIANT ITEM READY '+json.dumps(dict(**proof, item=a.item, Lua_SHA256=H(text.encode()),
        source_SHA256=H(Path(__file__).read_bytes()))), flush=True)
    if a.compile_only:
        assert not list(a.output.rglob('*'))
        return 0
    assert image == current and H(current) == Installed.CANDIDATE, 'Native mode requires installed exact6201'
    import run_stdout_mesen_1110 as Native
    from nightly_patch_guard_v1 import check
    target, script = M.SLOT/'candidate.nes', M.SLOT/'controller.lua'
    assert set(M.SLOT.iterdir()) == {target, script} and target.read_bytes() == current
    guard = check(M.Probe.ROM)
    assert guard['ROM_sha256'] == H(current) and not guard['matching_patch_files']
    Native.require_free_workspace(M.R, M.Probe.ROM, allow_interactive=True)
    previous = script.read_bytes()
    try:
        script.write_bytes(text.encode())
        result = Native.run(script, M.Probe.ROM, M.SLOT/'capture', H(current), 240)
        assert result['outputs_written'] == 0 and not result['images']
        print('GIANT ITEM RESULT '+json.dumps(dict(item=a.item, **result), separators=(',', ':')), flush=True)
        return int(not result['passed'])
    finally:
        script.write_bytes(previous)
        assert set(M.SLOT.iterdir()) == {target, script} and target.read_bytes() == current
        assert M.Probe.ROM.read_bytes() == current and check(M.Probe.ROM) == guard


if __name__ == '__main__':
    raise SystemExit(main())
