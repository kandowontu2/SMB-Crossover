"""Bind the existing route to deliberate native Simon whip combat in Hard."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    source=ROOT/'tools/playthroughs/full_roster_policy_og.lua'
    assert hashlib.sha256(source.read_bytes()).hexdigest()=='17d3a38d53fe09b930048f081938bf707028f765577207bce41777ea4f5edb7b'
    text='-- Controller inputs only: stop on support and use the actual whip.\nlocal base=(function()\n'+source.read_text()+'''\nend)()
return function(c)
 local b=base(c)
 if c.char~=5 or c.r('Cv3Variant')~=0 or c.r('CrossoverBehaviorVersion')~=1 or c.x<420 then return b end
 local e=c.enemy()
 if c.grounded and e and math.abs(e.dx)<60 and math.abs(e.y-c.y)<48 then
  local face=e.dx<0 and 2 or 1
  if c.r('PlayerFacingDir')~=face then return {left=face==2,right=face==1}end
  return {down=e.id==6,b=c.r('RgAttack')==0}
 end
 return b
end
'''
    out=a.output/'policy.lua';out.write_text(text)
    q=dict(prepared=True,game_changes=False,memory_writes=False,
        original_policy_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        policy_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
        adaptation='Hard Simon stops on actual ground before a nearby ordinary enemy, turns toward it and supplies native whip edges, crouching for a Goomba. All Easy inputs and other source navigation remain unchanged.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
