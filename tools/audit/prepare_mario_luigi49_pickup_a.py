"""Prepare an ordinary controller pickup observation, without setup RAM writes."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
OUT = R / 'build/verification/root49s2-mario-luigi-pickups-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    cp = R / 'build/checkpoints/roster-audit-v49-menu-options-s2/manifest.json'
    manifest = json.loads(cp.read_text())
    assert all(sha(R / n) == h for n, h in manifest['source_hashes'].items())
    OUT.mkdir()
    text = r'''-- Ordinary power-on controller discovery, with read-only pickup observation.
local cfg=assert(ROSTER_CONFIG)
local root=assert(cfg.out:match('^(.*)/build/'))
local choose=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
local frame=0
local f=assert(io.open(cfg.out..'pickup-observation.csv','w'))
f:write('frame,x,y,power,size,engine,changeSize,timer,actors\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return '{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='boolean'then return tostring(v)else return tostring(v)end
end
local transitions={}
local spawnSeen=false
local oldPower=0
emu.addEventCallback(function()
 frame=frame+1
 if frame<540 then return end
 assert(r('SelectedCharacter')==cfg.character,'Actual ordinary selected character')
 local actors={}
 for i=0,5 do
  local flag,id=r('Enemy_Flag',i),r('Enemy_ID',i)
  if flag>0 then
   actors[#actors+1]=table.concat({i,flag,id,r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i)},':')
   if id==0x2e then spawnSeen=true end
  end
 end
 local p=r('PlayerStatus')
 if p~=oldPower then
  transitions[#transitions+1]={frame=frame,oldPower=oldPower,newPower=p,engine=r('GameEngineSubroutine'),spawnSeen=spawnSeen,
   x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position')}
  local png=assert(io.open(cfg.out..'pickup-power-'..p..'-f'..frame..'.png','wb'));png:write(emu.takeScreenshot());png:close()
  oldPower=p
 end
 f:write(table.concat({frame,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),p,r('PlayerSize'),r('GameEngineSubroutine'),r('PlayerChangeSizeFlag'),r('TimerControl'),table.concat(actors,';')},',')..'\n')
 if frame%60==0 then f:flush()end
end,emu.eventType.endFrame)
local stop=emu.stop
local closed=false
function emu.stop(code)
 if not closed then
  closed=true;f:close()
  local o=assert(io.open(cfg.out..'pickup-observation-summary.json','w'))
  o:write(json({character=cfg.character,frames=frame,controller_only=true,emulated_writes=false,spawnSeen=spawnSeen,transitions=transitions,full_route_proof=false})..'\n');o:close()
 end
 return stop(code)
end
return function(c)return choose(c)end
'''
    policy = OUT / 'policy.lua'
    policy.write_text(text)
    base = R / 'tools/playthroughs/mario_luigi_scrooge_policy.lua'
    nav = R / 'tools/playthroughs/mario_luigi_scrooge_nav.lua'
    (OUT / 'preparation.json').write_text(json.dumps(dict(
        status='PREPARED_ORDINARY_INPUT_READONLY_OBSERVER', script_sha256=sha(__file__),
        checkpoint_sha256=sha(cp), policy_sha256=sha(policy),
        base_policy_sha256=sha(base), navigation_sha256=sha(nav),
        emulated_writes=False, intended_scope='Ordinary first-mushroom pickup and growth; not a full route clear.',
        expected_short_endpoint='Unchanged harness frame limit after2200 frames; component evidence reviewed separately.'), indent=2) + '\n')
    print(str(policy), sha(policy))


if __name__ == '__main__':
    main()
