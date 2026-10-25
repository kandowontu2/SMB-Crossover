"""Prepare explicit read-only melee controls and a sequential discovery driver."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
TAIL = '''local firstSeen=false
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 local e=c.enemy()
 if c.char==4 and c.variant==1 then
  -- Physically acquire Jump before the tall pipes. The old controller
  -- started its one-shot block input in mid-air and held A through landing,
  -- giving the original edge-triggered Zelda II jump no new press.
  if (c.r('Z2LearnedSpells')&2)==0 and c.x>=315 and c.x<480 then
   local item
   for slot=0,5 do
    if c.r('Enemy_Flag',slot)>0 and c.r('Enemy_ID',slot)==0x2e then
     item={x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot),
           y=c.r('Enemy_Y_Position',slot),state=c.r('Enemy_State',slot)}
    end
   end
   if item then
    firstSeen=true
    if item.state<128 then return{}end
    return{right=c.x<item.x-4,left=c.x>item.x+4}
   end
   if not firstSeen then
    b={right=c.x<331,left=c.x>334}
    if c.x>=330 and c.x<=335 then
     b.a=(c.grounded and not c.lastA)or(not c.grounded and c.vy>=128)
    end
    if e and e.id~=13 and math.abs(e.dx)<32 and math.abs(e.y-c.y)<30 and c.grounded then
     b.b=c.poll%24<8
    end
    return b
   end
  elseif (c.r('Z2LearnedSpells')&2)~=0 and(c.r('Z2ActiveSpells')&2)==0 then
   return{select=(c.lastMask&32)==0}
  end
  -- Holding A through the ascent is the native variable-jump control.
  if not c.grounded and c.vy>=128 then b.a=true end
 end
 if c.char==4 or(c.char==5 and c.variant==1)then
  -- Their original grounded attack states block walking or new jumps.
  -- Keep the genuine attack timer; release B on empty floor and on launch.
  local near=e and e.id~=13 and e.dx>0 and e.dx<64 and math.abs(e.y-c.y)<34
  b.b=near and not b.a and c.poll%24<8 or false
  if c.char==4 and c.variant==0 and c.grounded and c.r('RgAttack')~=0 then
   b.a=false;b.b=false
  end
 end
 return b
end
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    normal = ARCHIVE / '2026-10-24-roster-pe/policy-v1/policy.lua'
    assert sha(normal) == 'f4e84baefbafa94986a3a56ff1209fd135549d24eb2ef58ba8749ccdfd4f61cc'
    text = 'local normal=(function()\n' + normal.read_text() + '\nend)()\n' + TAIL
    assert 'emu.write(' not in text and 'dofile(' not in text
    policy = a.output / 'policy.lua'
    policy.write_text(text)
    base = ROOT / 'tools/audit/run_full_routes_of.py'
    source = base.read_text()
    before = 'ROOT = Path(__file__).resolve().parents[2]'
    assert source.count(before) == 1 and source.count('ThreadPoolExecutor(max_workers=2)') == 1
    source = source.replace(before, 'ROOT = Path(' + repr(ROOT.as_posix()) + ')')
    source = source.replace('ThreadPoolExecutor(max_workers=2)', 'ThreadPoolExecutor(max_workers=1)')
    driver = a.output / 'single-worker-runner.py'
    driver.write_text(source)
    proof = dict(prepared=True, game_changes=False, memory_writes=False,
        policy_sha256=sha(policy), policy_parent_sha256=sha(normal),
        sequential_driver_sha256=sha(driver), original_driver_sha256=sha(base),
        preparation_sha256=sha(Path(__file__)), native_workers=1,
        driver_changes=['Explicit existing workspace root', 'One native worker instead of two'],
        scope='Read-only melee discovery controller candidates. Original source edge-triggered jumping and attack locks are retained. Zelda II first Jump acquisition/casting is physical. No route pass, gameplay repair, equipment grant or visual claim is made by preparation.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')


if __name__ == '__main__':
    main()
