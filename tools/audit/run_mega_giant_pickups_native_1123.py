"""Exact private Giant Mushroom factory; root-only shared-slot native entry.

Default --compile-only writes no output.  The --run path is for Root's single
Mesen queue and restores the existing two shared files from memory.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from check_ff_stdout_controller_source_1110 import LuaRuntime
import probe_mega_giant_first_pickup_1123 as Probe
import propose_mega_giant_item_semantics_1123 as Fix

R, W = Probe.R, Probe.W
H = lambda raw: sha256(raw).hexdigest()
DK = 'c691588689f0779da6af467493c374d203e8d511d22e346a279642a3e6a8737a'
PRIVATE = '28db963105688758e5ddc331ae57655ff509def8575893516be78e67c2667144'
SLOT = R / 'build/smb2-flag-native-1113'


def three_way(current, out):
    """Actual byte disjointness, exact inverse views, bound dependencies below."""
    if H(current) == Probe.PIN:
        parent = current
    else:
        assert H(current) == DK
        import compose_dkjr_shinobi_1123 as Donkey
        # Only the already approved small typed compiler participates; no
        # archive extraction or producer/native entry is called here.
        parent = Donkey.recover_parent(current)
        assert H(parent) == Probe.PIN
    private = Fix.compose(parent)
    assert H(private) == PRIVATE
    changes = {i for i, (a, b) in enumerate(zip(parent, private, strict=True)) if a != b}
    carried = {i for i, (a, b) in enumerate(zip(parent, current, strict=True)) if a != b}
    assert not changes & carried
    merged = bytearray(current)
    for i in changes:
        assert merged[i] == parent[i]
        merged[i] = private[i]
    merged = bytes(merged)
    no_giant = merged[:Fix.AT] + Fix.OLD + merged[Fix.AT+len(Fix.OLD):]
    assert no_giant == current
    no_dk = bytearray(merged)
    for i in carried:
        no_dk[i] = parent[i]
    assert bytes(no_dk) == private and Fix.inverse(private) == parent
    b, labels, binding = Probe.binding(parent, out)
    protected = set()
    # All linked native spans used by this observer, plus the exact unchanged
    # Giant body/service, scene loader, geometry, art and metadata carriers.
    for row in binding['checked']:
        at = Probe.Giant.at(row['bank'], row['pc'])
        protected.update(range(at, at+row['size']))
    for name in ('IdleLoop', 'GameLoop', 'PowerUpObjHandler', 'HandlePowerUpCollision',
                 'MarioSourcePowerupCollision', 'MarioSourceBeginPowerup',
                 'MarioSourcePowerupUpdate', 'NativeRarePlayerHeadCollisionCore', 'SetupPowerUp'):
        at = W.location(b, name)
        size = max(32, int(b['syms'][name].get('size', '512'), 0))
        protected.update(range(at, at+size))
    protected.update(range(Probe.Giant.at(84, 0xbe00), Probe.Giant.at(84, 0xbf66)))
    for page in (180, 182, 212, 214):
        at = 16 + 128*8192 + page*1024
        protected.update(range(at, at+1024))
    assert not carried & protected, ('Changed live Giant source dependency', sorted(carried & protected)[:8])
    assert all(current[i] == parent[i] and merged[i] == private[i] for i in protected)
    return parent, merged, b, labels, dict(parent_SHA256=H(parent), current_SHA256=H(current),
        private_SHA256=PRIVATE, candidate_SHA256=H(merged), Giant_changed_bytes=len(changes),
        carried_changed_bytes=len(carried), actual_changes_disjoint=True,
        bound_live_dependency_bytes=len(protected), both_exact_inverse_views=True)


def controller(current, out):
    parent, image, b, labels, proof = three_way(current, out)
    ram_names = ('SelectedCharacter', 'MarioVariant', 'OperMode', 'OperMode_Task',
        'GameEngineSubroutine', 'NumberofLives', 'WorldNumber', 'LevelNumber', 'PlayerStatus',
        'PlayerSize', 'Player_State', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
        'Player_Y_HighPos', 'CheatStartLevel', 'CheatInvincible', 'GuestPowerupActive',
        'GuestPowerupAge', 'GuestPowerupTarget', 'GuestPowerupOld', 'TimerControl',
        'Player1ScoreDisplay', 'Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'PowerUpType',
        'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position', 'CrossoverMenuState',
        'CrossoverMenuIndex', 'CrossoverTitleDrawn', 'DisableScreenFlag', 'InjuryTimer')
    config = dict(rom=H(image), ram={n: W.address(b, n) for n in ram_names}, hooks={})
    def hook(name, bank, pc, n=5):
        at = Probe.Giant.at(bank, pc)
        config['hooks'][name] = dict(pc=pc, offset=at-16, hex=image[at:at+n].hex())
    for name in ('GameLoop', 'PowerUpObjHandler', 'HandlePowerUpCollision', 'MarioSourcePowerupUpdate'):
        at = W.location(b, name)
        hook(name, (at-16)//8192, W.address(b, name))
    at = W.location(b, 'IdleLoop')
    hook('returned', (at-16)//8192, W.address(b, 'IdleLoop')+12)
    hook('sweep', 90, labels['GiantSweepEffect'])
    hook('leaf', 90, 0xb174)
    hook('head', 126, W.address(b, 'PlayerHeadCollision'))
    cookie_at = Probe.Giant.at(84, 0xbeec)
    config['cookie'] = image[cookie_at:cookie_at+16].hex()
    assert config['cookie'].startswith('a7000902')
    config['proof'] = proof
    text = 'local C=' + lua(config) + '\n' + POLICY
    LuaRuntime().compile(text)
    return image, text, proof


def lua(value):
    if isinstance(value, dict):
        return '{' + ','.join('['+json.dumps(str(k))+']='+lua(v) for k, v in value.items()) + '}'
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


POLICY = r'''
local frame,main,active,entered,menuReady,done=0,0,0,false,false,false
local pad,marks,birth,collected,growth,completion,resumed={}, {},nil,nil,{},nil,{}
local growthEntries,firstPostAge={},nil
local previousActive=0
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function own()return r('SelectedCharacter')==0 and r('MarioVariant')==9 end
local function playing()return r('OperMode')==1 and r('OperMode_Task')==3 end
local function score()local n=0;for i=0,5 do n=10*n+r('Player1ScoreDisplay',i)end;return n end
local function sample()return{frame=frame,main=main,active=active,x=x(),y=r('Player_Y_Position'),
 engine=r('GameEngineSubroutine'),status=r('PlayerStatus'),size=r('PlayerSize'),
 lives=r('NumberofLives'),growth=r('GuestPowerupActive'),age=r('GuestPowerupAge'),
 native_state=r('Player_State'),score=score()}end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),
 state=r('Enemy_State',i),kind=r('PowerUpType',i),x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),
 y=r('Enemy_Y_Position',i)}end
local function json(v)
 if type(v)=='string'then return string.format('%q',v)end
 if type(v)~='table'then return tostring(v)end
 local q={};if #v>0 then for _,a in ipairs(v)do q[#q+1]=json(a)end;return'['..table.concat(q,',')..']'end
 for k,a in pairs(v)do q[#q+1]=string.format('%q',tostring(k))..':'..json(a)end
 table.sort(q);return'{'..table.concat(q,',')..'}'
end
local function finish(ok,reason)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=reason,ROM_SHA256=C.rom,controller_only=true,
  physical_frames=frame,terminal=sample(),marks=marks,birth=birth,collection=collected,
  growth=growth,growth_entries=growthEntries,first_post_age=firstPostAge,
  growth_completed=completion,resumed=resumed,proof=C.proof}))
 emu.stop(ok and 0 or 1)
end
local function safe(fn)return function(...)
 if done then return end;local ok,err=pcall(fn,...);if not ok then finish(false,tostring(err))end
end end
local function hook(name,fn)
 local q=assert(C.hooks[name]);local verified=false
 emu.addMemoryCallback(safe(function()
  local at=emu.convertAddress(q.pc)
  if not at or at.memType~=emu.memType.nesPrgRom or at.address~=q.offset then return end
  if not verified then
   for i=1,#q.hex,2 do assert(emu.read(q.pc+(i-1)//2,emu.memType.nesDebug)==tonumber(q.hex:sub(i,i+1),16),
    'Actual mapped code preimage '..name)end;verified=true
  end
  fn()
 end),emu.callbackType.exec,q.pc)
end
hook('GameLoop',function()main=main+1 end)
hook('sweep',function()
 if not entered then return end
 local at=emu.read(9,emu.memType.nesDebug)+256*emu.read(10,emu.memType.nesDebug)+emu.read(5,emu.memType.nesDebug)
 if emu.read(at,emu.memType.nesDebug)==0xc1 and not marks.head_origin then
  assert(x()>=300 and x()<=310 and r('Player_Y_Position')==176,'Real first block reach')
  marks.head_origin=sample();marks.head_origin.cell=at
 end
end)
hook('leaf',function()
 if marks.head_origin and not marks.leaf then
  assert(emu.read(6,emu.memType.nesDebug)==0xc1,'Original Mushroom metatile retained')
  assert(x()==336 and r('Player_Y_Position')==144,'Existing native Giant source-cell projection')
  marks.leaf=sample()
 end
end)
hook('head',function()
 if marks.leaf and not marks.native_head then
  local at=marks.head_origin.cell
  assert(emu.read(at,emu.memType.nesDebug)==0xc1,'Native handler received actual C1')
  marks.native_head=sample()
 end
end)
hook('PowerUpObjHandler',function()
 if not entered or birth then return end
 for i=0,5 do
  local a=actor(i)
  if a.flag~=0 and a.id==46 and a.kind==0 then
   assert(marks.native_head and a.x==336 and a.y<=144 and a.state>=1,'Actual block-born Mushroom')
   birth={hero=sample(),actor=a};return
  end
 end
end)
hook('HandlePowerUpCollision',function()
 if not entered then return end
 assert(not collected and birth,'Exactly one actual original Mushroom collection')
 for i=0,5 do local a=actor(i)
  if a.flag~=0 and a.id==46 and a.kind==0 and a.state>=6 then
   assert(r('PlayerStatus')==0 and r('NumberofLives')==2,'Healthy unpowered true collection')
   collected={hero=sample(),actor=a};return
  end
 end
 error('No mature actual Mushroom at collector')
end)
hook('MarioSourcePowerupUpdate',function()
 if not collected or r('GuestPowerupActive')==0 then return end
 local a=r('GuestPowerupAge')
 assert(a==#growthEntries and a<60 and r('GuestPowerupOld')==0 and r('GuestPowerupTarget')==1,
  'Each actual pre-increment original growth clock')
 growthEntries[#growthEntries+1]={age=a,main=main,status=r('PlayerStatus'),size=r('PlayerSize')}
end)
hook('returned',function()
 if not menuReady or not own()or not playing()then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==2
   and r('CheatStartLevel')==0 and r('CheatInvincible')==0 and r('PlayerStatus')==0,
   'Ordinary Easy 1-1 entry')
  for page=2,3 do for i=0,15 do
   assert(emu.read(page*8192+0x1fe0+i,emu.memType.nesWorkRam)==tonumber(C.cookie:sub(2*i+1,2*i+2),16),
    'Real Giant loaded scene cookie')
  end end
  entered=true;marks.first=sample()
 end
 assert(r('NumberofLives')==2 and r('WorldNumber')==0 and r('LevelNumber')==0
  and r('InjuryTimer')==0,'Healthy original 1-1 work')
 if r('GameEngineSubroutine')==8 then active=active+1 end
 if collected then
  if r('GuestPowerupActive')~=0 then
   local a=r('GuestPowerupAge')
   if firstPostAge==nil then
    assert(a==0 or a==1,'First completed return observes establish or first increment')
    firstPostAge=a
   end
   assert(a==firstPostAge+#growth and a<60 and r('TimerControl')==255,
    'Each completed original growth clock')
   growth[#growth+1]={age=a,status=r('PlayerStatus'),size=r('PlayerSize'),main=main}
  elseif not completion then
   assert(#growthEntries==60 and firstPostAge~=nil and #growth==60-firstPostAge
    and r('GuestPowerupAge')==60 and r('PlayerStatus')==1 and r('PlayerSize')==0
    and r('GameEngineSubroutine')==8 and score()>=collected.hero.score+1000,'Actual growth finish and +1000')
   completion=sample()
  else
   assert(r('PlayerStatus')==1 and r('PlayerSize')==0 and r('GameEngineSubroutine')==8
    and r('Player_State')==0 and r('Player_Y_Position')==176 and r('Player_Y_HighPos')==1,
    'Truly grounded retained upgrade continuation')
   resumed[#resumed+1]=sample()
   if #resumed==25 then
    assert(x()>completion.x and marks.native_head and birth and collected,'Movement after natural reward')
    finish(true,'Natural Giant Mushroom, sixty growth clocks and twenty-five grounded returns')
   end
  end
 end
 assert(active<600,'Finite first Mushroom approach')
end)
local function wait(n)for _=1,n do coroutine.yield()end end
local function press(n)pad={[n]=true};wait(4);pad={};wait(8)end
local function ready(fn)for _=1,900 do if fn()then return end;coroutine.yield()end;error('Menu readiness bound')end
local menu=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press('start');ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0)
 for _=1,9 do press('select')end
 assert(own(),'Real Mega Giant Mario menu selection')
 press('start');menuReady=true
end)
emu.addEventCallback(safe(function()
 emu.setInput(menuReady and {right=true}or pad,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(safe(function()
 frame=frame+1;assert(frame<5000,'Finite physical frame bound')
 if not menuReady then local ok,err=coroutine.resume(menu);assert(ok,err)end
end),emu.eventType.endFrame)
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--compile-only', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = ap.parse_args()
    args.output.mkdir(exist_ok=True)
    current = Probe.ROM.read_bytes()
    image, text, proof = controller(current, args.output)
    print('GIANT NATIVE READY ' + json.dumps(dict(**proof, Lua_SHA256=H(text.encode()),
        source_SHA256=H(Path(__file__).read_bytes()), no_gameplay_writes=True)), flush=True)
    if args.compile_only:
        assert not list(args.output.rglob('*'))
        return 0
    import run_stdout_mesen_1110 as Native
    from nightly_patch_guard_v1 import check
    target, script = SLOT/'candidate.nes', SLOT/'controller.lua'
    assert set(SLOT.iterdir()) == {target, script} and target.read_bytes() == current
    before = check(Probe.ROM)
    assert not before['matching_patch_files']
    Native.require_free_workspace(R, target, allow_interactive=True)
    previous = script.read_bytes()
    try:
        target.write_bytes(image)
        script.write_bytes(text.encode())
        result = Native.run(script, target, SLOT/'capture', H(image), 180)
        assert result['outputs_written'] == 0 and not result['images']
        print('GIANT NATIVE RESULT ' + json.dumps(result, separators=(',', ':')), flush=True)
        return int(not result['passed'])
    finally:
        script.write_bytes(previous)
        target.write_bytes(current)
        assert set(SLOT.iterdir()) == {target, script} and Probe.ROM.read_bytes() == current
        assert check(Probe.ROM) == before


if __name__ == '__main__':
    raise SystemExit(main())
