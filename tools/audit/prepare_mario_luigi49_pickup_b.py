"""Retain A's missed pickup and make a controller detour under the real block."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
OUT = R / 'build/verification/root49s2-mario-luigi-pickups-b'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    a = R / 'build/verification/root49s2-mario-luigi-pickups-a/policy.lua'
    assert sha(a) == 'e0430d681c3c1f436450e278c76161bf9e16bd83f15ebce899256cdc097e5a9a'
    negative = R / 'build/roster-through-2-2/root49s2-mario-pickup-a-0-v0-mmc3/pickup-observation-summary.json'
    n = json.loads(negative.read_text())
    assert not n['spawnSeen'] and not n['transitions']
    old = 'return function(c)return choose(c)end'
    text = a.read_text()
    assert text.count(old) == 1
    new = r'''local phase='travel'
local age=0
local function aim(c,target)
 local v=c.vx>=128 and c.vx-256 or c.vx
 if c.x>target+6 then return {left=true}
 elseif c.x<target-6 then return {right=true}
 elseif v>1 then return {left=true}
 elseif v< -1 then return {right=true}
 else return {}end
end
return function(c)
 if c.status>0 then return {}end
 if phase=='travel' then
  if c.x<404 then return choose(c)end
  phase='drop'
  local map=assert(io.open(cfg.out..'first-block-grid.csv','w'));map:write('x,y,tile\n')
  for y=112,208,16 do for x=304,464,16 do map:write(x..','..y..','..c.block(x,y)..'\n')end end;map:close()
 end
 if phase=='drop' then
  if c.grounded and c.y>=160 then phase='under' end
  return aim(c,420)
 elseif phase=='under' then
  local b=aim(c,336)
  if c.grounded and c.x>=328 and c.x<=343 and c.vx==0 then phase='bump';age=0;return {a=true}end
  return b
 elseif phase=='bump' then
  age=age+1
  local px
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then px=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)end end
  if px then phase='chase';age=0;return {}end
  assert(age<180,'Bounded real-block reveal; no spawned powerup')
  if c.grounded and age>45 then age=0 end
  return {a=age<24}
 else
  age=age+1
  local px
  for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then px=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)end end
  assert(px or c.status>0,'The real mushroom remains active until pickup')
  assert(age<600,'Bounded ordinary mushroom pursuit')
  -- Follow below the real row; it walks off its edge and falls to the player.
  -- This avoids manufacturing a jump through the solid row.
  return aim(c,math.min(430,math.max(328,px)))
 end
end'''
    text = text.replace(old, new)
    OUT.mkdir()
    p = OUT / 'policy.lua'
    p.write_text(text)
    (OUT / 'preparation.json').write_text(json.dumps(dict(
        status='PREPARED_CONTROLLER_REPAIR_ORDINARY_PICKUP', source_runtime_changed=False,
        parent_policy_sha256=sha(a), parent_missed_pickup_sha256=sha(negative),
        policy_sha256=sha(p), script_sha256=sha(__file__), emulated_writes=False,
        changes='Drop off the actual row, return below its first mushroom block, press A, follow its real fall.',
        scope='Ordinary pickup component; unchanged full harness retains explicit frame-limit endpoint.'), indent=2) + '\n')
    print(str(p), sha(p))


if __name__ == '__main__':
    main()
