"""Release the source variable jump after clearing the measured48px coral."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'lowhop-preparation-t.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-floor-s-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=D/'prefix-mmc5-24199-t.csv';prefix.write_text('\n'.join(lines[:24200])+'\n')
    s=(D/'floor-policy-s.lua').read_text().replace('c.x==1398','c.x==1409')
    s=s.replace('local walked,walkAge,walkStill,lastWalkX=false,0,0,0',"local walked,walkAge,walkStill,lastWalkX=false,0,0,0\nlocal wallPhase,wallAge,released='jump',0,false")
    at=s.index(' if not walked then')
    extra=r''' if wallPhase~='done' then
  wallAge=wallAge+1;assert(wallAge<240,'Bounded source low coral hop')
  if c.y<=128 then released=true end
  local b={right=true,a=not released,b=c.poll%8<4}
  if released and c.grounded and c.x>=1442 then wallPhase='done';lastWalkX=c.x end
  walk:write(table.concat({c.frame,c.x,c.y,c.state,c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32),c.block(c.x+16,c.y+32),(b.right and 1 or 0)+(b.b and 64 or 0)+(b.a and 128 or 0)},',')..'\n');walk:flush()
  return b
 end
'''
    s=s[:at]+extra+s[at:];policy=D/'lowhop-policy-t.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    grid=R/'build/roster-through-2-2/root49-d-samus-m5-floor-s-2-v0-mmc5/actual-water-floor-grid-s.csv'
    out.write_text(json.dumps(dict(status='PREPARED_SOURCE_VARIABLE_LOW_CORAL_JUMP',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),grid_sha256=sha(grid),
      source_release='reference/crossover/decompiled/scripts/com/smbc/characters/Samus.as relJmpBtn enables frictionY; movement multiplies upward vy by pow(fy,dt).',
      diagnosis='S actual single16wide coral1424/Y160..208 blocks lowerfloor at1409. Fresh jump, releaseA after realY128 clears48px obstruction, then continue lowerfloor; do not hold the previous high water jump into upper fish.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared measured48px coral/source low jump T')
if __name__=='__main__':main()
