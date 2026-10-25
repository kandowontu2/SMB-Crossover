"""Freeze the observed facing-before-crouching controller correction."""
from pathlib import Path
import argparse
import hashlib
import json

ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
PREFIX = '''return function(c)
 if c.char==2 and c.r('CrossoverBehaviorVersion')==1 and c.grounded then
  local e
  for slot=0,5 do
   local flag,id,st=c.r('Enemy_Flag',slot),c.r('Enemy_ID',slot),c.r('Enemy_State',slot)
   local x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
   local y=c.r('Enemy_Y_Position',slot);local dx=x-c.x
   if flag>0 and flag<128 and id~=13 and(id<0x15 or id==0x2d or id==0x33)and st<0x20 and not(id==6 and st>=2)
      and math.abs(dx)<120 and math.abs(y-c.y)<42 and(not e or math.abs(dx)<math.abs(e.dx))then e={dx=dx}end
  end
  if e then
   if c.r('SmBall')~=0 then return{up=true}end
   local face=e.dx<0 and 2 or 1
   -- SamusMovement intentionally skips direction/facing while holding Down.
   -- The retained failure held Down+Left for317completed updates without
   -- turning, then died. Turn upright before pressing Down to crouch again.
   if c.r('PlayerFacingDir')~=face then return{left=face==2,right=face==1}end
   if c.r('SmCrouch')==0 then return{down=true}end
   return{down=true,b=c.r('FrameCounter')%12<2}
  elseif c.r('SmCrouch')~=0 then return{up=true}end
 end
 return normal(c)
end
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    source = ARCHIVE / '2026-10-24-roster-pe/policy-v1/policy.lua'
    assert sha(source) == 'f4e84baefbafa94986a3a56ff1209fd135549d24eb2ef58ba8749ccdfd4f61cc'
    policy = a.output / 'policy.lua'
    text = 'local normal=(function()\n' + source.read_text() + '\nend)()\n' + PREFIX
    assert 'emu.write(' not in text and 'dofile(' not in text
    policy.write_text(text)
    observed = ARCHIVE / '2026-10-24-roster-pf/samus-observe-v1'
    proof = dict(prepared=True, game_changes=False, memory_writes=False,
        policy_sha256=sha(policy), source_policy_sha256=sha(source),
        observer_proof_sha256=sha(observed / 'slot-proof.json'),
        completed_observer_sha256=sha(observed / 'completed.csv'),
        driver_sha256=sha(Path(__file__)),
        scope='Observed read-only test-controller repair. All317completed updates1800..2116held Down+Left, kept facing right, never fired while left Goombas approached. Turn before crouch. This does not alter Samus source behavior or certify a new route.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')


if __name__ == '__main__':
    main()
