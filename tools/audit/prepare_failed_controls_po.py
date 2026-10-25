"""Freeze terrain-origin and stair-landing controller corrections; no game writes."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
TAIL = '''local stair='approach';local crossHold=0
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
local function threat(c)
 local e
 for slot=0,5 do
  local flag,id,st=c.r('Enemy_Flag',slot),c.r('Enemy_ID',slot),c.r('Enemy_State',slot)
  local x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
  local y=c.r('Enemy_Y_Position',slot);local dx=x-c.x
  if flag>0 and flag<128 and id~=13 and(id<0x15 or id==0x2d or id==0x33)and st<0x20 and not(id==6 and st>=2)
     and dx>0 and dx<120 and math.abs(y-c.y)<40 and(not e or dx<e.dx)then e={dx=dx,x=x,y=y,id=id}end
 end
 return e
end
return function(c)
 local b=c.char==0 and mario(c)or general(c)
 if c.world~=0 or c.level~=0 then return b end
 local e=threat(c)
 if c.char==0 then
  -- Small art retains the native32px terrain foot offset.
  -- Walk into the stair section rather than carrying full run momentum
  -- over its last narrow support. This changes inputs, not native physics.
  if c.x>=2280 and c.x<2512 then b.b=false end
  if c.grounded and not c.lastA and e and e.dx<64 and not solid(c,c.x+8,c.y-24)then b.a=true end
  if not c.grounded and c.vy>=128 then b.a=true end
  return b
 end
 if c.char~=14 then return b end
 -- Preserve the physical crate until there is a real throw target.
 -- A resting nearby crate is collected through the original B action.
 b.b=false
 local held=c.peek(A.CdHeld)
 if held==0 then
  for slot=0,5 do
   if c.peek(A.CdBoxKind+slot)~=0 and c.peek(A.CdBoxMode+slot)==0 then
    local x=c.peek(A.CdBoxX+slot)+256*c.peek(A.CdBoxPage+slot)
    local y=c.peek(A.CdBoxY+slot)
    if math.abs(x-c.x)<=20 and y-c.y>=-8 and y-c.y<=32 then b.b=c.poll%12<3 end
   end
  end
 elseif c.grounded and e and e.dx<80 then
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  b.b=c.poll%24<6
  if e.dx>32 then b.right=false;b.left=false;b.a=false end
 end
 if c.grounded and not c.lastA and e and e.dx<72 and not solid(c,c.x+8,c.y-24)then b.a=true end
 if not c.grounded and c.vy>=128 then b.a=true end
 if c.x>=2380 and c.x<2512 then
  if stair=='approach'and c.x>=2432 and c.y<=112 then stair='land'end
  if stair=='land'then
   b={right=c.x<2440,left=c.x>2442}
   if c.grounded and c.y<=112 and not c.lastA then
    stair='cross';crossHold=6;b={right=true,a=true}
   end
  elseif stair=='cross'then
   b.right=true;b.left=false;b.b=false
   b.a=crossHold>0 or(not c.grounded and c.vy>=128)
   if crossHold>0 then crossHold=crossHold-1 end
  end
 end
 return b
end
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old = ARCHIVE / '2026-10-24-matrix-om/policies-v3/policy.lua'
    general = ARCHIVE / '2026-10-24-roster-pe/policy-v1/policy.lua'
    assert sha(old) == '550622acf3b3f7ddc3fea34eefb6180e11697578292825ccc152bd936153ea06'
    assert sha(general) == 'f4e84baefbafa94986a3a56ff1209fd135549d24eb2ef58ba8749ccdfd4f61cc'
    # Decode the actual linked Small-foot table; keep the field alias values
    # bound to this ROM rather than relying on unexported Lua symbol names.
    debug = a.rom.with_suffix('.dbg')
    text = debug.read_text() if debug.exists() else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    symbols, segments = {}, {}
    for line in text.splitlines():
        if not line.startswith(('sym\t', 'seg\t')): continue
        q = dict(x.split('=', 1) for x in line[4:].split(',') if '=' in x)
        if line.startswith('seg\t'): segments[q['id']] = q
        elif 'val' in q: symbols[q['name'].strip('"')] = q
    def location(name):
        s = symbols[name]; g = segments[s['seg']]
        return int(g['ooffs'], 0) + int(s['val'], 0) - int(g['start'], 0)
    raw = a.rom.read_bytes(); table = location('BlockBuffer_Y_Adder')
    assert raw[table+14+1:table+14+3] == bytes((32, 32))
    aliases = {n: int(symbols[n]['val'], 0) for n in ('CdHeld', 'CdBoxKind', 'CdBoxMode', 'CdBoxX', 'CdBoxPage', 'CdBoxY')}
    mario = old.read_text()
    assert mario.count('local height=small and 16 or 32') == 1
    mario = mario.replace('local height=small and 16 or 32', 'local height=32')
    policy = a.output / 'policy.lua'
    source = 'local mario=(function()\n' + mario + '\nend)()\n'
    source += 'local general=(function()\n' + general.read_text() + '\nend)()\n'
    source += 'local A={' + ','.join(n + '=' + str(v) for n, v in aliases.items()) + '}\n' + TAIL
    assert 'emu.write(' not in source and 'dofile(' not in source
    policy.write_text(source)
    proof = dict(prepared=True, game_changes=False, memory_writes=False,
        ROM_sha256=sha(a.rom), policy_sha256=sha(policy), mario_parent_sha256=sha(old),
        general_parent_sha256=sha(general), actual_small_feet_Y_adders=[32, 32], linked_CD_aliases=aliases,
        driver_sha256=sha(Path(__file__)),
        scope='Controller-only corrections. Actual linked small-Mario feet retain32px; old Chip/Dale traces show launch from x2385/y144and missing the final stair near2444/y108. Retry lands on2440/y112before a new gap jump and preserves physical crates for real targets. No game state, physics, inventory, terrain or equipment is injected. This preparation is not a pass.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')


if __name__ == '__main__': main()
