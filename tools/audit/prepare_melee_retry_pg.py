"""Retain the first melee failures; bind the exact active-spell ABI for retry."""
from pathlib import Path
import argparse
import hashlib
import json

ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
TAIL = '''return function(c)
 local b=normal(c)
 if c.world==0 and c.level==0 and c.char==5 and c.variant==1 then
  local function solid(x,y)
   local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
  end
  if c.grounded and c.y>=160 and not solid(c.x+32,232)then
   -- The retained original attempt launched30px before the first gap.
   -- Grant's authentic one-pixel air speed needs a takeoff at the edge.
   b.right=true;b.left=false;b.b=false
   b.a=not solid(c.x+6,232)and not c.lastA
  elseif not c.grounded and c.vy>=128 then b.a=true end
 end
 return b
end
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    parent = ARCHIVE / '2026-10-24-roster-pg/controls-v1'
    q = json.loads((parent / 'proof.json').read_text())
    original = parent / 'policy.lua'
    assert sha(original) == q['policy_sha256']
    text = original.read_text()
    before = "c.r('Z2ActiveSpells')"
    assert text.count(before) == 1
    # Actual fixed aliases: learned=InvAmmo+7, active=InvAmmo+9. The old
    # controller requested a non-exported label; the failure was in Lua.
    text = text.replace(before, "c.r('Z2LearnedSpells',2)")
    text = 'local normal=(function()\n' + text + '\nend)()\n' + TAIL
    assert 'emu.write(' not in text and 'dofile(' not in text
    policy = a.output / 'policy.lua'
    policy.write_text(text)
    proof = dict(prepared=True, game_changes=False, memory_writes=False,
        parent_policy_sha256=sha(original), policy_sha256=sha(policy),
        driver_sha256=sha(Path(__file__)),
        scope='The first two Zelda II retries physically acquired Jump, then their Lua observer failed on an unexported active-spell symbol. Use the source-defined learned+2alias. Grant retains native jump table and speed with later controller takeoff. All prior failed evidence remains unchanged. This preparation is not a route pass.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')


if __name__ == '__main__':
    main()
