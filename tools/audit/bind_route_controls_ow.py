"""Use real crouch attacks and jump over the flagpole base during discovery."""
from pathlib import Path
import argparse
import hashlib
import json

SOURCE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-matrix-om/failed-policies-v1/policy.lua')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(SOURCE) == '2f4d57be9fb1068cb6ec59e7dbc66270cc1c2df4fa9ec4b353702c9da30aa276'
    text = SOURCE.read_text()
    anchor = ' if useLedges then\n'
    assert text.count(anchor) == 1
    text = text.replace(anchor, " if c.char==0 then for _,ledge in ipairs(ledges)do ledge.top=112+(c.r('PlayerSize')~=0 and 16 or 0)end end\n" + anchor)
    text = 'local normal=(function()\n' + text + '''
end)()
local flagHold=0
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==17 and c.x>3115 and c.x<3184 then
  -- The ordinary solid pole base must be jumped; walking into it is no clear.
  if c.grounded and not c.lastA then flagHold=8 end
  b={right=true,b=true,a=flagHold>0 or(not c.grounded and c.vy>=128)}
  if flagHold>0 then flagHold=flagHold-1 end
 end
 if c.char==10 then
  local e=c.enemy()
  if c.grounded and e and e.id~=13 and e.dx>0 and e.dx<88 and math.abs(e.y-c.y)<44 then
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
   return{down=true,b=c.poll%20<10}
  end
 end
 return b
end
'''
    policy = a.output / 'policy.lua'
    policy.write_text(text)
    q = dict(prepared=True, game_changes=False, memory_writes=False, source_sha256=sha(SOURCE),
             policy_sha256=sha(policy), driver_sha256=sha(Path(__file__)),
             scope='Controller discovery only: recognize Mario small-body landing height; hold a real SMB3 jump over the flagpole base; use actual Ryu grounded crouch-sword input against low enemies. Prior held-edge controls also apply to CV3. No physics, terrain, equipment, position or invincibility writes. Every discovery must still independently replay and pass the unchanged native clear/graphics/scroll checks.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
