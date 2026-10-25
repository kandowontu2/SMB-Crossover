"""Avoid firing melee attacks into empty space during route discovery."""
from pathlib import Path
import argparse
import hashlib
import json

SOURCE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-render-dispatch-ov/controls-ow-v1/policy.lua')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(SOURCE) == 'cd7656ee1264658ae059563c14e22383ed9cfb0bd479e4c0406ae203c0be0308'
    text = 'local normal=(function()\n' + SOURCE.read_text() + '''
end)()
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.char==10 or(c.char==5 and c.r('Cv3Variant')>0)then
  -- Their source attacks stop grounded walking. Do not spam B on empty floor.
  b.b=false
  local e=c.enemy()
  if e and e.id~=13 and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<46 then
   if c.grounded then
    if c.r('PlayerFacingDir')~=1 then return{right=true}end
    if e.dx<48 then return{down=true,b=c.poll%24<12}end
    return{}
   else
    b.b=e.dx<52 and math.abs(e.y-c.y)<30 and c.poll%24<12
   end
  end
 end
 return b
end
'''
    policy = a.output / 'policy.lua'
    policy.write_text(text)
    q = dict(prepared=True, game_changes=False, memory_writes=False, source_sha256=sha(SOURCE),
             policy_sha256=sha(policy), driver_sha256=sha(Path(__file__)),
             scope='Controller only. Native CV3/Ryu grounded attacks stop walking; continuous empty-floor B was wasting most updates and provoking the generic stuck-jump rule. Release B on empty floor, wait for low enemies and use native facing/crouch attacks within48px. Air attacks remain distance/height gated. No positions, physics, collision, health, terrain or equipment writes. All negative attempts remain retained and actual clear/replay gates are unchanged.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
